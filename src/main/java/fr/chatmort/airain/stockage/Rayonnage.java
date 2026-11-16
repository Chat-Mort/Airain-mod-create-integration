package fr.chatmort.airain.stockage;

import com.simibubi.create.api.behaviour.display.DisplaySource;
import com.simibubi.create.api.registry.CreateRegistries;
import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** 1.62 : enregistrement du rayonnage impérial (casier, renforts, source « stock du rayonnage »). */
public final class Rayonnage {
	private Rayonnage() {}
	public static final DeferredBlock<CasierBlock> CASIER = AirainMod.BLOCKS.register("airain_rack", () -> new CasierBlock(
		BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(3f, 6f).sound(SoundType.COPPER).noOcclusion().requiresCorrectToolForDrops()
			.isRedstoneConductor((a, b, c) -> false).isSuffocating((a, b, c) -> false).isViewBlocking((a, b, c) -> false)));
	static { AirainMod.ITEMS.register("airain_rack", () -> new CasierItem(CASIER.get(), new Item.Properties())); }
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<CasierBlockEntity>> BE = AirainMod.BLOCK_ENTITIES.register("airain_rack",
		() -> BlockEntityType.Builder.of((p, s) -> new CasierBlockEntity(Rayonnage.BE.get(), p, s), CASIER.get()).build(null));
	public static final DeferredItem<RenfortItem> RENFORT_1 = AirainMod.ITEMS.register("rack_reinforcement_1", () -> new RenfortItem(1, new Item.Properties()));
	public static final DeferredItem<RenfortItem> RENFORT_2 = AirainMod.ITEMS.register("rack_reinforcement_2", () -> new RenfortItem(2, new Item.Properties()));
	public static final DeferredItem<RenfortItem> RENFORT_3 = AirainMod.ITEMS.register("rack_reinforcement_3", () -> new RenfortItem(3, new Item.Properties()));
	public static final DeferredItem<RenfortItem> RENFORT_4 = AirainMod.ITEMS.register("rack_reinforcement_4", () -> new RenfortItem(4, new Item.Properties().fireResistant()));

	public static final DeferredRegister<DisplaySource> SOURCES = DeferredRegister.create(CreateRegistries.DISPLAY_SOURCE, AirainMod.ID);
	public static final DeferredHolder<DisplaySource, SourceStock> STOCK = SOURCES.register("rack_stock", SourceStock::new);

	public static void charger(IEventBus bus) { SOURCES.register(bus); }
	public static void associer() { DisplaySource.BY_BLOCK.add(CASIER.get(), STOCK.get()); }
}
