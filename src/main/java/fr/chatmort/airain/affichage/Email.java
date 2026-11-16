package fr.chatmort.airain.affichage;

import com.simibubi.create.api.behaviour.display.DisplaySource;
import com.simibubi.create.api.behaviour.display.DisplayTarget;
import com.simibubi.create.api.registry.CreateRegistries;
import fr.chatmort.airain.AirainMod;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** 1.60 : enregistrement du tableau émaillé, de sa cible de liaison d'affichage et de la source « moulage de canon ». */
public final class Email {
	private Email() {}

	public static final DeferredBlock<EmailBlock> BLOC = AirainMod.BLOCKS.register("enamel_board", () -> new EmailBlock(
		BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(2f, 6f).sound(SoundType.COPPER).noOcclusion()
			.lightLevel(s -> s.getValue(EmailBlock.LUMIERE)).isRedstoneConductor((a, b, c) -> false).isSuffocating((a, b, c) -> false).isViewBlocking((a, b, c) -> false)));
	static { AirainMod.ITEMS.register("enamel_board", () -> new BlockItem(BLOC.get(), new Item.Properties())); }
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<EmailBlockEntity>> BE = AirainMod.BLOCK_ENTITIES.register("enamel_board",
		() -> BlockEntityType.Builder.of((p, s) -> new EmailBlockEntity(Email.BE.get(), p, s), BLOC.get()).build(null));

	public static final DeferredRegister<DisplayTarget> CIBLES = DeferredRegister.create(CreateRegistries.DISPLAY_TARGET, AirainMod.ID);
	public static final DeferredRegister<DisplaySource> SOURCES = DeferredRegister.create(CreateRegistries.DISPLAY_SOURCE, AirainMod.ID);
	public static final DeferredHolder<DisplayTarget, CibleEmail> CIBLE = CIBLES.register("enamel_board", CibleEmail::new);
	public static final DeferredHolder<DisplaySource, SourceMoulage> MOULAGE = SOURCES.register("cannon_casting", SourceMoulage::new);

	public static void charger(IEventBus bus) { CIBLES.register(bus); SOURCES.register(bus); }

	/** À la mise en route (après les registres) : la cible sur le bloc, la source sur le moule de Big Cannons s'il est là. */
	public static void associer() {
		DisplayTarget.BY_BLOCK.register(BLOC.get(), CIBLE.get());
		var moule = BuiltInRegistries.BLOCK_ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath("createbigcannons", "cannon_cast"));
		if (moule != null) DisplaySource.BY_BLOCK_ENTITY.add(moule, MOULAGE.get());
	}
}
