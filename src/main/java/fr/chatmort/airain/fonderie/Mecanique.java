package fr.chatmort.airain.fonderie;

import com.simibubi.create.api.equipment.goggles.IHaveGoggleInformation;
import com.simibubi.create.content.kinetics.KineticNetwork;
import com.simibubi.create.content.kinetics.base.GeneratingKineticBlockEntity;
import com.simibubi.create.content.kinetics.base.IRotate;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.content.kinetics.motor.CreativeMotorBlockEntity;
import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.atelier.BlocPatine;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

/**
 * La mécanique impériale : deux pièces qui s'emboîtent dans Create, faites (presque) entièrement à la fonderie.
 *  - L'allégeur impérial se pose dans une ligne d'arbres ; son volant d'inertie retire 25 % de la charge de tout le réseau
 *    (un seul allégeur compte par réseau).
 *  - Le surcompresseur impérial se pose contre un générateur (roue à eau, moulin, moteur à vapeur…) : +50 % de capacité
 *    de stress pour ce générateur (un seul compte par générateur). Ni l'un ni l'autre ne perd en efficacité en se patinant.
 */
public final class Mecanique {
	private Mecanique() {}

	public static final float ALLEGEMENT = 0.25f, SURCOMPRESSION = 1.5f;

	// ====================================================================== l'allégeur (bloc)
	public static class Allegeur extends BlocPatine implements IRotate, EntityBlock {
		private static final Map<Direction.Axis, VoxelShape> FORMES = new java.util.EnumMap<>(Direction.Axis.class);
		static {
			FORMES.put(Direction.Axis.Z, Shapes.or(Block.box(0, 0, 0, 16, 16, 3), Block.box(0, 0, 13, 16, 16, 16), Block.box(1, 1, 3, 15, 15, 13)));
			FORMES.put(Direction.Axis.X, Shapes.or(Block.box(0, 0, 0, 3, 16, 16), Block.box(13, 0, 0, 16, 16, 16), Block.box(3, 1, 1, 13, 15, 15)));
			FORMES.put(Direction.Axis.Y, Shapes.or(Block.box(0, 0, 0, 16, 3, 16), Block.box(0, 13, 0, 16, 16, 16), Block.box(1, 3, 1, 15, 13, 15)));
		}
		public Allegeur(WeatherState etat, Properties p) { super(etat, p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.AXIS, Direction.Axis.Z)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.AXIS); }
		// l'axe suit l'arbre voisin, sinon la face visée
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction.Axis a = c.getClickedFace().getAxis();
			for (Direction d : Direction.values()) {
				BlockState n = c.getLevel().getBlockState(c.getClickedPos().relative(d));
				if (n.getBlock() instanceof IRotate r && r.hasShaftTowards(c.getLevel(), c.getClickedPos().relative(d), n, d.getOpposite())) { a = d.getAxis(); break; }
			}
			return defaultBlockState().setValue(BlockStateProperties.AXIS, a);
		}
		@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return d.getAxis() == s.getValue(BlockStateProperties.AXIS); }
		@Override public Direction.Axis getRotationAxis(BlockState s) { return s.getValue(BlockStateProperties.AXIS); }
		@Override
		protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
			super.onPlace(s, l, p, ancien, deplace);
			if (l.getBlockEntity(p) instanceof KineticBlockEntity k) { k.preventSpeedUpdate = 0; if (ancien.getBlock() == s.getBlock() && ancien.getValue(BlockStateProperties.AXIS) == s.getValue(BlockStateProperties.AXIS)) k.preventSpeedUpdate = 2; }
		}
		@Override
		protected void updateIndirectNeighbourShapes(BlockState s, LevelAccessor l, BlockPos p, int flags, int count) {
			if (l.isClientSide() || !(l.getBlockEntity(p) instanceof KineticBlockEntity k) || k.preventSpeedUpdate > 0) return;
			k.warnOfMovement(); k.clearKineticInformation(); k.updateSpeed = true;
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(BlockStateProperties.AXIS)); }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new AllegeurBlockEntity(ALLEGEUR_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return t == ALLEGEUR_BE.get() ? (lv, p, st, be) -> ((AllegeurBlockEntity) be).tick() : null;
		}
	}

	/** L'allégeur : une charge négative, recalculée sur ce que pèse le reste du réseau. */
	public static class AllegeurBlockEntity extends KineticBlockEntity {
		private float impact;            // charge propre (par tr/min), négative quand il travaille
		public float allege;             // stress retiré (su), affiché aux lunettes
		public boolean actif, double_;   // double_ : un autre allégeur règle déjà ce réseau
		private int attente;
		public AllegeurBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }

		@Override public float calculateStressApplied() { lastStressApplied = impact; return impact; }

		@Override
		public void tick() {
			super.tick();
			if (level == null) return;
			if (level.isClientSide) { if (actif && getSpeed() != 0) etincelles(); return; }
			if (--attente > 0) return;
			attente = 10;
			float nouvel = 0, retire = 0; boolean dbl = false;
			float v = Math.abs(getSpeed());
			if (hasNetwork() && v > 0) {
				KineticNetwork n = getOrCreateNetwork();
				float autres = 0; long chef = worldPosition.asLong();
				for (Entry<KineticBlockEntity, Float> e : new ArrayList<>(n.members.entrySet())) {
					KineticBlockEntity k = e.getKey();
					if (k instanceof AllegeurBlockEntity) { if (k != this && k.getBlockPos().asLong() < chef) dbl = true; continue; }
					if (e.getValue() > 0) autres += e.getValue() * Math.abs(k.getTheoreticalSpeed());
				}
				if (!dbl) { retire = autres * ALLEGEMENT; nouvel = -retire / v; }
			}
			boolean act = retire > 0;
			if (nouvel != impact) { impact = nouvel; if (hasNetwork()) getOrCreateNetwork().updateStressFor(this, impact); }
			if (act != actif || dbl != double_ || Math.abs(retire - allege) > 1) {
				if (act && !actif) level.playSound(null, worldPosition, SoundEvents.BEACON_POWER_SELECT, SoundSource.BLOCKS, 0.25f, 1.6f);
				actif = act; double_ = dbl; allege = retire; sendData();
			}
		}
		/** Côté client : quelques étincelles rouges qui s'échappent de la jante du volant. */
		private void etincelles() {
			RandomSource r = level.random;
			if (r.nextInt(6) != 0) return;
			Direction.Axis a = getBlockState().getValue(BlockStateProperties.AXIS);
			double t = r.nextDouble() * Math.PI * 2, c = Math.cos(t) * 0.44, s = Math.sin(t) * 0.44;
			double x = 0.5, y = 0.5, z = 0.5;
			switch (a) { case X -> { y += c; z += s; } case Y -> { x += c; z += s; } default -> { x += c; y += s; } }
			level.addParticle(new DustParticleOptions(new Vector3f(0.85f, 0.18f, 0.12f), 0.6f), worldPosition.getX() + x, worldPosition.getY() + y, worldPosition.getZ() + z, 0, 0.01, 0);
			if (r.nextInt(12) == 0) level.addParticle(ParticleTypes.ELECTRIC_SPARK, worldPosition.getX() + x, worldPosition.getY() + y, worldPosition.getZ() + z, 0, 0.02, 0);
		}
		@Override
		public void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			t.putFloat("impact", impact); t.putFloat("allege", allege); t.putBoolean("actif", actif); t.putBoolean("double", double_);
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			impact = t.getFloat("impact"); allege = t.getFloat("allege"); actif = t.getBoolean("actif"); double_ = t.getBoolean("double");
		}
		@Override
		public boolean addToGoggleTooltip(List<Component> tt, boolean accroupi) {
			tt.add(Component.literal("    ").append(Component.translatable("block.airain.airain_load_reliever")).withStyle(ChatFormatting.GOLD));
			if (double_) tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.double")).withStyle(ChatFormatting.RED));
			else if (!actif) tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.repos")).withStyle(ChatFormatting.GRAY));
			else {
				tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.allege", Math.round(allege))).withStyle(ChatFormatting.AQUA));
				tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.allege_part", Math.round(ALLEGEMENT * 100))).withStyle(ChatFormatting.DARK_GRAY));
			}
			return true;
		}
	}

	// ====================================================================== le surcompresseur (bloc ; FACING : vers le générateur)
	public static class Surcompresseur extends BlocPatine implements EntityBlock {
		private static final Map<Direction, VoxelShape> FORMES = new java.util.EnumMap<>(Direction.class);
		static {
			for (Direction d : Direction.Plane.HORIZONTAL)
				FORMES.put(d, Shapes.or(Block.box(0, 0, 0, 16, 3, 16), ConduitAir.boiteVers(d, 2, 3, 3, 14, 14, 13), ConduitAir.boiteVers(d, 5, 4, 0, 11, 10, 3), ConduitAir.boiteVers(d, 5, 14, 10, 11, 21, 14)));
		}
		public Surcompresseur(WeatherState etat, Properties p) { super(etat, p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING); }
		// posé contre le générateur : le raccord se tourne vers lui
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction f = c.getClickedFace().getAxis().isHorizontal() ? c.getClickedFace().getOpposite() : c.getHorizontalDirection();
			for (Direction d : Direction.Plane.HORIZONTAL)
				if (c.getLevel().getBlockEntity(c.getClickedPos().relative(d)) instanceof GeneratingKineticBlockEntity) { f = d; break; }
			return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, f);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(BlockStateProperties.HORIZONTAL_FACING)); }
		@Override
		protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
			super.onPlace(s, l, p, ancien, deplace);
			if (!l.isClientSide && !ancien.is(s.getBlock())) reveiller(l, cible(l, p, s));
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			GeneratingKineticBlockEntity g = l.isClientSide || n.getBlock() instanceof Surcompresseur ? null : cible(l, p, s);
			super.onRemove(s, l, p, n, deplace);
			if (g != null) reveiller(l, g);
		}
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new SurcompresseurBlockEntity(SURCOMP_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return t == SURCOMP_BE.get() ? (lv, p, st, be) -> ((SurcompresseurBlockEntity) be).tick() : null;
		}
	}
	/** Le générateur que ce surcompresseur alimente : celui devant son raccord, sinon le plus proche à 2 blocs (grandes roues, moulins). */
	public static GeneratingKineticBlockEntity cible(Level l, BlockPos p, BlockState s) {
		if (!(s.getBlock() instanceof Surcompresseur)) return null;
		Direction f = s.getValue(BlockStateProperties.HORIZONTAL_FACING);
		if (l.getBlockEntity(p.relative(f)) instanceof GeneratingKineticBlockEntity g && admis(g)) return g;
		GeneratingKineticBlockEntity mieux = null; double dm = 99;
		for (BlockPos q : BlockPos.betweenClosed(p.offset(-2, -2, -2), p.offset(2, 2, 2)))
			if (l.getBlockEntity(q) instanceof GeneratingKineticBlockEntity g && admis(g)) {
				double d = q.distSqr(p);
				if (d < dm) { dm = d; mieux = g; }
			}
		return mieux;
	}
	private static boolean admis(GeneratingKineticBlockEntity g) { return !(g instanceof CreativeMotorBlockEntity); }
	static void reveiller(Level l, GeneratingKineticBlockEntity g) { if (g != null && !g.isRemoved()) g.updateGeneratedRotation(); }
	/** Facteur de capacité d'un générateur (appelé par le mixin) : 1,5 si un surcompresseur l'alimente. */
	public static float facteur(KineticBlockEntity be) {
		Level l = be.getLevel();
		if (l == null || !(be instanceof GeneratingKineticBlockEntity g) || !admis(g)) return 1f;
		BlockPos p = be.getBlockPos();
		for (BlockPos q : BlockPos.betweenClosed(p.offset(-2, -2, -2), p.offset(2, 2, 2))) {
			BlockState s = l.getBlockState(q);
			if (s.getBlock() instanceof Surcompresseur && cible(l, q.immutable(), s) == be) return SURCOMPRESSION;
		}
		return 1f;
	}

	/** Le surcompresseur : pistons et manomètre qui suivent le générateur, bouffées de vapeur, et un rappel régulier de sa cible. */
	public static class SurcompresseurBlockEntity extends BlockEntity implements IHaveGoggleInformation {
		public float phase, phaseAvant, aiguille, vitesse;
		private BlockPos cibleAvant;
		private int attente;
		public SurcompresseurBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }
		public GeneratingKineticBlockEntity generateur() { return level == null ? null : cible(level, worldPosition, getBlockState()); }
		public void tick() {
			if (level == null) return;
			GeneratingKineticBlockEntity g = generateur();
			float v = g == null ? 0 : Math.abs(g.getSpeed());
			vitesse = v;
			if (level.isClientSide) {
				phaseAvant = phase;
				phase += v / 256f * 0.6f + (v > 0 ? 0.05f : 0);
				aiguille += ((v > 0 ? 0.35f + 0.65f * Math.min(1f, v / 256f) : 0) - aiguille) * 0.1f;
				if (v > 0 && level.random.nextInt(Math.max(4, 24 - (int) (v / 12))) == 0) {
					Direction f = getBlockState().getValue(BlockStateProperties.HORIZONTAL_FACING);
					double x = worldPosition.getX() + 0.5 - f.getStepX() * 0.25 + f.getClockWise().getStepX() * 0.3, z = worldPosition.getZ() + 0.5 - f.getStepZ() * 0.25 + f.getClockWise().getStepZ() * 0.3;
					level.addParticle(ParticleTypes.CLOUD, x, worldPosition.getY() + 1.0, z, 0, 0.04 + v / 256f * 0.06, 0);
				}
				return;
			}
			if (--attente > 0) return;
			attente = 40;
			BlockPos c = g == null ? null : g.getBlockPos();
			if (c == null ? cibleAvant != null : !c.equals(cibleAvant)) {            // la cible a changé : on prévient l'ancienne et la nouvelle
				if (cibleAvant != null && level.getBlockEntity(cibleAvant) instanceof GeneratingKineticBlockEntity a) reveiller(level, a);
				reveiller(level, g);
				cibleAvant = c;
			}
			if (v > 0 && level.random.nextInt(4) == 0) level.playSound(null, worldPosition, SoundEvents.FIRE_EXTINGUISH, SoundSource.BLOCKS, 0.06f, 1.4f);
		}
		@Override
		public boolean addToGoggleTooltip(List<Component> tt, boolean accroupi) {
			tt.add(Component.literal("    ").append(Component.translatable("block.airain.airain_supercharger")).withStyle(ChatFormatting.GOLD));
			GeneratingKineticBlockEntity g = generateur();
			if (g == null) { tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.sans_generateur")).withStyle(ChatFormatting.RED)); return true; }
			tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.alimente", g.getBlockState().getBlock().getName())).withStyle(ChatFormatting.GRAY));
			tt.add(Component.literal("    ").append(Component.translatable("airain.mecanique.surcomp", Math.round((SURCOMPRESSION - 1) * 100))).withStyle(ChatFormatting.AQUA));
			return true;
		}
		@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
		@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
	}

	// ====================================================================== enregistrement (4 teintes × patinable/cirée)
	private static final WeatherState[] ETATS = {WeatherState.UNAFFECTED, WeatherState.EXPOSED, WeatherState.WEATHERED, WeatherState.OXIDIZED};
	private static final MapColor[] COULEURS = {MapColor.GOLD, MapColor.TERRACOTTA_YELLOW, MapColor.TERRACOTTA_ORANGE, MapColor.TERRACOTTA_RED};
	public static final Map<String, List<DeferredBlock<Block>>> FAMILLES = new LinkedHashMap<>();
	private interface Fabrique { Block creer(WeatherState e, BlockBehaviour.Properties p); }
	private static void famille(String nom, Fabrique f) {
		List<DeferredBlock<Block>> t = new ArrayList<>();
		for (int s = 0; s < 4; s++)
			for (int c = 0; c < 2; c++) {
				final int st = s; final boolean cire = c == 1;
				String id = (cire ? "waxed_" : "") + BlocsAirain.STADES[s] + nom;
				DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, () -> f.creer(cire ? null : ETATS[st],
					BlockBehaviour.Properties.of().mapColor(COULEURS[st]).requiresCorrectToolForDrops().strength(4f, 8f).sound(SoundType.COPPER).noOcclusion()
						.isRedstoneConductor((a, bb, cc) -> false).isSuffocating((a, bb, cc) -> false).isViewBlocking((a, bb, cc) -> false)));
				AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
				t.add(b);
			}
		FAMILLES.put(nom, t);
	}
	static {
		famille("airain_load_reliever", Allegeur::new);
		famille("airain_supercharger", Surcompresseur::new);
	}
	private static Block[] blocs(String f) { return FAMILLES.get(f).stream().map(DeferredBlock::get).toArray(Block[]::new); }
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<AllegeurBlockEntity>> ALLEGEUR_BE = AirainMod.BLOCK_ENTITIES.register("airain_load_reliever",
		() -> BlockEntityType.Builder.of((p, s) -> new AllegeurBlockEntity(Mecanique.ALLEGEUR_BE.get(), p, s), blocs("airain_load_reliever")).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<SurcompresseurBlockEntity>> SURCOMP_BE = AirainMod.BLOCK_ENTITIES.register("airain_supercharger",
		() -> BlockEntityType.Builder.of((p, s) -> new SurcompresseurBlockEntity(Mecanique.SURCOMP_BE.get(), p, s), blocs("airain_supercharger")).build(null));

	public static void charger() {}
}
