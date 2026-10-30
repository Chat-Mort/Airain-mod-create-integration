package fr.chatmort.airain;

import com.simibubi.create.api.stress.BlockStressValues;

import fr.chatmort.airain.banc.BancEntretienBlock;
import fr.chatmort.airain.banc.BancEntretienBlockEntity;
import fr.chatmort.airain.enchant.DesenchanteurBlock;
import fr.chatmort.airain.enchant.DesenchanteurBlockEntity;
import fr.chatmort.airain.enchant.TableEmpireBlock;
import fr.chatmort.airain.enchant.TableEmpireBlockEntity;
import fr.chatmort.airain.enchant.TableEmpireMenu;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
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
	public static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, ID);
	public static final DeferredRegister<net.minecraft.world.item.CreativeModeTab> ONGLETS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ID);

	/** Un seul onglet créatif pour tout l'Empire : les objets du mod, puis ceux du pack (KubeJS). */
	public static final DeferredHolder<net.minecraft.world.item.CreativeModeTab, net.minecraft.world.item.CreativeModeTab> ONGLET = ONGLETS.register("empire",
		() -> net.minecraft.world.item.CreativeModeTab.builder()
			.title(Component.translatable("itemGroup.airain.empire"))
			.icon(() -> new net.minecraft.world.item.ItemStack(AirainMod.FONDATION_ITEM.get()))
			.displayItems((params, sortie) -> {
				for (var h : ITEMS.getEntries()) sortie.accept(h.get());
				for (var e : net.minecraft.core.registries.BuiltInRegistries.ITEM.entrySet())
					if (e.getKey().location().getNamespace().equals("kubejs")) sortie.accept(e.getValue());
			}).build());

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

	// ---- enchantement : table de l'Empire et désenchanteur
	public static final DeferredBlock<TableEmpireBlock> TABLE = BLOCKS.register("table_enchantement",
		() -> new TableEmpireBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_ORANGE).strength(5f, 1200f).requiresCorrectToolForDrops().sound(SoundType.COPPER)
			.lightLevel(s -> 7).noOcclusion()));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TableEmpireBlockEntity>> TABLE_BE =
		BLOCK_ENTITIES.register("table_enchantement",
			() -> BlockEntityType.Builder.of(TableEmpireBlockEntity::new, TABLE.get()).build(null));
	public static final DeferredItem<BlockItem> TABLE_ITEM = ITEMS.register("table_enchantement",
		() -> new BlockItem(TABLE.get(), new Item.Properties()));
	public static final DeferredHolder<MenuType<?>, MenuType<fr.chatmort.airain.banc.BancMenu>> BANC_MENU = MENUS.register("banc_entretien",
		() -> IMenuTypeExtension.create(fr.chatmort.airain.banc.BancMenu::new));
	/** Modules du banc d'entretien. */
	public static final DeferredItem<Item> MEULE_FINE = ITEMS.register("meule_fine", () -> new Item(new Item.Properties().stacksTo(1)));
	public static final DeferredItem<Item> DEMULTIPLICATEUR = ITEMS.register("demultiplicateur", () -> new Item(new Item.Properties().stacksTo(1)));
	public static final DeferredItem<Item> GRAISSEUR = ITEMS.register("graisseur", () -> new Item(new Item.Properties().stacksTo(1)));
	public static final DeferredHolder<MenuType<?>, MenuType<TableEmpireMenu>> TABLE_MENU = MENUS.register("table_enchantement",
		() -> IMenuTypeExtension.create(TableEmpireMenu::new));

	public static final DeferredBlock<DesenchanteurBlock> DESENCH = BLOCKS.register("desenchanteur",
		() -> new DesenchanteurBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_PURPLE).strength(3f, 6f).requiresCorrectToolForDrops().sound(SoundType.COPPER).noOcclusion()));
	/** Socle de l'Empire : expose un trophée de boss, effet permanent pour toute l'équipe. */
	public static final DeferredBlock<fr.chatmort.airain.trophee.SocleBlock> SOCLE = BLOCKS.register("socle_trophee",
		() -> new fr.chatmort.airain.trophee.SocleBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.GOLD).strength(3f, 9f).requiresCorrectToolForDrops().sound(SoundType.METAL).noOcclusion()
			.lightLevel(s -> s.getValue(fr.chatmort.airain.trophee.SocleBlock.LUMIERE) ? 12 : 0)));
	public static final DeferredItem<BlockItem> SOCLE_ITEM = ITEMS.register("socle_trophee",
		() -> new BlockItem(SOCLE.get(), new Item.Properties()));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.trophee.SocleBlockEntity>> SOCLE_BE =
		BLOCK_ENTITIES.register("socle_trophee",
			() -> BlockEntityType.Builder.of(fr.chatmort.airain.trophee.SocleBlockEntity::new, SOCLE.get()).build(null));

	/** Pierre de fondation : nomme une base, titre à l'écran en entrant dans sa zone. */
	public static final DeferredBlock<fr.chatmort.airain.fondation.FondationBlock> FONDATION = BLOCKS.register("pierre_fondation",
		() -> new fr.chatmort.airain.fondation.FondationBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.STONE).strength(2.5f, 9f).requiresCorrectToolForDrops().sound(SoundType.STONE).noOcclusion()));
	public static final DeferredItem<BlockItem> FONDATION_ITEM = ITEMS.register("pierre_fondation",
		() -> new BlockItem(FONDATION.get(), new Item.Properties()));
	/** Grand étendard : même piédestal, mât de six blocs, bannière réglable en taille. */
	public static final DeferredBlock<fr.chatmort.airain.fondation.GrandEtendardBlock> GRAND_ETENDARD = BLOCKS.register("grand_etendard",
		() -> new fr.chatmort.airain.fondation.GrandEtendardBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.STONE).strength(2.5f, 9f).requiresCorrectToolForDrops().sound(SoundType.STONE).noOcclusion()));
	public static final DeferredItem<BlockItem> GRAND_ETENDARD_ITEM = ITEMS.register("grand_etendard",
		() -> new BlockItem(GRAND_ETENDARD.get(), new Item.Properties()));
	/** Bannière murale : décorative, mêmes réglages de toile. */
	public static final DeferredBlock<fr.chatmort.airain.fondation.BanniereMuraleBlock> BANNIERE_MURALE = BLOCKS.register("banniere_murale",
		() -> new fr.chatmort.airain.fondation.BanniereMuraleBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOL).strength(0.8f).sound(SoundType.WOOL).noOcclusion().noCollission()));
	public static final DeferredItem<BlockItem> BANNIERE_MURALE_ITEM = ITEMS.register("banniere_murale",
		() -> new BlockItem(BANNIERE_MURALE.get(), new Item.Properties()));
	/** Gabarit de bannière : copie l'apparence d'un étendard pour l'appliquer à un autre. */
	public static final DeferredItem<Item> GABARIT = ITEMS.register("gabarit_banniere",
		() -> new fr.chatmort.airain.fondation.GabaritItem(new Item.Properties().stacksTo(1)));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.fondation.FondationBlockEntity>> FONDATION_BE =
		BLOCK_ENTITIES.register("pierre_fondation",
			() -> BlockEntityType.Builder.of(fr.chatmort.airain.fondation.FondationBlockEntity::new, FONDATION.get(), GRAND_ETENDARD.get(), BANNIERE_MURALE.get()).build(null));
	/** Balise de défense : tour-phare à sirène de 3 x 3 x 8 ; lance les assauts de l'Empire (logique : airain_balise.js). */
	public static final DeferredBlock<fr.chatmort.airain.balise.BaliseBlock> BALISE = BLOCKS.register("balise_defense",
		() -> new fr.chatmort.airain.balise.BaliseBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.METAL).strength(5f, 1200f).sound(SoundType.METAL).noOcclusion()));
	public static final DeferredBlock<fr.chatmort.airain.balise.BalisePartieBlock> BALISE_PARTIE = BLOCKS.register("balise_partie",
		() -> new fr.chatmort.airain.balise.BalisePartieBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.METAL).strength(5f, 1200f).sound(SoundType.METAL).noOcclusion().noLootTable()
			.lightLevel(s -> s.getValue(fr.chatmort.airain.balise.BalisePartieBlock.LUMIERE) ? 15 : 0)));
	public static final DeferredItem<BlockItem> BALISE_ITEM = ITEMS.register("balise_defense",
		() -> new BlockItem(BALISE.get(), new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.RARE)));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.balise.BaliseBlockEntity>> BALISE_BE =
		BLOCK_ENTITIES.register("balise_defense",
			() -> BlockEntityType.Builder.of(fr.chatmort.airain.balise.BaliseBlockEntity::new, BALISE.get()).build(null));

	/** Codex de l'Empire : une page par créature, ouverte en combattant. */
	public static final DeferredItem<Item> CODEX = ITEMS.register("codex",
		() -> new fr.chatmort.airain.codex.CodexItem(new Item.Properties().stacksTo(1)));
	public static final DeferredItem<Item> REGISTRE = ITEMS.register("registre_fondations",
		() -> new fr.chatmort.airain.fondation.RegistreItem(new Item.Properties().stacksTo(1)));

	/** Encre runique : consommée quand la table applique le niveau ouvert par un tome ancien. */
	public static final DeferredItem<Item> ENCRE = ITEMS.register("encre_runique",
		() -> new Item(new Item.Properties().rarity(net.minecraft.world.item.Rarity.RARE)));
	public static final DeferredItem<BlockItem> DESENCH_ITEM = ITEMS.register("desenchanteur",
		() -> new BlockItem(DESENCH.get(), new Item.Properties()));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<DesenchanteurBlockEntity>> DESENCH_BE =
		BLOCK_ENTITIES.register("desenchanteur",
			() -> BlockEntityType.Builder.of(DesenchanteurBlockEntity::new, DESENCH.get()).build(null));

	public AirainMod(IEventBus bus) {
		BLOCKS.register(bus);
		ITEMS.register(bus);
		BLOCK_ENTITIES.register(bus);
		MENUS.register(bus);
		NeoForge.EVENT_BUS.addListener(this::tableVanilla);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::chute);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.fondation.Fondations::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.codex.Codex::mort);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.banc.Affutage::vitesse);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.banc.Affutage::degats);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.banc.Affutage::infobulle);
		bus.addListener((net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent e) -> e.registrar("1")
			.playToServer(fr.chatmort.airain.trophee.ConfigurerSocle.TYPE, fr.chatmort.airain.trophee.ConfigurerSocle.CODEC,
				fr.chatmort.airain.trophee.ConfigurerSocle::traiter)
			.playToServer(fr.chatmort.airain.fondation.ConfigurerFondation.TYPE, fr.chatmort.airain.fondation.ConfigurerFondation.CODEC,
				fr.chatmort.airain.fondation.ConfigurerFondation::traiter)
			.playToClient(fr.chatmort.airain.fondation.TitreFondation.TYPE, fr.chatmort.airain.fondation.TitreFondation.CODEC,
				(m, ctx) -> fr.chatmort.airain.fondation.HudFondation.recevoir(m, ctx))
			.playToClient(fr.chatmort.airain.codex.OuvrirCodex.TYPE, fr.chatmort.airain.codex.OuvrirCodex.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.codex(m)))
			.playToClient(fr.chatmort.airain.fondation.OuvrirRegistre.TYPE, fr.chatmort.airain.fondation.OuvrirRegistre.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.registre(m))));
		bus.addListener(this::setup);
		bus.addListener(this::capacites);
		ONGLETS.register(bus);
	}

	private void setup(FMLCommonSetupEvent event) {
		// Impact de stress à 1 tr/min, comme la presse mécanique
		event.enqueueWork(() -> {
			BlockStressValues.IMPACTS.register(BANC.get(), () -> 8.0);
			BlockStressValues.IMPACTS.register(DESENCH.get(), () -> 8.0);
		});
	}

	private void capacites(RegisterCapabilitiesEvent event) {
		event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, BANC_BE.get(), (be, side) -> be.automatisation);
		event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, BANC_BE.get(), (be, side) -> be.reservoir);
		event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, DESENCH_BE.get(), (be, side) -> be.automatisation);
		event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, DESENCH_BE.get(), (be, side) -> be.reservoir);
	}

	/** La table d'enchantement vanilla ne s'ouvre plus : c'est la table de l'Empire qui enchante. */
	private void tableVanilla(PlayerInteractEvent.RightClickBlock event) {
		if (!event.getLevel().getBlockState(event.getPos()).is(Blocks.ENCHANTING_TABLE))
			return;
		if (event.getEntity().isShiftKeyDown() && !event.getItemStack().isEmpty())
			return;   // laisser poser un bloc contre la table
		event.setCanceled(true);
		event.setCancellationResult(InteractionResult.SUCCESS);
		if (!event.getLevel().isClientSide)
			event.getEntity().displayClientMessage(Component.translatable("airain.table.vanilla_bloquee"), true);
	}
}
