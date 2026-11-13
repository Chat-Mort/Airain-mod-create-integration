package fr.chatmort.airain.fonderie;

import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.neoforge.common.SoundActions;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * L'airain, alliage secret de l'Empire : lingot, pépite, plaque, engrenage, laitier, brique réfractaire,
 * et l'airain en fusion (90 mB = un lingot), qui ne sort que du haut-fourneau.
 */
public final class MetalAirain {
	private MetalAirain() {}

	public static final DeferredItem<Item> LINGOT = AirainMod.ITEMS.register("airain_ingot", () -> new Item(new Item.Properties()));
	public static final DeferredItem<Item> PEPITE = AirainMod.ITEMS.register("airain_nugget", () -> new Item(new Item.Properties()));
	public static final DeferredItem<Item> PLAQUE = AirainMod.ITEMS.register("airain_sheet", () -> new Item(new Item.Properties()));
	public static final DeferredItem<Item> ENGRENAGE = AirainMod.ITEMS.register("airain_gear", () -> new Item(new Item.Properties()));
	// engrenage en cours d'assemblage (assemblage séquencé de Create)
	public static final DeferredItem<Item> ENGRENAGE_INACHEVE = AirainMod.ITEMS.register("incomplete_airain_gear",
		() -> new com.simibubi.create.content.processing.sequenced.SequencedAssemblyItem(new Item.Properties()));
	public static final DeferredItem<Item> LAITIER = AirainMod.ITEMS.register("slag", () -> new Item(new Item.Properties()));
	public static final DeferredItem<Item> BRIQUE = AirainMod.ITEMS.register("fire_brick", () -> new Item(new Item.Properties()));

	// ---- airain en fusion
	public static final DeferredRegister<FluidType> TYPES = DeferredRegister.create(NeoForgeRegistries.Keys.FLUID_TYPES, AirainMod.ID);
	public static final DeferredRegister<Fluid> FLUIDES = DeferredRegister.create(net.minecraft.core.registries.Registries.FLUID, AirainMod.ID);
	public static final DeferredHolder<FluidType, FluidType> TYPE = TYPES.register("molten_airain", () -> new FluidType(FluidType.Properties.create()
		.descriptionId("fluid.airain.molten_airain").lightLevel(15).density(3000).viscosity(6000).temperature(1300)
		.canSwim(false).canDrown(false).supportsBoating(false).canHydrate(false)
		.sound(SoundActions.BUCKET_FILL, net.minecraft.sounds.SoundEvents.BUCKET_FILL_LAVA)
		.sound(SoundActions.BUCKET_EMPTY, net.minecraft.sounds.SoundEvents.BUCKET_EMPTY_LAVA)));
	public static final DeferredHolder<Fluid, FlowingFluid> SOURCE = FLUIDES.register("molten_airain", () -> new BaseFlowingFluid.Source(proprietes()));
	public static final DeferredHolder<Fluid, FlowingFluid> COULANT = FLUIDES.register("flowing_molten_airain", () -> new BaseFlowingFluid.Flowing(proprietes()));
	public static final DeferredBlock<LiquidBlock> BLOC_FUSION = AirainMod.BLOCKS.register("molten_airain",
		() -> new LiquidBlock(SOURCE.get(), BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).replaceable().noCollission()
			.strength(100f).noLootTable().liquid().pushReaction(PushReaction.DESTROY).lightLevel(s -> 15)));
	public static final DeferredItem<Item> SEAU = AirainMod.ITEMS.register("molten_airain_bucket",
		() -> new BucketItem(SOURCE.get(), new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));

	private static BaseFlowingFluid.Properties proprietes() {
		return new BaseFlowingFluid.Properties(TYPE, SOURCE, COULANT).bucket(SEAU).block(BLOC_FUSION)
			.slopeFindDistance(2).levelDecreasePerBlock(2).tickRate(30);
	}

	/** Force le chargement de la classe (ses objets rejoignent ITEMS et BLOCKS avant leur enregistrement). */
	public static void charger() {}
}
