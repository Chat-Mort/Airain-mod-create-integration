package fr.chatmort.airain.fonderie;

import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.DoubleHighBlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.WeatheringCopperDoorBlock;
import net.minecraft.world.level.block.WeatheringCopperFullBlock;
import net.minecraft.world.level.block.WeatheringCopperGrateBlock;
import net.minecraft.world.level.block.WeatheringCopperSlabBlock;
import net.minecraft.world.level.block.WeatheringCopperStairBlock;
import net.minecraft.world.level.block.WeatheringCopperTrapDoorBlock;
import net.minecraft.world.level.block.ChainBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Le style impérial : tous les blocs d'airain, chacun en quatre stades (neuf, terni, vieilli, rouge impérial)
 * et en version cirée. Le temps les fait passer d'un stade au suivant, comme le cuivre (data maps
 * neoforge:oxidizables et neoforge:waxables, générées avec les modèles).
 * Nom d'un bloc : [waxed_][exposed_|weathered_|oxidized_]<famille>, ex. waxed_weathered_cut_airain.
 */
public final class BlocsAirain {
	private BlocsAirain() {}

	public static final String[] STADES = {"", "exposed_", "weathered_", "oxidized_"};
	private static final WeatherState[] ETATS = {WeatherState.UNAFFECTED, WeatherState.EXPOSED, WeatherState.WEATHERED, WeatherState.OXIDIZED};
	// couleur sur les cartes : du doré au rouge impérial
	private static final MapColor[] COULEURS = {MapColor.GOLD, MapColor.TERRACOTTA_YELLOW, MapColor.TERRACOTTA_ORANGE, MapColor.TERRACOTTA_RED};

	/** famille → [stade][0 = se patine, 1 = cirée] */
	public static final Map<String, DeferredBlock<Block>[][]> FAMILLES = new LinkedHashMap<>();

	private interface Fabrique { Block creer(int stade, boolean cire, BlockBehaviour.Properties p); }

	private static BlockBehaviour.Properties proprietes(int stade) {
		return BlockBehaviour.Properties.of().mapColor(COULEURS[stade]).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER);
	}

	@SuppressWarnings("unchecked")
	private static void famille(String nom, Fabrique f, java.util.function.UnaryOperator<BlockBehaviour.Properties> retouche, boolean porte) {
		DeferredBlock<Block>[][] t = new DeferredBlock[4][2];
		for (int s = 0; s < 4; s++) {
			for (int c = 0; c < 2; c++) {
				final int st = s; final boolean cire = c == 1;
				String id = (cire ? "waxed_" : "") + STADES[s] + nom;
				DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, () -> f.creer(st, cire, retouche.apply(proprietes(st))));
				if (porte) AirainMod.ITEMS.register(id, () -> new DoubleHighBlockItem(b.get(), new Item.Properties()));
				else AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
				t[s][c] = b;
			}
		}
		FAMILLES.put(nom, t);
	}

	static {
		var id = (java.util.function.UnaryOperator<BlockBehaviour.Properties>) p -> p;
		// blocs pleins
		for (String n : new String[] {"airain_block", "cut_airain", "riveted_airain", "chiseled_airain"})
			famille(n, (s, c, p) -> c ? new Block(p) : new WeatheringCopperFullBlock(ETATS[s], p), id, false);
		famille("airain_pillar", (s, c, p) -> c ? new RotatedPillarBlock(p) : new Patine.Pilier(ETATS[s], p), id, false);
		// escaliers et dalles (lisse et taillé) : l'escalier reprend l'état du bloc plein du même stade
		for (String[] es : new String[][] {{"airain_stairs", "airain_block"}, {"cut_airain_stairs", "cut_airain"}}) {
			final String base = es[1];
			famille(es[0], (s, c, p) -> {
				var etat = FAMILLES.get(base)[s][c ? 1 : 0].get().defaultBlockState();
				return c ? new StairBlock(etat, p) : new WeatheringCopperStairBlock(ETATS[s], etat, p);
			}, id, false);
		}
		famille("airain_slab", (s, c, p) -> c ? new SlabBlock(p) : new WeatheringCopperSlabBlock(ETATS[s], p), id, false);
		famille("cut_airain_slab", (s, c, p) -> c ? new SlabBlock(p) : new WeatheringCopperSlabBlock(ETATS[s], p), id, false);
		// pièces ajourées et décor
		var ajoure = (java.util.function.UnaryOperator<BlockBehaviour.Properties>) p -> p.noOcclusion()
			.isValidSpawn((a, b, c, d) -> false).isRedstoneConductor((a, b, c) -> false).isSuffocating((a, b, c) -> false).isViewBlocking((a, b, c) -> false);
		famille("airain_grate", (s, c, p) -> c ? new Patine.GrilleCiree(p) : new WeatheringCopperGrateBlock(ETATS[s], p), ajoure, false);
		famille("airain_bars", (s, c, p) -> c ? new Patine.BarreauxCires(p) : new Patine.Barreaux(ETATS[s], p), p -> p.noOcclusion().strength(5f, 6f), false);
		famille("airain_door", (s, c, p) -> c ? new DoorBlock(BlockSetType.COPPER, p) : new WeatheringCopperDoorBlock(BlockSetType.COPPER, ETATS[s], p),
			p -> p.noOcclusion().pushReaction(net.minecraft.world.level.material.PushReaction.DESTROY), true);
		famille("airain_trapdoor", (s, c, p) -> c ? new TrapDoorBlock(BlockSetType.COPPER, p) : new WeatheringCopperTrapDoorBlock(BlockSetType.COPPER, ETATS[s], p),
			p -> p.noOcclusion().isValidSpawn((a, b, c, d) -> false), false);
		famille("airain_chain", (s, c, p) -> c ? new ChainBlock(p) : new Patine.Chaine(ETATS[s], p), p -> p.noOcclusion().sound(SoundType.CHAIN).strength(5f, 6f), false);
		famille("airain_lantern", (s, c, p) -> c ? new Patine.Lanterne(p) : new Patine.LanternePatinable(ETATS[s], p),
			p -> p.noOcclusion().sound(SoundType.LANTERN).strength(3.5f).lightLevel(e -> 11).pushReaction(net.minecraft.world.level.material.PushReaction.DESTROY), false);
	}

	/** Force le chargement de la classe avant l'enregistrement. */
	public static void charger() {}
	@SuppressWarnings("unused") private static final Class<?> LANTERNE = LanternBlock.class;
}
