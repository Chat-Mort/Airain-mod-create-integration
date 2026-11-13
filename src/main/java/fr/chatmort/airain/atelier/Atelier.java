package fr.chatmort.airain.atelier;

import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.fonderie.BlocsAirain;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.UnaryOperator;

/**
 * Enregistrement des pièces d'atelier (1.51) : tuyauterie, lampes, plancher technique, toboggan, réverbère (familles
 * qui se patinent : 4 teintes × patinable/cirée), et manomètre, gyrophare, établi, plaques, bornes (airain poli).
 */
public final class Atelier {
	private Atelier() {}

	private static final WeatherState[] ETATS = {WeatherState.UNAFFECTED, WeatherState.EXPOSED, WeatherState.WEATHERED, WeatherState.OXIDIZED};
	private static final MapColor[] COULEURS = {MapColor.GOLD, MapColor.TERRACOTTA_YELLOW, MapColor.TERRACOTTA_ORANGE, MapColor.TERRACOTTA_RED};
	public static final Map<String, DeferredBlock<Block>[][]> FAMILLES = new LinkedHashMap<>();
	private interface Fabrique { Block creer(WeatherState etat, BlockBehaviour.Properties p); }

	private static BlockBehaviour.Properties base(MapColor c) {
		return BlockBehaviour.Properties.of().mapColor(c).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
			.isValidSpawn((a, b, cc, d) -> false).isRedstoneConductor((a, b, cc) -> false).isSuffocating((a, b, cc) -> false).isViewBlocking((a, b, cc) -> false);
	}
	@SuppressWarnings("unchecked")
	private static void famille(String nom, Fabrique f, UnaryOperator<BlockBehaviour.Properties> retouche) {
		DeferredBlock<Block>[][] t = new DeferredBlock[4][2];
		for (int s = 0; s < 4; s++)
			for (int c = 0; c < 2; c++) {
				final int st = s; final boolean cire = c == 1;
				String id = (cire ? "waxed_" : "") + BlocsAirain.STADES[s] + nom;
				DeferredBlock<Block> b = AirainMod.BLOCKS.register(id, () -> f.creer(cire ? null : ETATS[st], retouche.apply(base(COULEURS[st]))));
				AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
				t[s][c] = b;
			}
		FAMILLES.put(nom, t);
	}
	/** Le bloc neuf (non patiné, non ciré) d'une famille. */
	public static Block bloc(String famille) { return FAMILLES.get(famille)[0][0].get(); }

	static {
		famille("airain_pipe", Tuyaux.Tuyau::new, p -> p);
		famille("airain_pipe_valve", Tuyaux.Vanne::new, p -> p);
		famille("airain_pendant_lamp", Lampes.Suspension::new, p -> p.lightLevel(s -> 15));
		famille("airain_wall_lamp", Lampes.Applique::new, p -> p.lightLevel(s -> 14));
		famille("airain_raised_floor", PlancherTechnique::new, p -> p);
		famille("airain_chute", Toboggan::new, p -> p.friction(0.98f));
		famille("airain_lamppost", Reverbere::new, p -> p.lightLevel(s -> s.getValue(Reverbere.HAUT) ? 15 : 0));
	}
	private static <B extends Block> DeferredBlock<B> simple(String id, java.util.function.Function<BlockBehaviour.Properties, B> f, UnaryOperator<BlockBehaviour.Properties> retouche) {
		DeferredBlock<B> b = AirainMod.BLOCKS.register(id, () -> f.apply(retouche.apply(base(MapColor.GOLD))));
		AirainMod.ITEMS.register(id, () -> new BlockItem(b.get(), new Item.Properties()));
		return b;
	}
	public static final DeferredBlock<Manometre> MANOMETRE = simple("airain_gauge", Manometre::new, p -> p.noCollission());
	public static final DeferredBlock<Lampes.Gyrophare> GYROPHARE = simple("airain_beacon_light", Lampes.Gyrophare::new, p -> p.lightLevel(s -> s.getValue(BlockStateProperties.LIT) ? 15 : 0));
	public static final DeferredBlock<Etabli> ETABLI = simple("airain_workbench", Etabli::new, p -> p);
	public static final DeferredBlock<Plaque> PLAQUE = simple("airain_sign_plate", Plaque::new, p -> p.noCollission().strength(1.5f, 6f));
	public static final DeferredBlock<Borne> BORNE = simple("airain_signpost", Borne::new, p -> p);

	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Manometre.ManometreBlockEntity>> MANOMETRE_BE = AirainMod.BLOCK_ENTITIES.register("airain_gauge",
		() -> BlockEntityType.Builder.of(Manometre.ManometreBlockEntity::new, MANOMETRE.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Lampes.GyrophareBlockEntity>> GYROPHARE_BE = AirainMod.BLOCK_ENTITIES.register("airain_beacon_light",
		() -> BlockEntityType.Builder.of(Lampes.GyrophareBlockEntity::new, GYROPHARE.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Etabli.EtabliBlockEntity>> ETABLI_BE = AirainMod.BLOCK_ENTITIES.register("airain_workbench",
		() -> BlockEntityType.Builder.of(Etabli.EtabliBlockEntity::new, ETABLI.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Borne.BorneBlockEntity>> BORNE_BE = AirainMod.BLOCK_ENTITIES.register("airain_signpost",
		() -> BlockEntityType.Builder.of(Borne.BorneBlockEntity::new, BORNE.get()).build(null));
	public static final DeferredHolder<MenuType<?>, MenuType<EtabliMenu>> ETABLI_MENU = AirainMod.MENUS.register("airain_workbench",
		() -> IMenuTypeExtension.create(EtabliMenu::new));

	public static void charger() {}
}
