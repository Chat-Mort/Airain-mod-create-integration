package fr.chatmort.airain.fonderie;

import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;

import java.util.function.Function;
import java.util.function.Supplier;

/**
 * Matériaux de construction de l'Empire (1.57) : marbre blanc et marbre noir veinés d'or, ardoise, carrelage.
 * Marbre : mélangeur de Create (8 pierres + 1 pépite d'or) ; ardoise : presse sur de la deepslate pavée ;
 * variantes au tailleur de pierre. Le marbre brut tire au hasard une de ses 6 textures (blockstate).
 */
public final class Materiaux {
	private Materiaux() {}

	private static BlockBehaviour.Properties pierre(MapColor c, SoundType son) {
		return BlockBehaviour.Properties.of().mapColor(c).requiresCorrectToolForDrops().strength(1.8f, 6f).sound(son);
	}
	private static <B extends Block> DeferredBlock<B> bloc(String id, Supplier<B> f) {
		DeferredBlock<B> b = AirainMod.BLOCKS.register(id, f);
		AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
		return b;
	}
	/** Un bloc plein, et à volonté ses escaliers, sa dalle et son muret. */
	private static DeferredBlock<Block> famille(String id, String racine, MapColor c, SoundType son, boolean escaliers, boolean dalle, boolean muret) {
		DeferredBlock<Block> b = bloc(id, () -> new Block(pierre(c, son)));
		if (escaliers) bloc(racine + "_stairs", () -> new StairBlock(b.get().defaultBlockState(), pierre(c, son)));
		if (dalle) bloc(racine + "_slab", () -> new SlabBlock(pierre(c, son)));
		if (muret) bloc(racine + "_wall", () -> new WallBlock(pierre(c, son).forceSolidOn()));
		return b;
	}

	static {
		for (String teinte : new String[]{"white", "black"}) {
			MapColor c = teinte.equals("white") ? MapColor.QUARTZ : MapColor.COLOR_BLACK;
			SoundType son = SoundType.CALCITE;
			famille(teinte + "_marble", teinte + "_marble", c, son, true, true, true);
			famille("polished_" + teinte + "_marble", "polished_" + teinte + "_marble", c, son, true, true, false);
			famille(teinte + "_marble_bricks", teinte + "_marble_brick", c, son, true, true, true);
			// 1.67 : colonne raccordée (bandes d'or seulement aux bouts d'une colonne)
			bloc(teinte + "_marble_pillar", () -> new Colonne(pierre(c, son)));
			bloc("chiseled_" + teinte + "_marble", () -> new Block(pierre(c, son)));
		}
		famille("slate", "slate", MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES, true, true, true);
		famille("slate_shingles", "slate_shingle", MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES, true, true, false);
		famille("marble_tiles", "marble_tile", MapColor.QUARTZ, SoundType.CALCITE, false, true, false);
		// 1.67 : nouvelles ardoises (briques, petites dalles, taillée, chevrons, ciselée, colonne cannelée)
		famille("slate_bricks", "slate_brick", MapColor.DEEPSLATE, SoundType.DEEPSLATE_BRICKS, true, true, true);
		famille("small_slate_tiles", "small_slate_tile", MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES, true, true, true);
		famille("cut_slate", "cut_slate", MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES, true, true, true);
		bloc("herringbone_slate", () -> new Block(pierre(MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES)));
		bloc("chiseled_slate", () -> new Block(pierre(MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES)));
		bloc("slate_pillar", () -> new Colonne(pierre(MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES)));
	}

	/**
	 * 1.67 : colonne qui se raccorde à ses voisines de même axe. FIN_POS / FIN_NEG : ce bloc est le bout de la colonne
	 * du côté positif (haut, est, sud) / négatif de son axe ; la bande décorative n'est dessinée que là.
	 */
	public static class Colonne extends RotatedPillarBlock {
		public static final net.minecraft.world.level.block.state.properties.BooleanProperty FIN_POS = net.minecraft.world.level.block.state.properties.BooleanProperty.create("positive_end"),
				FIN_NEG = net.minecraft.world.level.block.state.properties.BooleanProperty.create("negative_end");
		public Colonne(BlockBehaviour.Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FIN_POS, true).setValue(FIN_NEG, true)); }
		@Override protected void createBlockStateDefinition(net.minecraft.world.level.block.state.StateDefinition.Builder<Block, net.minecraft.world.level.block.state.BlockState> b) { super.createBlockStateDefinition(b); b.add(FIN_POS, FIN_NEG); }
		private net.minecraft.world.level.block.state.BlockState raccords(net.minecraft.world.level.block.state.BlockState s, net.minecraft.world.level.LevelReader l, net.minecraft.core.BlockPos p) {
			net.minecraft.core.Direction.Axis a = s.getValue(AXIS);
			return s.setValue(FIN_POS, !meme(s, l.getBlockState(p.relative(net.minecraft.core.Direction.fromAxisAndDirection(a, net.minecraft.core.Direction.AxisDirection.POSITIVE)))))
					.setValue(FIN_NEG, !meme(s, l.getBlockState(p.relative(net.minecraft.core.Direction.fromAxisAndDirection(a, net.minecraft.core.Direction.AxisDirection.NEGATIVE)))));
		}
		// même bloc, même axe : la colonne continue
		private boolean meme(net.minecraft.world.level.block.state.BlockState s, net.minecraft.world.level.block.state.BlockState v) { return v.is(this) && v.getValue(AXIS) == s.getValue(AXIS); }
		@Override public net.minecraft.world.level.block.state.BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext c) { return raccords(super.getStateForPlacement(c), c.getLevel(), c.getClickedPos()); }
		@Override
		protected net.minecraft.world.level.block.state.BlockState updateShape(net.minecraft.world.level.block.state.BlockState s, net.minecraft.core.Direction d, net.minecraft.world.level.block.state.BlockState v, net.minecraft.world.level.LevelAccessor l, net.minecraft.core.BlockPos p, net.minecraft.core.BlockPos np) {
			return d.getAxis() == s.getValue(AXIS) ? raccords(s, l, p) : s;
		}
		// tournée (structures), la colonne garde ses bouts quand l'axe change ; un demi-tour échange les deux bouts
		@Override
		protected net.minecraft.world.level.block.state.BlockState rotate(net.minecraft.world.level.block.state.BlockState s, net.minecraft.world.level.block.Rotation r) {
			net.minecraft.world.level.block.state.BlockState t = super.rotate(s, r);
			net.minecraft.core.Direction.Axis a = s.getValue(AXIS);
			boolean inverse = a != net.minecraft.core.Direction.Axis.Y && (r == net.minecraft.world.level.block.Rotation.CLOCKWISE_180
					|| (r == net.minecraft.world.level.block.Rotation.CLOCKWISE_90 && a == net.minecraft.core.Direction.Axis.Z)
					|| (r == net.minecraft.world.level.block.Rotation.COUNTERCLOCKWISE_90 && a == net.minecraft.core.Direction.Axis.X));
			return inverse ? t.setValue(FIN_POS, s.getValue(FIN_NEG)).setValue(FIN_NEG, s.getValue(FIN_POS)) : t;
		}
	}

	public static void charger() {}
	@SuppressWarnings("unused") private static final Function<String, String> RIEN = s -> s;
}
