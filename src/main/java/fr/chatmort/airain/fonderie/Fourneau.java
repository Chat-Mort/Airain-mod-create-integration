package fr.chatmort.airain.fonderie;

import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

/** Enregistrement des blocs du haut-fourneau impérial. */
public final class Fourneau {
	private Fourneau() {}

	private static BlockBehaviour.Properties briques() {
		return BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_RED).requiresCorrectToolForDrops().strength(3.5f, 9f).sound(SoundType.NETHER_BRICKS);
	}
	public static final DeferredBlock<FourneauBlocs.Briques> BRIQUES = AirainMod.BLOCKS.register("fire_bricks", () -> new FourneauBlocs.Briques(briques()));
	public static final DeferredBlock<FourneauBlocs.Tuyere> TUYERE = AirainMod.BLOCKS.register("blast_furnace_tuyere", () -> new FourneauBlocs.Tuyere(briques()));
	public static final DeferredBlock<FourneauBlocs.Gueulard> GUEULARD = AirainMod.BLOCKS.register("blast_furnace_hopper",
		() -> new FourneauBlocs.Gueulard(briques().noOcclusion().lightLevel(s -> s.getValue(FourneauBlocs.LIT) ? 12 : 0)));
	public static final DeferredBlock<FourneauBlocs.TrouCoulee> TROU = AirainMod.BLOCKS.register("blast_furnace_taphole",
		() -> new FourneauBlocs.TrouCoulee(briques().noOcclusion().lightLevel(s -> s.getValue(FourneauBlocs.LIT) ? 13 : 0)));
	static {
		AirainMod.ITEMS.register("fire_bricks", () -> new BlockItem(BRIQUES.get(), new Item.Properties()));
		AirainMod.ITEMS.register("blast_furnace_tuyere", () -> new BlockItem(TUYERE.get(), new Item.Properties()));
		AirainMod.ITEMS.register("blast_furnace_hopper", () -> new BlockItem(GUEULARD.get(), new Item.Properties()));
		AirainMod.ITEMS.register("blast_furnace_taphole", () -> new BlockItem(TROU.get(), new Item.Properties()));
	}
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<HautFourneauBlockEntity>> BE = AirainMod.BLOCK_ENTITIES.register("blast_furnace",
		() -> BlockEntityType.Builder.of(HautFourneauBlockEntity::new, TROU.get()).build(null));

	public static void charger() {}
}
