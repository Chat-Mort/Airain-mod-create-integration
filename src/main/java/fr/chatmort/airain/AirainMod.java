package fr.chatmort.airain;

import com.simibubi.create.api.stress.BlockStressValues;

import fr.chatmort.airain.banc.BancEntretienBlock;
import fr.chatmort.airain.banc.BancEntretienBlockEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * L'Empire d'Airain : intégration Create.
 * Ajoute le banc d'entretien, une machine Create qui répare l'équipement avec de l'huile au lieu de l'expérience.
 */
@Mod(AirainMod.ID)
public class AirainMod {
	public static final String ID = "airain";

	public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ID);
	public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ID);
	public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, ID);

	public static final DeferredBlock<BancEntretienBlock> BANC = BLOCKS.register("banc_entretien",
		() -> new BancEntretienBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_ORANGE)
			.strength(3f, 6f)
			.requiresCorrectToolForDrops()
			.sound(SoundType.COPPER)
			.noOcclusion()));

	public static final DeferredItem<BlockItem> BANC_ITEM = ITEMS.register("banc_entretien",
		() -> new BlockItem(BANC.get(), new Item.Properties()));

	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<BancEntretienBlockEntity>> BANC_BE =
		BLOCK_ENTITIES.register("banc_entretien",
			() -> BlockEntityType.Builder.of(BancEntretienBlockEntity::new, BANC.get()).build(null));

	public AirainMod(IEventBus bus) {
		BLOCKS.register(bus);
		ITEMS.register(bus);
		BLOCK_ENTITIES.register(bus);
		bus.addListener(this::setup);
		bus.addListener(this::capacites);
		bus.addListener(this::ongletCreatif);
	}

	private void setup(FMLCommonSetupEvent event) {
		// Impact de stress à 1 tr/min, comme la presse mécanique
		event.enqueueWork(() -> BlockStressValues.IMPACTS.register(BANC.get(), () -> 8.0));
	}

	private void capacites(RegisterCapabilitiesEvent event) {
		event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, BANC_BE.get(), (be, side) -> be.automatisation);
		event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, BANC_BE.get(), (be, side) -> be.reservoir);
	}

	private void ongletCreatif(BuildCreativeModeTabContentsEvent event) {
		if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS)
			event.accept(BANC_ITEM.get());
	}
}
