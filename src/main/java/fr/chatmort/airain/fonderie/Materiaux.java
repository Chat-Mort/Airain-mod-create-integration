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
			bloc(teinte + "_marble_pillar", () -> new RotatedPillarBlock(pierre(c, son)));
			bloc("chiseled_" + teinte + "_marble", () -> new Block(pierre(c, son)));
		}
		famille("slate", "slate", MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES, true, true, true);
		famille("slate_shingles", "slate_shingle", MapColor.DEEPSLATE, SoundType.DEEPSLATE_TILES, true, true, false);
		famille("marble_tiles", "marble_tile", MapColor.QUARTZ, SoundType.CALCITE, false, true, false);
	}

	public static void charger() {}
	@SuppressWarnings("unused") private static final Function<String, String> RIEN = s -> s;
}
