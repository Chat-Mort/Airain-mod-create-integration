package fr.chatmort.airain.trophee;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import org.joml.Vector3f;

/**
 * Piédestal de l'Empire : le trophée exposé, l'apparence du socle, la plaque gravée (nom et jour de la victoire).
 * Côté client, des particules rappellent l'effet du trophée.
 */
public class SocleBlockEntity extends BlockEntity {
	private ItemStack trophee = ItemStack.EMPTY;
	private SocleApparence apparence = SocleApparence.DEFAUT;
	private String plaque = "";
	private int jour;

	public SocleBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.SOCLE_BE.get(), pos, state);
	}

	public ItemStack trophee() { return trophee; }
	public SocleApparence apparence() { return apparence; }
	public String plaque() { return plaque; }
	public int jour() { return jour; }

	/** Pose d'un trophée : la plaque se grave toute seule (nom de l'objet et jour de jeu). */
	public void exposer(ItemStack pile) {
		trophee = pile.copyWithCount(1);
		if (level != null) {
			plaque = trophee.getHoverName().getString();
			if (plaque.length() > 32) plaque = plaque.substring(0, 32);
			jour = (int) (level.getDayTime() / 24000L) + 1;
		}
		enregistrer();
		maj();
	}

	public ItemStack reprendre() {
		ItemStack p = trophee;
		trophee = ItemStack.EMPTY;
		if (level instanceof ServerLevel sl)
			TropheeRegistre.de(sl.getServer()).retirer(level, worldPosition);
		maj();
		return p;
	}

	public void configurer(SocleApparence a, String texte) {
		apparence = a;
		plaque = texte.length() > 32 ? texte.substring(0, 32) : texte;
		if (level != null && !level.isClientSide) {
			BlockState s = getBlockState();
			if (s.getValue(SocleBlock.LUMIERE) != a.eclaire()) level.setBlock(worldPosition, s.setValue(SocleBlock.LUMIERE, a.eclaire()), 3);
		}
		enregistrer();
		maj();
	}

	private void enregistrer() {
		if (level instanceof ServerLevel sl && !trophee.isEmpty())
			TropheeRegistre.de(sl.getServer()).poser(level, worldPosition, BuiltInRegistries.ITEM.getKey(trophee.getItem()), plaque, jour);
	}

	@Override
	public void onLoad() {
		super.onLoad();
		enregistrer();   // au cas où le registre aurait été perdu
	}

	/** Signal du comparateur : 0 sans trophée, sinon d'autant plus fort que le trophée donne d'effets. */
	public int signal() {
		if (trophee.isEmpty()) return 0;
		return Math.min(15, 7 + 4 * Trophees.effetsDe(trophee).size());
	}

	// ------------------------------------------------------------------ particules (client)
	public void tickClient() {
		if (level == null || trophee.isEmpty() || !apparence.avecParticules()) return;
		RandomSource r = level.random;
		if (r.nextInt(8) != 0) return;
		double y = worldPosition.getY() + (apparence.haute() ? 2.05 : 1.05) + r.nextDouble() * 0.5;
		for (Trophees.Effet e : Trophees.effetsDe(trophee)) {
			ParticleOptions p = switch (e) {
				case FEU -> ParticleTypes.SMALL_FLAME;
				case REGENERATION -> r.nextInt(4) == 0 ? ParticleTypes.HEART : null;
				case VISION -> ParticleTypes.ELECTRIC_SPARK;
				case RESISTANCE -> new DustParticleOptions(new Vector3f(0.72f, 0.74f, 0.78f), 0.8f);
				case HATE -> new DustParticleOptions(new Vector3f(1f, 0.82f, 0.3f), 0.7f);
				case FORCE -> new DustParticleOptions(new Vector3f(0.85f, 0.15f, 0.12f), 0.8f);
				case CHUTE -> ParticleTypes.WHITE_ASH;
			};
			if (p == null) continue;
			double a = r.nextDouble() * Math.PI * 2, d = 0.25 + r.nextDouble() * 0.15;
			level.addParticle(p, worldPosition.getX() + 0.5 + Math.cos(a) * d, y, worldPosition.getZ() + 0.5 + Math.sin(a) * d,
				0, e == Trophees.Effet.CHUTE ? -0.01 : 0.015, 0);
		}
	}

	@SuppressWarnings("unchecked")
	public static <T extends BlockEntity> BlockEntityTicker<T> ticker(Level l, BlockEntityType<T> type) {
		return l.isClientSide && type == AirainMod.SOCLE_BE.get() ? (lv, p, st, be) -> ((SocleBlockEntity) be).tickClient() : null;
	}

	private void maj() {
		setChanged();
		if (level != null) {
			level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
			level.updateNeighbourForOutputSignal(worldPosition, getBlockState().getBlock());
		}
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registres) {
		super.saveAdditional(tag, registres);
		if (!trophee.isEmpty()) tag.put("trophee", trophee.save(registres));
		tag.putInt("apparence", apparence.pack()); tag.putString("plaque", plaque); tag.putInt("jour", jour);
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registres) {
		super.loadAdditional(tag, registres);
		trophee = tag.contains("trophee") ? ItemStack.parseOptional(registres, tag.getCompound("trophee")) : ItemStack.EMPTY;
		apparence = SocleApparence.unpack(tag.getInt("apparence"));
		plaque = tag.getString("plaque"); jour = tag.getInt("jour");
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider registres) {
		CompoundTag t = saveWithoutMetadata(registres);
		t.putBoolean("sync", true);   // un paquet vide est ignoré par le client : l'objet retiré resterait affiché
		return t;
	}

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() {
		return ClientboundBlockEntityDataPacket.create(this);
	}
}
