package fr.chatmort.airain.fonderie;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WeatheringCopper;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 1.63 : cloisons grillagées et portail coulissant. Les cloisons se raccordent comme des barreaux (lignes, angles, T) et
 * s'empilent (bandeau en haut et en bas de la cloison). Le portail glisse le long de la cloison : clic droit main nue
 * pour l'ouvrir ou le fermer, ou un signal de redstone. Les portails voisins (en largeur et en hauteur) bougent ensemble.
 * Quatre teintes qui se patinent, et cirées, comme le reste de l'airain.
 */
public final class Cloisons {
	private Cloisons() {}

	public static final BooleanProperty HAUT = BooleanProperty.create("top"), BAS = BooleanProperty.create("bottom");
	public static final BooleanProperty OUVERT = BlockStateProperties.OPEN, ALIM = BlockStateProperties.POWERED;
	/** Le portail glisse vers le bout positif de son axe (est ou sud), sinon vers le négatif. */
	public static final BooleanProperty SENS = BooleanProperty.create("slide_positive");
	public static final EnumProperty<Direction.Axis> AXE = BlockStateProperties.HORIZONTAL_AXIS;

	// ====================================================================== la cloison
	public static class Cloison extends IronBarsBlock implements Passerelle.Patinable {
		private final WeatherState etat;
		public Cloison(WeatherState etat, Properties p) { super(p); this.etat = etat; registerDefaultState(defaultBlockState().setValue(HAUT, true).setValue(BAS, true)); }
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { super.createBlockStateDefinition(b); b.add(HAUT, BAS); }
		private static BlockState vertical(BlockState s, BlockGetter l, BlockPos p) {
			return s.setValue(HAUT, !(l.getBlockState(p.above()).getBlock() instanceof Cloison)).setValue(BAS, !(l.getBlockState(p.below()).getBlock() instanceof Cloison));
		}
		/** Raccord aussi aux portails coulissants (que les barreaux de Minecraft ignorent). */
		private static BlockState portails(BlockState s, BlockGetter l, BlockPos p) {
			for (Direction d : Direction.Plane.HORIZONTAL) if (l.getBlockState(p.relative(d)).getBlock() instanceof Portail) s = s.setValue(PROPERTY_BY_DIRECTION.get(d), true);
			return s;
		}
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return portails(vertical(super.getStateForPlacement(c), c.getLevel(), c.getClickedPos()), c.getLevel(), c.getClickedPos()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			BlockState r = super.updateShape(s, d, v, l, p, np);
			return d.getAxis() == Direction.Axis.Y ? vertical(r, l, p) : portails(r, l, p);
		}
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
	}

	// ====================================================================== le portail coulissant
	public static class Portail extends Block implements EntityBlock, Passerelle.Patinable, IWrenchable {
		private final WeatherState etat;
		public final int stade;
		private static final VoxelShape X = Block.box(0, 0, 9, 16, 16, 11), Z = Block.box(9, 0, 0, 11, 16, 16);
		public Portail(WeatherState etat, int stade, Properties p) {
			super(p); this.etat = etat; this.stade = stade;
			registerDefaultState(defaultBlockState().setValue(AXE, Direction.Axis.X).setValue(OUVERT, false).setValue(ALIM, false).setValue(SENS, true));
		}
		@Override public WeatherState etat() { return etat; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(AXE, OUVERT, ALIM, SENS); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction.Axis a = c.getHorizontalDirection().getClockWise().getAxis();
			Level l = c.getLevel(); BlockPos p = c.getClickedPos();
			// il glisse du côté d'une cloison (où le vantail ira se ranger), sinon vers l'est ou le sud
			boolean neg = l.getBlockState(p.relative(a, -1)).getBlock() instanceof Cloison && !(l.getBlockState(p.relative(a, 1)).getBlock() instanceof Cloison);
			BlockState voisin = l.getBlockState(p.relative(a, -1));
			if (voisin.getBlock() instanceof Portail && voisin.getValue(AXE) == a) return defaultBlockState().setValue(AXE, a).setValue(SENS, voisin.getValue(SENS)).setValue(OUVERT, voisin.getValue(OUVERT));
			voisin = l.getBlockState(p.relative(a, 1));
			if (voisin.getBlock() instanceof Portail && voisin.getValue(AXE) == a) return defaultBlockState().setValue(AXE, a).setValue(SENS, voisin.getValue(SENS)).setValue(OUVERT, voisin.getValue(OUVERT));
			return defaultBlockState().setValue(AXE, a).setValue(SENS, !neg);
		}
		@Override
		protected BlockState rotate(BlockState s, Rotation r) {
			if (r == Rotation.NONE || r == Rotation.CLOCKWISE_180) return s;
			return s.setValue(AXE, s.getValue(AXE) == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.X);
		}
		// ouvert, le portail reste visable sur toute sa baie (pour le refermer ou le casser) mais ne bloque plus le passage
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return s.getValue(AXE) == Direction.Axis.X ? X : Z; }
		@Override protected VoxelShape getCollisionShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return s.getValue(OUVERT) ? Shapes.empty() : getShape(s, l, p, c); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.ENTITYBLOCK_ANIMATED; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new PortailBE(PORTAIL_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return l.isClientSide && t == PORTAIL_BE.get() ? (lv, p, st, be) -> ((PortailBE) be).tick() : null;
		}
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }

		/** Le vantail entier : les portails voisins de même axe, en largeur et en hauteur. */
		public static List<BlockPos> vantail(BlockGetter l, BlockPos p, Direction.Axis a) {
			List<BlockPos> r = new ArrayList<>(); Set<BlockPos> vus = new HashSet<>(); ArrayDeque<BlockPos> f = new ArrayDeque<>();
			f.add(p); vus.add(p);
			while (!f.isEmpty() && r.size() < 48) {
				BlockPos q = f.poll(); BlockState s = l.getBlockState(q);
				if (!(s.getBlock() instanceof Portail) || s.getValue(AXE) != a) continue;
				r.add(q);
				for (BlockPos n : new BlockPos[] {q.relative(a, 1), q.relative(a, -1), q.above(), q.below()}) if (vus.add(n)) f.add(n);
			}
			return r;
		}
		private static void basculer(Level l, BlockPos p, BlockState s, boolean ouvert, Boolean alim) {
			for (BlockPos q : vantail(l, p, s.getValue(AXE))) {
				BlockState t = l.getBlockState(q).setValue(OUVERT, ouvert);
				if (alim != null) t = t.setValue(ALIM, alim);
				l.setBlock(q, t, Block.UPDATE_CLIENTS | Block.UPDATE_NEIGHBORS);
			}
			l.playSound(null, p, ouvert ? SoundEvents.IRON_TRAPDOOR_OPEN : SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.BLOCKS, 0.9f, 0.7f);
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!l.isClientSide) basculer(l, p, s, !s.getValue(OUVERT), null);
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected void neighborChanged(BlockState s, Level l, BlockPos p, Block b, BlockPos np, boolean m) {
			if (l.isClientSide) return;
			boolean signal = false;
			for (BlockPos q : vantail(l, p, s.getValue(AXE))) if (l.hasNeighborSignal(q)) { signal = true; break; }
			if (signal != s.getValue(ALIM)) basculer(l, p, s, signal, signal);
		}
		/** Clé de Create : change le côté où glisse le vantail. */
		@Override
		public InteractionResult onWrenched(BlockState s, UseOnContext c) {
			Level l = c.getLevel();
			if (!l.isClientSide) {
				boolean n = !s.getValue(SENS);
				for (BlockPos q : vantail(l, c.getClickedPos(), s.getValue(AXE))) l.setBlock(q, l.getBlockState(q).setValue(SENS, n), Block.UPDATE_CLIENTS);
				l.playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
			}
			return InteractionResult.SUCCESS;
		}
	}
	/** Côté client : avancée de l'ouverture, pour le glissement en douceur. */
	public static class PortailBE extends BlockEntity {
		public float avance, avant;
		public PortailBE(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); avance = avant = s.getValue(OUVERT) ? 1 : 0; }
		void tick() { avant = avance; float cible = getBlockState().getValue(OUVERT) ? 1 : 0; avance += Math.signum(cible - avance) * Math.min(Math.abs(cible - avance), 1 / 14f); }
		public net.minecraft.world.phys.AABB getRenderBoundingBox() { return new net.minecraft.world.phys.AABB(worldPosition).inflate(10, 1, 10); }
	}

	// ====================================================================== enregistrement
	private static final WeatherState[] ETATS = {WeatherState.UNAFFECTED, WeatherState.EXPOSED, WeatherState.WEATHERED, WeatherState.OXIDIZED};
	private static final MapColor[] COULEURS = {MapColor.GOLD, MapColor.TERRACOTTA_ORANGE, MapColor.TERRACOTTA_RED, MapColor.COLOR_RED};
	public static final Map<String, DeferredBlock<Block>[][]> FAMILLES = new LinkedHashMap<>();
	private interface Fabrique { Block creer(WeatherState etat, int stade, BlockBehaviour.Properties p); }
	@SuppressWarnings("unchecked")
	private static void famille(String nom, Fabrique f) {
		DeferredBlock<Block>[][] t = new DeferredBlock[4][2];
		for (int s = 0; s < 4; s++)
			for (int c = 0; c < 2; c++) {
				final int st = s; final boolean cire = c == 1;
				String id = (cire ? "waxed_" : "") + BlocsAirain.STADES[s] + nom;
				DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, () -> f.creer(cire ? null : ETATS[st], st,
					BlockBehaviour.Properties.of().mapColor(COULEURS[st]).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
						.isValidSpawn((a, bb, cc, dd) -> false).isRedstoneConductor((a, bb, cc) -> false).isSuffocating((a, bb, cc) -> false).isViewBlocking((a, bb, cc) -> false)));
				AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
				t[s][c] = b;
			}
		FAMILLES.put(nom, t);
	}
	static {
		famille("airain_mesh_fence", (e, s, p) -> new Cloison(e, p));
		famille("airain_sliding_gate", Portail::new);
	}
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<PortailBE>> PORTAIL_BE = AirainMod.BLOCK_ENTITIES.register("airain_sliding_gate", () -> {
		List<Block> b = new ArrayList<>();
		for (DeferredBlock<Block>[] t : FAMILLES.get("airain_sliding_gate")) for (DeferredBlock<Block> x : t) b.add(x.get());
		return BlockEntityType.Builder.of((p, s) -> new PortailBE(Cloisons.PORTAIL_BE.get(), p, s), b.toArray(new Block[0])).build(null);
	});
	public static void charger() {}
}
