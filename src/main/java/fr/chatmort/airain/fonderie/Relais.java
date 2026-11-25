package fr.chatmort.airain.fonderie;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.simibubi.create.content.kinetics.base.GeneratingKineticBlockEntity;
import com.simibubi.create.content.kinetics.base.KineticBlock;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.content.kinetics.KineticNetwork;
import com.simibubi.create.foundation.block.IBE;
import com.simibubi.create.foundation.blockEntity.behaviour.BlockEntityBehaviour;
import com.simibubi.create.foundation.blockEntity.behaviour.ValueBoxTransform;
import com.simibubi.create.foundation.blockEntity.behaviour.scrollValue.ScrollValueBehaviour;

import fr.chatmort.airain.AirainMod;
import net.createmod.catnip.math.VecHelper;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * 1.69.3 : le relais cinétique d'airain. Un émetteur prend la rotation de son réseau ; chaque récepteur du même canal
 * la rend à la même vitesse, dans n'importe quelle dimension (les deux côtés chargés). Ce que consomment les machines
 * côté récepteur pèse sur le réseau de l'émetteur, plus 10 % de perte.
 */
public final class Relais {
	private Relais() {}

	public static final DirectionProperty FACING = BlockStateProperties.FACING;           // vers où regarde l'œil ; l'arbre entre par l'arrière
	public static final BooleanProperty RECEPTEUR = BooleanProperty.create("receiver");
	public static final BooleanProperty OUVERT = BooleanProperty.create("open");
	public static final float PERTE = 1.1f;

	public static final DeferredBlock<Bloc> BLOC = AirainMod.BLOCKS.register("kinetic_relay", () -> new Bloc(BlockBehaviour.Properties.of()
		.mapColor(MapColor.COLOR_BLACK).requiresCorrectToolForDrops().strength(5f, 1200f).sound(SoundType.NETHERITE_BLOCK).noOcclusion()
		.lightLevel(s -> s.getValue(OUVERT) ? 7 : 0)));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<BE>> BE_TYPE = AirainMod.BLOCK_ENTITIES.register("kinetic_relay",
		() -> BlockEntityType.Builder.of((p, s) -> new BE(Relais.BE_TYPE.get(), p, s), BLOC.get()).build(null));

	public static void charger() {
		AirainMod.ITEMS.register("kinetic_relay", () -> new BlockItem(BLOC.get(), new Item.Properties()));
	}

	// ------------------------------------------------------------------ registre des canaux (serveur), revérifié à chaque lecture
	private static final Map<Integer, GlobalPos> EMETTEURS = new HashMap<>();
	private static final Map<Integer, Set<GlobalPos>> RECEPTEURS = new HashMap<>();

	/** Le relais de ce mode et de ce canal à cette position, s'il y est encore et chargé. */
	private static BE relais(MinecraftServer srv, GlobalPos g, boolean recepteur, int canal) {
		ServerLevel l = srv.getLevel(g.dimension());
		if (l == null || !l.isLoaded(g.pos())) return null;
		return l.getBlockEntity(g.pos()) instanceof BE b && !b.isRemoved() && b.recepteur() == recepteur && b.canal() == canal ? b : null;
	}

	public static void arret(ServerStoppedEvent e) { EMETTEURS.clear(); RECEPTEURS.clear(); }

	// ------------------------------------------------------------------ le bloc
	public static class Bloc extends KineticBlock implements IBE<BE> {
		public Bloc(Properties p) {
			super(p);
			registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(RECEPTEUR, false).setValue(OUVERT, false));
		}
		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, RECEPTEUR, OUVERT); super.createBlockStateDefinition(b); }
		// posé contre un arbre : l'arrière se colle à la face cliquée, l'œil regarde le joueur
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getClickedFace()); }
		@Override public BlockState rotate(BlockState s, Rotation r) { return s.setValue(FACING, r.rotate(s.getValue(FACING))); }
		@Override public BlockState mirror(BlockState s, Mirror m) { return s.rotate(m.getRotation(s.getValue(FACING))); }
		@Override public Direction.Axis getRotationAxis(BlockState s) { return s.getValue(FACING).getAxis(); }
		@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return d == s.getValue(FACING).getOpposite(); }
		// changer de mode n'est pas « équivalent » pour Create : le réseau est défait puis refait
		@Override
		protected boolean areStatesKineticallyEquivalent(BlockState a, BlockState b) {
			return super.areStatesKineticallyEquivalent(a, b) && a.getValue(RECEPTEUR) == b.getValue(RECEPTEUR) && a.getValue(FACING) == b.getValue(FACING);
		}
		@Override public Class<BE> getBlockEntityClass() { return BE.class; }
		@Override public BlockEntityType<? extends BE> getBlockEntityType() { return BE_TYPE.get(); }

		// clic droit à main vide : émetteur <-> récepteur
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (l.isClientSide) return InteractionResult.SUCCESS;
			boolean rec = !s.getValue(RECEPTEUR);
			KineticBlockEntity.switchToBlockState(l, p, s.setValue(RECEPTEUR, rec).setValue(OUVERT, false));
			if (l.getBlockEntity(p) instanceof BE b) { b.vitesse = 0; b.capacite = 0; b.impact = 0; b.attente = 0; }
			l.playSound(null, p, rec ? SoundEvents.ENDER_EYE_DEATH : SoundEvents.END_PORTAL_FRAME_FILL, SoundSource.BLOCKS, 0.8f, 1.2f);
			j.displayClientMessage(Component.translatable(rec ? "airain.relais.recepteur" : "airain.relais.emetteur",
				l.getBlockEntity(p) instanceof BE b ? b.canal() : 1).withStyle(ChatFormatting.LIGHT_PURPLE), true);
			return InteractionResult.SUCCESS;
		}
	}

	// ------------------------------------------------------------------ l'entité
	public static class BE extends GeneratingKineticBlockEntity {
		ScrollValueBehaviour canalReglage;
		float vitesse, capacite, impact;     // récepteur : vitesse et capacité rendues ; émetteur : charge par tr/min
		int attente, recepteurs;
		boolean doublon;

		public BE(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }

		public boolean recepteur() { return getBlockState().getValue(RECEPTEUR); }
		public int canal() { return canalReglage == null ? 1 : canalReglage.getValue(); }

		@Override
		public void addBehaviours(List<BlockEntityBehaviour> behaviours) {
			super.addBehaviours(behaviours);
			// canal réglé comme sur les machines de Create, sur les quatre côtés
			canalReglage = new ScrollValueBehaviour(Component.translatable("airain.relais.canal"), this, new Plaque());
			canalReglage.between(1, 99);
			canalReglage.value = 1;
			canalReglage.withCallback(i -> { attente = 0; });
			behaviours.add(canalReglage);
		}

		@Override
		public void initialize() {
			super.initialize();
			if (recepteur()) updateGeneratedRotation();
		}

		@Override public float getGeneratedSpeed() { return recepteur() ? vitesse : 0; }
		@Override public float calculateAddedStressCapacity() { float c = recepteur() ? capacite : 0; lastCapacityProvided = c; return c; }
		@Override public float calculateStressApplied() { float i = recepteur() ? 0 : impact; lastStressApplied = i; return i; }

		@Override
		public void tick() {
			super.tick();
			if (level == null || level.isClientSide || level.getServer() == null) return;
			if (--attente > 0) return;
			attente = 10;
			GlobalPos ici = GlobalPos.of(level.dimension(), worldPosition);
			if (recepteur()) recevoir(level.getServer(), ici); else emettre(level.getServer(), ici);
			// l'œil s'ouvre quand le relais travaille
			boolean ouvert = getSpeed() != 0 && !isOverStressed() && !doublon;
			BlockState s = getBlockState();
			if (s.getValue(OUVERT) != ouvert) level.setBlock(worldPosition, s.setValue(OUVERT, ouvert), Block.UPDATE_CLIENTS);
		}

		private void emettre(MinecraftServer srv, GlobalPos ici) {
			int c = canal();
			RECEPTEURS.values().forEach(r -> r.remove(ici));
			GlobalPos chef = EMETTEURS.get(c);
			if (chef != null && !chef.equals(ici) && relais(srv, chef, false, c) != null) doublon = true;
			else { doublon = false; EMETTEURS.put(c, ici); }
			// ce que tirent les machines des récepteurs, plus la perte
			float demande = 0; int nb = 0;
			if (!doublon) {
				Set<GlobalPos> rs = RECEPTEURS.getOrDefault(c, Set.of());
				for (GlobalPos g : Set.copyOf(rs)) {
					BE r = relais(srv, g, true, c);
					if (r == null) { rs.remove(g); continue; }
					nb++;
					// 1.69.4 : un réseau récepteur surchargé est arrêté par Create, il ne tire plus rien sur l'émetteur
					if (!r.hasNetwork() || r.getSpeed() == 0 || r.isOverStressed()) continue;
					KineticNetwork n = r.getOrCreateNetwork();
					float st = n.calculateStress(), cap = n.calculateCapacity();
					float part = cap > 0 ? Math.min(1f, r.capacite * Math.abs(r.getSpeed()) / cap) : 1f;   // part de ce récepteur dans son réseau
					demande += st * part;
				}
			}
			recepteurs = nb;
			float v = Math.abs(getSpeed());
			float nouvel = v > 0 ? demande * PERTE / v : 0;
			if (Math.abs(nouvel - impact) > 0.001f) { impact = nouvel; if (hasNetwork()) getOrCreateNetwork().updateStressFor(this, impact); }
			sendData();
		}

		private void recevoir(MinecraftServer srv, GlobalPos ici) {
			int c = canal();
			if (ici.equals(EMETTEURS.get(c))) EMETTEURS.remove(c);
			RECEPTEURS.values().forEach(r -> r.remove(ici));
			RECEPTEURS.computeIfAbsent(c, k -> new HashSet<>()).add(ici);
			GlobalPos g = EMETTEURS.get(c);
			BE e = g == null ? null : relais(srv, g, false, c);
			float v = 0, cap = 0;
			doublon = false;
			if (e != null && e.hasNetwork() && e.getSpeed() != 0 && !e.isOverStressed()) {
				// pas de boucle : un récepteur qui ferait tourner son propre émetteur s'arrête
				boolean boucle = e.getLevel() == level && hasNetwork() && e.network.equals(network) && !hasSource();
				if (!boucle) {
					v = e.getSpeed();
					KineticNetwork n = e.getOrCreateNetwork();
					float propre = e.impact * Math.abs(e.getSpeed());
					float libre = n.calculateCapacity() - (n.calculateStress() - propre);
					int nb = Math.max(1, RECEPTEURS.getOrDefault(c, Set.of()).size());
					cap = Math.max(0f, libre / PERTE / nb) / Math.abs(v);
				}
			}
			recepteurs = e != null ? 1 : 0;
			boolean change = v != vitesse || Math.abs(cap - capacite) > Math.max(0.05f, capacite * 0.02f);
			vitesse = v; capacite = cap;
			if (change) updateGeneratedRotation();
		}

		@Override
		protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			t.putFloat("vitesse", vitesse); t.putFloat("capacite", capacite); t.putFloat("impact", impact);
			t.putInt("recepteurs", recepteurs); t.putBoolean("doublon", doublon);
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			vitesse = t.getFloat("vitesse"); capacite = t.getFloat("capacite"); impact = t.getFloat("impact");
			recepteurs = t.getInt("recepteurs"); doublon = t.getBoolean("doublon");
		}

		// lunettes de l'ingénieur : mode, canal, état de la liaison
		@Override
		public boolean addToGoggleTooltip(List<Component> tt, boolean accroupi) {
			tt.add(Component.literal("    ").append(Component.translatable("block.airain.kinetic_relay")).withStyle(ChatFormatting.GOLD));
			tt.add(Component.literal("    ").append(Component.translatable(recepteur() ? "airain.relais.recepteur" : "airain.relais.emetteur", canal())).withStyle(ChatFormatting.LIGHT_PURPLE));
			String etat = doublon ? "airain.relais.doublon" : recepteur() ? (recepteurs > 0 ? "airain.relais.relie" : "airain.relais.sans_emetteur")
				: (recepteurs > 0 ? "airain.relais.vers" : "airain.relais.sans_recepteur");
			tt.add(Component.literal("    ").append(Component.translatable(etat, recepteurs)).withStyle(doublon || recepteurs == 0 ? ChatFormatting.RED : ChatFormatting.GRAY));
			super.addToGoggleTooltip(tt, accroupi);
			return true;
		}
	}

	/** Plaque du canal : au milieu des quatre côtés, juste devant le cœur (en retrait d'un texel). */
	static class Plaque extends ValueBoxTransform.Sided {
		@Override protected Vec3 getSouthLocation() { return VecHelper.voxelSpace(8, 8, 15.5); }
		@Override protected boolean isSideActive(BlockState s, Direction d) { return d.getAxis() != s.getValue(FACING).getAxis(); }
	}
}
