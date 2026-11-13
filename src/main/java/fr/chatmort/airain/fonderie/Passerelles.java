package fr.chatmort.airain.fonderie;

import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

import java.util.LinkedHashMap;
import java.util.Map;

/** Enregistrement des passerelles d'airain : 8 familles × 4 teintes × (patinable, cirée), et le portillon. */
public final class Passerelles {
	private Passerelles() {}

	private static final WeatherState[] ETATS = {WeatherState.UNAFFECTED, WeatherState.EXPOSED, WeatherState.WEATHERED, WeatherState.OXIDIZED};
	private static final MapColor[] COULEURS = {MapColor.GOLD, MapColor.TERRACOTTA_YELLOW, MapColor.TERRACOTTA_ORANGE, MapColor.TERRACOTTA_RED};
	public static final Map<String, DeferredBlock<Block>[][]> FAMILLES = new LinkedHashMap<>();

	private interface Fabrique { Block creer(WeatherState etat, BlockBehaviour.Properties p); }

	@SuppressWarnings("unchecked")
	private static void famille(String nom, Fabrique f) {
		DeferredBlock<Block>[][] t = new DeferredBlock[4][2];
		for (int s = 0; s < 4; s++)
			for (int c = 0; c < 2; c++) {
				final int st = s; final boolean cire = c == 1;
				String id = (cire ? "waxed_" : "") + BlocsAirain.STADES[s] + nom;
				DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, () -> f.creer(cire ? null : ETATS[st],
					BlockBehaviour.Properties.of().mapColor(COULEURS[st]).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
						.isValidSpawn((a, bb, cc, dd) -> false).isRedstoneConductor((a, bb, cc) -> false).isSuffocating((a, bb, cc) -> false).isViewBlocking((a, bb, cc) -> false)));
				AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
				t[s][c] = b;
			}
		FAMILLES.put(nom, t);
	}

	static {
		famille("airain_catwalk", Passerelle.Plancher::new);
		famille("airain_catwalk_stairs", Passerelle.Escalier::new);
		famille("airain_catwalk_ramp", Passerelle.Rampe::new);
		famille("airain_support", Passerelle.Poteau::new);
		famille("airain_ladder", Passerelle.Echelle::new);
		// pièces ajoutées en 1.50 : escalier à palier, suspente, rambarde seule
		famille("airain_catwalk_landing", Passerelle.Palier::new);
		famille("airain_hanger", Passerelle.Suspente::new);
		famille("airain_railing", Passerelle.RambardeSeule::new);
		// 1.52 : pièces-mécanismes des passerelles mobiles
		famille("airain_catwalk_drawbridge", (e, p) -> new PasserelleMobile(e, p, true));
		famille("airain_catwalk_telescopic", (e, p) -> new PasserelleMobile(e, p, false));
	}
	/** Le portillon : un objet qu'on pose sur un côté de passerelle (clic droit), puis qu'on ouvre main nue. */
	public static final DeferredItem<Item> PORTILLON = AirainMod.ITEMS.register("airain_catwalk_gate", () -> new Item(new Item.Properties()));

	/** Bloc-entité des pièces-mécanismes (toutes teintes). */
	@SuppressWarnings("DataFlowIssue")
	public static final net.neoforged.neoforge.registries.DeferredHolder<net.minecraft.world.level.block.entity.BlockEntityType<?>, net.minecraft.world.level.block.entity.BlockEntityType<PasserelleMobile.Mecanisme>> MOBILE_BE =
		AirainMod.BLOCK_ENTITIES.register("airain_catwalk_mechanism", () -> {
			java.util.List<Block> b = new java.util.ArrayList<>();
			for (String f : new String[]{"airain_catwalk_drawbridge", "airain_catwalk_telescopic"})
				for (DeferredBlock<Block>[] t : FAMILLES.get(f)) for (DeferredBlock<Block> x : t) b.add(x.get());
			return net.minecraft.world.level.block.entity.BlockEntityType.Builder.of((p, s) -> new PasserelleMobile.Mecanisme(Passerelles.MOBILE_BE.get(), p, s), b.toArray(new Block[0])).build(null);
		});

	public static void charger() {}
}
