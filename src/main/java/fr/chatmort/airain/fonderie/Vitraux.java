package fr.chatmort.airain.fonderie;

import com.mojang.serialization.MapCodec;
import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * 1.72 : petits vitraux, 16 couleurs × 2 dessins de plombs (losanges, carreaux). Panneau fin posé face au joueur ;
 * les vitraux voisins dans le même plan se raccordent (n'importe quelle couleur), le cadre doré ne reste que sur le pourtour.
 */
public final class Vitraux {
	private Vitraux() {}

	public static final String[] COULEURS = {"white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray",
		"cyan", "purple", "blue", "brown", "green", "red", "black"};
	public static final String[] DESSINS = {"diamond", "square"};

	public static void charger() {
		for (String c : COULEURS)
			for (String d : DESSINS) {
				String n = c + "_" + d + "_leaded_glass";
				var b = AirainMod.BLOCKS.register(n, () -> new Vitrail(BlockBehaviour.Properties.of().mapColor(MapColor.NONE).strength(0.4f)
					.sound(SoundType.GLASS).noOcclusion().isValidSpawn((s, l, p, t) -> false).isRedstoneConductor((s, l, p) -> false)
					.isSuffocating((s, l, p) -> false).isViewBlocking((s, l, p) -> false)));
				AirainMod.ITEMS.register(n, () -> new BlockItem(b.get(), new Item.Properties()));
			}
	}

	public static final EnumProperty<Direction.Axis> AXE = BlockStateProperties.HORIZONTAL_AXIS;
	public static final BooleanProperty HAUT = BlockStateProperties.UP, BAS = BlockStateProperties.DOWN,
		GAUCHE = BooleanProperty.create("left"), DROITE = BooleanProperty.create("right");

	public static class Vitrail extends Block {
		public static final MapCodec<Vitrail> CODEC = simpleCodec(Vitrail::new);
		private static final VoxelShape Z = Block.box(0, 0, 7, 16, 16, 9), X = Block.box(7, 0, 0, 9, 16, 16);
		public Vitrail(Properties p) {
			super(p);
			registerDefaultState(defaultBlockState().setValue(AXE, Direction.Axis.Z).setValue(HAUT, false).setValue(BAS, false).setValue(GAUCHE, false).setValue(DROITE, false));
		}
		@Override protected MapCodec<? extends Block> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(AXE, HAUT, BAS, GAUCHE, DROITE); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return s.getValue(AXE) == Direction.Axis.Z ? Z : X; }

		/** Côtés du plan : gauche = x bas du modèle (ouest si axe z, nord si axe x tourné d'un quart). */
		private static Direction gauche(BlockState s) { return s.getValue(AXE) == Direction.Axis.Z ? Direction.WEST : Direction.NORTH; }
		private static boolean meme(BlockState s, BlockState n) { return n.getBlock() instanceof Vitrail && n.getValue(AXE) == s.getValue(AXE); }
		private BlockState relier(BlockState s, LevelAccessor l, BlockPos p) {
			Direction g = gauche(s);
			return s.setValue(HAUT, meme(s, l.getBlockState(p.above()))).setValue(BAS, meme(s, l.getBlockState(p.below())))
				.setValue(GAUCHE, meme(s, l.getBlockState(p.relative(g)))).setValue(DROITE, meme(s, l.getBlockState(p.relative(g.getOpposite()))));
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			// posé face au joueur ; contre un vitrail voisin, on reprend son plan
			Direction.Axis ax = c.getHorizontalDirection().getAxis();
			BlockState contre = c.getLevel().getBlockState(c.getClickedPos().relative(c.getClickedFace().getOpposite()));
			if (contre.getBlock() instanceof Vitrail && c.getClickedFace().getAxis() != contre.getValue(AXE)) ax = contre.getValue(AXE);
			return relier(defaultBlockState().setValue(AXE, ax), c.getLevel(), c.getClickedPos());
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState n, LevelAccessor l, BlockPos p, BlockPos np) { return relier(s, l, p); }
		/** Entre deux vitraux du même plan, les tranches qui se touchent ne sont pas dessinées. */
		@Override
		protected boolean skipRendering(BlockState s, BlockState n, Direction d) {
			return (meme(s, n) && d.getAxis() != s.getValue(AXE)) || super.skipRendering(s, n, d);
		}
		@Override protected boolean propagatesSkylightDown(BlockState s, BlockGetter l, BlockPos p) { return true; }
		@Override protected float getShadeBrightness(BlockState s, BlockGetter l, BlockPos p) { return 1f; }
	}
}
