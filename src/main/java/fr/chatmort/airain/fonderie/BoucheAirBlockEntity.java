package fr.chatmort.airain.fonderie;

import com.simibubi.create.api.equipment.goggles.IHaveGoggleInformation;
import com.simibubi.create.content.kinetics.fan.AirCurrent;
import com.simibubi.create.content.kinetics.fan.EncasedFanBlock;
import com.simibubi.create.content.kinetics.fan.EncasedFanBlockEntity;
import com.simibubi.create.content.kinetics.fan.IAirCurrentSource;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * La bouche d'air : elle remonte le réseau de conduits jusqu'au ventilateur qui l'alimente et recopie sa vitesse.
 * Comme force et portée d'un courant de Create ne dépendent que de la vitesse, le courant sorti est identique à
 * celui qui entre, quelle que soit la longueur du conduit. Soufflage → la bouche souffle ; aspiration → elle aspire.
 */
public class BoucheAirBlockEntity extends BlockEntity implements IAirCurrentSource, IHaveGoggleInformation {
	private final AirCurrent courant = new AirCurrent(this);
	/** Vitesse recopiée du ventilateur : positive en soufflage, négative en aspiration, 0 sans ventilateur. */
	private float vitesse;
	private boolean tropLong;
	private int attente, recherche;
	private float derniere = -1;

	public BoucheAirBlockEntity(BlockPos p, BlockState s) { super(ConduitAir.BE.get(), p, s); }

	private Direction sens() { return getBlockState().getValue(ConduitAir.FACING); }

	// ------------------------------------------------------------------ le réseau
	/** Parcourt les conduits depuis le dos de la bouche ; garde le ventilateur le plus rapide qui souffle dedans. */
	private float chercher() {
		tropLong = false;
		BlockPos depart = worldPosition.relative(sens().getOpposite());
		if (!ConduitAir.porteConduit(level.getBlockState(depart), sens())) return 0;
		ArrayDeque<BlockPos> file = new ArrayDeque<>(); Set<BlockPos> vus = new HashSet<>();
		file.add(depart); vus.add(depart);
		float meilleur = 0;
		while (!file.isEmpty()) {
			BlockPos p = file.poll();
			BlockState ici = level.getBlockState(p);
			for (Direction d : Direction.values()) {
				// un conduit logé dans un plancher technique ne s'ouvre que dans son axe
				if (!(ici.getBlock() instanceof ConduitAir.Conduit) && !ConduitAir.porteConduit(ici, d)) continue;
				BlockPos n = p.relative(d);
				if (vus.contains(n) || !level.isLoaded(n)) continue;
				BlockState s = level.getBlockState(n);
				if (ConduitAir.porteConduit(s, d)) {
					vus.add(n);
					if (vus.size() > ConduitAir.MAX_CONDUITS) { tropLong = true; return 0; }
					file.add(n);
				} else if (s.getBlock() instanceof EncasedFanBlock && s.getValue(BlockStateProperties.FACING) == d.getOpposite()
					&& level.getBlockEntity(n) instanceof EncasedFanBlockEntity fan && fan.getSpeed() != 0) {
					float v = Math.abs(fan.getSpeed());
					if (fan.getAirFlowDirection() != s.getValue(BlockStateProperties.FACING)) v = -v;      // le ventilateur aspire
					if (Math.abs(v) > Math.abs(meilleur)) meilleur = v;
				}
			}
		}
		return meilleur;
	}

	// ------------------------------------------------------------------ tic (serveur et client, comme le ventilateur)
	public void tick() {
		if (level == null) return;
		if (!level.isClientSide && --attente <= 0) {
			attente = 10;
			float v = chercher();
			boolean change = v != vitesse;
			vitesse = v;
			courant.rebuild();
			if (change || courant.maxDistance != derniere) {
				derniere = courant.maxDistance;
				setChanged();
				level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
			}
		}
		if (vitesse == 0) return;
		if (--recherche <= 0) { recherche = 5; courant.findEntities(); }
		courant.tick();
	}

	// ------------------------------------------------------------------ source de courant pour Create
	@Override public AirCurrent getAirCurrent() { return courant; }
	@Nullable @Override public Level getAirCurrentWorld() { return level; }
	@Override public BlockPos getAirCurrentPos() { return worldPosition; }
	@Override public float getSpeed() { return vitesse; }
	@Override public Direction getAirflowOriginSide() { return sens(); }
	@Nullable @Override public Direction getAirFlowDirection() { return vitesse == 0 ? null : vitesse > 0 ? sens() : sens().getOpposite(); }
	@Override public boolean isSourceRemoved() { return isRemoved(); }

	// ------------------------------------------------------------------ lunettes
	@Override
	public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
		t.add(Component.literal("    ").append(Component.translatable("block.airain.airain_air_vent")).withStyle(ChatFormatting.GOLD));
		if (tropLong) { t.add(Component.literal("    ").append(Component.translatable("airain.conduit.trop_long", ConduitAir.MAX_CONDUITS)).withStyle(ChatFormatting.RED)); return true; }
		if (vitesse == 0) { t.add(Component.literal("    ").append(Component.translatable("airain.conduit.muet")).withStyle(ChatFormatting.GRAY)); return true; }
		t.add(Component.literal("    ").append(Component.translatable(vitesse > 0 ? "airain.conduit.souffle" : "airain.conduit.aspire", Math.round(Math.abs(vitesse)))).withStyle(ChatFormatting.GRAY));
		t.add(Component.literal("    ").append(Component.translatable("airain.conduit.portee", String.format("%.1f", courant.maxDistance))).withStyle(ChatFormatting.DARK_GRAY));
		return true;
	}

	// ------------------------------------------------------------------ sauvegarde et synchronisation
	@Override
	protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) {
		super.saveAdditional(t, r);
		t.putFloat("vitesse", vitesse); t.putBoolean("trop_long", tropLong);
	}
	@Override
	protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) {
		super.loadAdditional(t, r);
		vitesse = t.getFloat("vitesse"); tropLong = t.getBoolean("trop_long");
		if (level != null && level.isClientSide) courant.rebuild();
	}
	@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
	@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
	@Override
	public void onDataPacket(Connection c, ClientboundBlockEntityDataPacket pk, HolderLookup.Provider r) {
		super.onDataPacket(c, pk, r);
		courant.rebuild();
	}
}
