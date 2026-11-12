package fr.chatmort.airain.fusion;

import fr.chatmort.airain.AirainMod;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * L'Écho liquide : la source d'Ars Nouveau condensée (1 mB = 1 de source). Il passe dans les tuyaux, pompes et réservoirs
 * de Create ; le bec verseur l'utilise pour imprégner les objets. Rendu : la texture de source d'Ars, teintée de violet.
 */
public final class EchoLiquide {
	private EchoLiquide() {}

	public static final DeferredRegister<FluidType> TYPES = DeferredRegister.create(NeoForgeRegistries.Keys.FLUID_TYPES, AirainMod.ID);
	public static final DeferredRegister<Fluid> FLUIDES = DeferredRegister.create(net.minecraft.core.registries.Registries.FLUID, AirainMod.ID);

	public static final DeferredHolder<FluidType, FluidType> TYPE = TYPES.register("liquid_echo", () -> new FluidType(FluidType.Properties.create()
		.descriptionId("fluid.airain.liquid_echo").lightLevel(10).density(800).viscosity(800).canDrown(true).canSwim(true)));

	public static final DeferredHolder<Fluid, FlowingFluid> SOURCE = FLUIDES.register("liquid_echo", () -> new BaseFlowingFluid.Source(proprietes()));
	public static final DeferredHolder<Fluid, FlowingFluid> COULANT = FLUIDES.register("flowing_liquid_echo", () -> new BaseFlowingFluid.Flowing(proprietes()));

	public static final net.neoforged.neoforge.registries.DeferredBlock<LiquidBlock> BLOC = AirainMod.BLOCKS.register("liquid_echo",
		() -> new LiquidBlock(SOURCE.get(), BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).replaceable().noCollission()
			.strength(100f).noLootTable().liquid().lightLevel(s -> 10)));
	public static final net.neoforged.neoforge.registries.DeferredItem<Item> SEAU = AirainMod.ITEMS.register("liquid_echo_bucket",
		() -> new BucketItem(SOURCE.get(), new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));

	private static BaseFlowingFluid.Properties proprietes() {
		return new BaseFlowingFluid.Properties(TYPE, SOURCE, COULANT).bucket(SEAU).block(BLOC).slopeFindDistance(2).levelDecreasePerBlock(2);
	}
}
