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
 */
@Mod(AirainMod.ID)
public class AirainMod {
	public static final String ID = "airain";

	public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ID);
	public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ID);
	public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, ID);
	public static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, ID);
	public static final DeferredRegister<net.minecraft.world.item.CreativeModeTab> ONGLETS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ID);

	/** Regroupement des items mod + KubeJS dans un seul onglet créa */
	public static final DeferredHolder<net.minecraft.world.item.CreativeModeTab, net.minecraft.world.item.CreativeModeTab> ONGLET = ONGLETS.register("empire",
		() -> net.minecraft.world.item.CreativeModeTab.builder()
			.title(Component.translatable("itemGroup.airain.empire"))
			.icon(() -> new net.minecraft.world.item.ItemStack(AirainMod.FONDATION_ITEM.get()))
			.displayItems((params, sortie) -> {
				for (var h : ITEMS.getEntries()) sortie.accept(h.get());
				for (var e : net.minecraft.core.registries.BuiltInRegistries.ITEM.entrySet())
					if (e.getKey().location().getNamespace().equals("kubejs")) sortie.accept(e.getValue());
			}).build());

	public static final DeferredBlock<BancEntretienBlock> BANC = BLOCKS.register("maintenance_bench",
		() -> new BancEntretienBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_ORANGE)
			.strength(3f, 6f)
			.requiresCorrectToolForDrops()
			.sound(SoundType.COPPER)
			.noOcclusion()));

	public static final DeferredItem<BlockItem> BANC_ITEM = ITEMS.register("maintenance_bench",
		() -> new BlockItem(BANC.get(), new Item.Properties()));

	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<BancEntretienBlockEntity>> BANC_BE =
		BLOCK_ENTITIES.register("maintenance_bench",
			() -> BlockEntityType.Builder.of(BancEntretienBlockEntity::new, BANC.get()).build(null));

	// ---- table de l'Empire et désenchanteur
	public static final DeferredBlock<TableEmpireBlock> TABLE = BLOCKS.register("imperial_enchanting_table",
		() -> new TableEmpireBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_ORANGE).strength(5f, 1200f).requiresCorrectToolForDrops().sound(SoundType.COPPER)
			.lightLevel(s -> 7).noOcclusion()));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TableEmpireBlockEntity>> TABLE_BE =
		BLOCK_ENTITIES.register("imperial_enchanting_table",
			() -> BlockEntityType.Builder.of(TableEmpireBlockEntity::new, TABLE.get()).build(null));
	public static final DeferredItem<BlockItem> TABLE_ITEM = ITEMS.register("imperial_enchanting_table",
		() -> new BlockItem(TABLE.get(), new Item.Properties()));
	public static final DeferredHolder<MenuType<?>, MenuType<fr.chatmort.airain.banc.BancMenu>> BANC_MENU = MENUS.register("maintenance_bench",
		() -> IMenuTypeExtension.create(fr.chatmort.airain.banc.BancMenu::new));
	/** Modules du banc d'entretien. */
	public static final DeferredItem<Item> MEULE_FINE = ITEMS.register("fine_grindstone", () -> new Item(new Item.Properties().stacksTo(1)));
	public static final DeferredItem<Item> DEMULTIPLICATEUR = ITEMS.register("reduction_gear", () -> new Item(new Item.Properties().stacksTo(1)));
	public static final DeferredItem<Item> GRAISSEUR = ITEMS.register("grease_gun", () -> new Item(new Item.Properties().stacksTo(1)));
	public static final DeferredHolder<MenuType<?>, MenuType<TableEmpireMenu>> TABLE_MENU = MENUS.register("imperial_enchanting_table",
		() -> IMenuTypeExtension.create(TableEmpireMenu::new));

	public static final DeferredBlock<DesenchanteurBlock> DESENCH = BLOCKS.register("disenchanter",
		() -> new DesenchanteurBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_PURPLE).strength(3f, 6f).requiresCorrectToolForDrops().sound(SoundType.COPPER).noOcclusion()));
	/** Piédestal → trophé exposé = effet constant partout dans le monde */
	public static final DeferredBlock<fr.chatmort.airain.trophee.SocleBlock> SOCLE = BLOCKS.register("trophy_pedestal",
		() -> new fr.chatmort.airain.trophee.SocleBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.GOLD).strength(3f, 9f).requiresCorrectToolForDrops().sound(SoundType.METAL).noOcclusion()
			.lightLevel(s -> s.getValue(fr.chatmort.airain.trophee.SocleBlock.LUMIERE) ? 12 : 0)));
	public static final DeferredItem<BlockItem> SOCLE_ITEM = ITEMS.register("trophy_pedestal",
		() -> new BlockItem(SOCLE.get(), new Item.Properties()));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.trophee.SocleBlockEntity>> SOCLE_BE =
		BLOCK_ENTITIES.register("trophy_pedestal",
			() -> BlockEntityType.Builder.of(fr.chatmort.airain.trophee.SocleBlockEntity::new, SOCLE.get()).build(null));

	/** Étandard de fondation : crée et nomme une base, titre à l'écran en entrant dans sa zone. */
	public static final DeferredBlock<fr.chatmort.airain.fondation.FondationBlock> FONDATION = BLOCKS.register("foundation_stone",
		() -> new fr.chatmort.airain.fondation.FondationBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.STONE).strength(2.5f, 9f).requiresCorrectToolForDrops().sound(SoundType.STONE).noOcclusion()));
	public static final DeferredItem<BlockItem> FONDATION_ITEM = ITEMS.register("foundation_stone",
		() -> new BlockItem(FONDATION.get(), new Item.Properties()));
	/** Grand étendard : même piédestal, mât de 6 à 8 blocs, bannière réglable en taille. */
	public static final DeferredBlock<fr.chatmort.airain.fondation.GrandEtendardBlock> GRAND_ETENDARD = BLOCKS.register("great_standard",
		() -> new fr.chatmort.airain.fondation.GrandEtendardBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.STONE).strength(2.5f, 9f).requiresCorrectToolForDrops().sound(SoundType.STONE).noOcclusion()));
	public static final DeferredItem<BlockItem> GRAND_ETENDARD_ITEM = ITEMS.register("great_standard",
		() -> new BlockItem(GRAND_ETENDARD.get(), new Item.Properties()));
	/** Bannière murale : décorative, mêmes réglages de toile. */
	public static final DeferredBlock<fr.chatmort.airain.fondation.BanniereMuraleBlock> BANNIERE_MURALE = BLOCKS.register("foundation_wall_banner",
		() -> new fr.chatmort.airain.fondation.BanniereMuraleBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOL).strength(0.8f).sound(SoundType.WOOL).noOcclusion().noCollission()));
	public static final DeferredItem<BlockItem> BANNIERE_MURALE_ITEM = ITEMS.register("foundation_wall_banner",
		() -> new BlockItem(BANNIERE_MURALE.get(), new Item.Properties()));
	/** Gabarit de bannière : copie l'apparence d'un étendard pour l'appliquer à un autre. */
	public static final DeferredItem<Item> GABARIT = ITEMS.register("banner_template",
		() -> new fr.chatmort.airain.fondation.GabaritItem(new Item.Properties().stacksTo(1)));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.fondation.FondationBlockEntity>> FONDATION_BE =
		BLOCK_ENTITIES.register("foundation_stone",
			() -> BlockEntityType.Builder.of(fr.chatmort.airain.fondation.FondationBlockEntity::new, FONDATION.get(), GRAND_ETENDARD.get(), BANNIERE_MURALE.get()).build(null));
	/** Balise de défense : tour-phare à sirène de 3 x 3 x 8 ; lance les assauts de l'Empire (logique : airain_balise.js). */
	public static final DeferredBlock<fr.chatmort.airain.balise.BaliseBlock> BALISE = BLOCKS.register("defense_beacon",
		() -> new fr.chatmort.airain.balise.BaliseBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.METAL).strength(5f, 1200f).sound(SoundType.METAL).noOcclusion()));
	public static final DeferredBlock<fr.chatmort.airain.balise.BalisePartieBlock> BALISE_PARTIE = BLOCKS.register("defense_beacon_part",
		() -> new fr.chatmort.airain.balise.BalisePartieBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.METAL).strength(5f, 1200f).sound(SoundType.METAL).noOcclusion().noLootTable()
			.lightLevel(s -> s.getValue(fr.chatmort.airain.balise.BalisePartieBlock.LUMIERE) ? 15 : 0)));
	public static final DeferredItem<BlockItem> BALISE_ITEM = ITEMS.register("defense_beacon",
		() -> new BlockItem(BALISE.get(), new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.RARE)));
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.balise.BaliseBlockEntity>> BALISE_BE =
		BLOCK_ENTITIES.register("defense_beacon",
			() -> BlockEntityType.Builder.of(fr.chatmort.airain.balise.BaliseBlockEntity::new, BALISE.get()).build(null));

	/** Codex de l'Empire : une page par créature, ouverte en combattant. */
	public static final DeferredItem<Item> CODEX = ITEMS.register("codex",
		() -> new fr.chatmort.airain.codex.CodexItem(new Item.Properties().stacksTo(1)));
	/** Livre de l'ingénieur : le manuel des machines de l'Empire. */
	public static final DeferredItem<Item> LIVRE_INGENIEUR = ITEMS.register("engineers_manual",
		() -> new fr.chatmort.airain.ingenieur.LivreIngenieurItem(new Item.Properties().stacksTo(1)));
	// ---- gardiens d'airain et choix final
	public static final DeferredRegister<net.minecraft.world.entity.EntityType<?>> ENTITES = DeferredRegister.create(Registries.ENTITY_TYPE, ID);
	public static final DeferredRegister<net.minecraft.world.item.ArmorMaterial> MATERIAUX = DeferredRegister.create(Registries.ARMOR_MATERIAL, ID);
	public static final DeferredHolder<net.minecraft.world.entity.EntityType<?>, net.minecraft.world.entity.EntityType<fr.chatmort.airain.gardien.GardienEntity>> GARDIEN =
		ENTITES.register("guardian", () -> net.minecraft.world.entity.EntityType.Builder.<fr.chatmort.airain.gardien.GardienEntity>of(
			fr.chatmort.airain.gardien.GardienEntity::new, net.minecraft.world.entity.MobCategory.MISC)
			.sized(1.4f, 2.7f).clientTrackingRange(10).build("guardian"));
	public static final DeferredItem<Item> GARDIEN_OEUF = ITEMS.register("guardian_spawn_egg",
		() -> new net.neoforged.neoforge.common.DeferredSpawnEggItem(GARDIEN, 0xA8742C, 0x3A8C7A, new Item.Properties()));
	/** Couronne d'airain : récompense de « Rallumer le Cœur ». Portée seule, ou montée à l'enclume sur un casque de netherite. */
	private static net.minecraft.world.item.ArmorMaterial materiau(String couche, int casque, float robustesse, float recul, net.minecraft.world.item.Item reparation) {
		return new net.minecraft.world.item.ArmorMaterial(
			java.util.Map.of(net.minecraft.world.item.ArmorItem.Type.HELMET, casque, net.minecraft.world.item.ArmorItem.Type.CHESTPLATE, casque,
				net.minecraft.world.item.ArmorItem.Type.LEGGINGS, casque, net.minecraft.world.item.ArmorItem.Type.BOOTS, casque, net.minecraft.world.item.ArmorItem.Type.BODY, casque),
			15, net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_GOLD,
			() -> reparation == null ? net.minecraft.world.item.crafting.Ingredient.EMPTY : net.minecraft.world.item.crafting.Ingredient.of(reparation),
			java.util.List.of(new net.minecraft.world.item.ArmorMaterial.Layer(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(ID, couche))),
			robustesse, recul);
	}
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_COURONNE =
		MATERIAUX.register("crown", () -> materiau("crown", 2, 0f, 0f, null));
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_CASQUE =
		MATERIAUX.register("crowned_helmet", () -> materiau("crowned_helmet", 3, 3f, 0.1f, net.minecraft.world.item.Items.NETHERITE_INGOT));
	public static final DeferredItem<Item> COURONNE = ITEMS.register("airain_crown",
		() -> new fr.chatmort.airain.gardien.CouronneItem(AIRAIN_COURONNE, false, new Item.Properties()
			.stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)
			.component(net.minecraft.core.component.DataComponents.UNBREAKABLE, new net.minecraft.world.item.component.Unbreakable(false))));
	public static final DeferredRegister<net.minecraft.world.item.crafting.RecipeSerializer<?>> SERIALISEURS = DeferredRegister.create(Registries.RECIPE_SERIALIZER, ID);
	public static final DeferredHolder<net.minecraft.world.item.crafting.RecipeSerializer<?>, net.minecraft.world.item.crafting.RecipeSerializer<Monture>> MONTURE =
		SERIALISEURS.register("mount", () -> Monture.SERIALISEUR);
	/** Couronne sacrée : le casque couronné consacré par une plaque sacrée. */
	public static final DeferredItem<Item> CASQUE_COURONNE_SACREE = ITEMS.register("sacred_crown",
		() -> new fr.chatmort.airain.gardien.CouronneItem(AIRAIN_CASQUE, true, new Item.Properties()
			.stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.RARE)
			.durability(net.minecraft.world.item.ArmorItem.Type.HELMET.getDurability(37))));
	/** Trophées des boss avancés : trophée → boss. */
	public static final java.util.Map<String, DeferredItem<Item>> TROPHEES_BOSS = new java.util.LinkedHashMap<>();
	static {
		String[][] t = {{"colossus_visor", "mowziesmobs:ferrous_wroughtnaut"}, {"magma_heart", "cataclysm:netherite_monstrosity"},
			{"prowler_gear", "cataclysm:the_prowler"}, {"guardian_eye", "cataclysm:ender_guardian"}, {"centurion_seal", "mebahelcreaturesdwarven:dwarven_centurion"}};
		for (String[] x : t) {
			final String nom = x[0];
			TROPHEES_BOSS.put(x[1], ITEMS.register(nom, () -> new fr.chatmort.airain.trophee.TropheeItem(nom,
				new Item.Properties().stacksTo(16).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC))));
		}
	}
	public static final DeferredItem<Item> CASQUE_COURONNE = ITEMS.register("crowned_helmet",
		() -> new fr.chatmort.airain.gardien.CouronneItem(AIRAIN_CASQUE, true, new Item.Properties()
			.stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.RARE)
			.durability(net.minecraft.world.item.ArmorItem.Type.HELMET.getDurability(37))));

	/** Armures de l'Empire : sacrée (netherite + plaque sacrée) puis impériale (sacrée + plaque impériale). */
	private static net.minecraft.world.item.ArmorMaterial materiauArmure(String couche, int casque, int plastron, int jambieres, int bottes, float robustesse, float recul) {
		return new net.minecraft.world.item.ArmorMaterial(
			java.util.Map.of(net.minecraft.world.item.ArmorItem.Type.HELMET, casque, net.minecraft.world.item.ArmorItem.Type.CHESTPLATE, plastron,
				net.minecraft.world.item.ArmorItem.Type.LEGGINGS, jambieres, net.minecraft.world.item.ArmorItem.Type.BOOTS, bottes, net.minecraft.world.item.ArmorItem.Type.BODY, plastron),
			15, net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_NETHERITE,
			() -> net.minecraft.world.item.crafting.Ingredient.of(net.minecraft.world.item.Items.NETHERITE_INGOT),
			java.util.List.of(new net.minecraft.world.item.ArmorMaterial.Layer(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(ID, couche))),
			robustesse, recul);
	}
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_SACREE =
		MATERIAUX.register("sacred", () -> materiauArmure("sacred", 3, 9, 7, 3, 3.5f, 0.15f));
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_IMPERIALE =
		MATERIAUX.register("imperial", () -> materiauArmure("imperial", 4, 10, 8, 4, 4.5f, 0.2f));
	private static DeferredItem<Item> armure(String nom, net.minecraft.core.Holder<net.minecraft.world.item.ArmorMaterial> m,
			net.minecraft.world.item.ArmorItem.Type type, int palier) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.ArmureItem(m, type, palier, new Item.Properties().stacksTo(1).fireResistant()
			.rarity(palier == 2 ? net.minecraft.world.item.Rarity.EPIC : net.minecraft.world.item.Rarity.RARE)
			.durability(type.getDurability(palier == 2 ? 55 : 45))));
	}
	public static final DeferredItem<Item> PLASTRON_SACRE = armure("sacred_chestplate", AIRAIN_SACREE, net.minecraft.world.item.ArmorItem.Type.CHESTPLATE, 1);
	public static final DeferredItem<Item> JAMBIERES_SACREES = armure("sacred_leggings", AIRAIN_SACREE, net.minecraft.world.item.ArmorItem.Type.LEGGINGS, 1);
	public static final DeferredItem<Item> BOTTES_SACREES = armure("sacred_boots", AIRAIN_SACREE, net.minecraft.world.item.ArmorItem.Type.BOOTS, 1);
	public static final DeferredItem<Item> CASQUE_IMPERIAL = armure("imperial_helmet", AIRAIN_IMPERIALE, net.minecraft.world.item.ArmorItem.Type.HELMET, 2);
	public static final DeferredItem<Item> PLASTRON_IMPERIAL = armure("imperial_chestplate", AIRAIN_IMPERIALE, net.minecraft.world.item.ArmorItem.Type.CHESTPLATE, 2);
	public static final DeferredItem<Item> JAMBIERES_IMPERIALES = armure("imperial_leggings", AIRAIN_IMPERIALE, net.minecraft.world.item.ArmorItem.Type.LEGGINGS, 2);
	public static final DeferredItem<Item> BOTTES_IMPERIALES = armure("imperial_boots", AIRAIN_IMPERIALE, net.minecraft.world.item.ArmorItem.Type.BOOTS, 2);

	/** Armes et pioche sacrées / impériales. */
	private static net.minecraft.world.item.Tier palier(int usages, float vitesse) {
		return new net.minecraft.world.item.Tier() {
			public int getUses() { return usages; }
			public float getSpeed() { return vitesse; }
			public float getAttackDamageBonus() { return 0f; }
			public net.minecraft.tags.TagKey<net.minecraft.world.level.block.Block> getIncorrectBlocksForDrops() { return net.minecraft.tags.BlockTags.INCORRECT_FOR_NETHERITE_TOOL; }
			public int getEnchantmentValue() { return 15; }
			public net.minecraft.world.item.crafting.Ingredient getRepairIngredient() { return net.minecraft.world.item.crafting.Ingredient.of(net.minecraft.world.item.Items.NETHERITE_INGOT); }
		};
	}
	// Paliers des armes et pioches de fin : palier(durabilité, vitesse de minage). Sacré = runique, impérial = arcanique.
	public static final net.minecraft.world.item.Tier TIER_SACRE = palier(2600, 12f), TIER_IMPERIAL = palier(3600, 16f);
	
	                       
	private static DeferredItem<Item> arme(String nom, fr.chatmort.airain.armure.ArmeItem.Type type, int pal,
			double degats, double vitesse, double portee, double recul, double balayage) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.ArmeItem(pal == 2 ? TIER_IMPERIAL : TIER_SACRE, type, pal,
			new Item.Properties().fireResistant().rarity(pal == 2 ? net.minecraft.world.item.Rarity.EPIC : net.minecraft.world.item.Rarity.RARE)
				.attributes(fr.chatmort.airain.armure.ArmeItem.stats(degats, vitesse, portee, recul, balayage))));
	}
	// Armes de l'Empire : arme(identifiant, type, palier 1 = sacré / 2 = impérial, dégâts, vitesse d'attaque, portée en plus en blocs, recul, balayage). Les pouvoirs sont dans armure/Armes.java.
	public static final DeferredItem<Item> EPEE_SACREE = arme("sacred_sword", fr.chatmort.airain.armure.ArmeItem.Type.EPEE, 1, 10, 1.7, 0.5, 0, 0);
	public static final DeferredItem<Item> EPEE_IMPERIALE = arme("imperial_sword", fr.chatmort.airain.armure.ArmeItem.Type.EPEE, 2, 13, 1.8, 1, 0, 0);
	public static final DeferredItem<Item> KATANA_SACRE = arme("sacred_katana", fr.chatmort.airain.armure.ArmeItem.Type.KATANA, 1, 9, 2.1, 0.5, 0, 0);
	public static final DeferredItem<Item> KATANA_IMPERIAL = arme("imperial_katana", fr.chatmort.airain.armure.ArmeItem.Type.KATANA, 2, 12, 2.3, 1, 0, 0);
	public static final DeferredItem<Item> ESPADON_SACRE = arme("sacred_greatsword", fr.chatmort.airain.armure.ArmeItem.Type.ESPADON, 1, 14, 0.9, 0.5, 0.5, 0);
	public static final DeferredItem<Item> ESPADON_IMPERIAL = arme("imperial_greatsword", fr.chatmort.airain.armure.ArmeItem.Type.ESPADON, 2, 18, 1.0, 1.5, 0.5, 0.5);
	public static final DeferredItem<Item> TWINBLADE_SACREE = arme("sacred_twinblade", fr.chatmort.airain.armure.ArmeItem.Type.TWINBLADE, 1, 8, 1.9, 0, 0, 0);
	public static final DeferredItem<Item> TWINBLADE_IMPERIALE = arme("imperial_twinblade", fr.chatmort.airain.armure.ArmeItem.Type.TWINBLADE, 2, 11, 2.0, 0, 0, 0);
	private static DeferredItem<Item> pioche(String nom, int pal, double portee) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.PiocheItem(pal == 2 ? TIER_IMPERIAL : TIER_SACRE, pal,
			new Item.Properties().fireResistant().rarity(pal == 2 ? net.minecraft.world.item.Rarity.EPIC : net.minecraft.world.item.Rarity.RARE)
				.attributes(net.minecraft.world.item.PickaxeItem.createAttributes(pal == 2 ? TIER_IMPERIAL : TIER_SACRE, 6f, -2.8f).withModifierAdded(
					net.minecraft.world.entity.ai.attributes.Attributes.BLOCK_INTERACTION_RANGE,
					new net.minecraft.world.entity.ai.attributes.AttributeModifier(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(ID, "pioche_portee"), portee,
						net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_VALUE), net.minecraft.world.entity.EquipmentSlotGroup.MAINHAND))));
	}
	public static final DeferredItem<Item> PIOCHE_SACREE = pioche("sacred_pickaxe", 1, 1);
	// Armes runiques (Écho, palier sacré) : mêmes paramètres que arme().
	private static DeferredItem<Item> armeEcho(String nom, fr.chatmort.airain.armure.ArmeItem.Type type, int pal,
			double degats, double vitesse, double portee, double recul, double balayage) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.ArmeItem(TIER_SACRE, type, pal, fr.chatmort.airain.armure.Lignee.ECHO,
			new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.RARE)
				.attributes(fr.chatmort.airain.armure.ArmeItem.stats(degats, vitesse, portee, recul, balayage))));
	}
	public static final DeferredItem<Item> EPEE_RUNIQUE = armeEcho("runic_sword", fr.chatmort.airain.armure.ArmeItem.Type.EPEE, 1, 10, 1.7, 0.5, 0, 0);
	public static final DeferredItem<Item> KATANA_RUNIQUE = armeEcho("runic_katana", fr.chatmort.airain.armure.ArmeItem.Type.KATANA, 1, 9, 2.1, 0.5, 0, 0);
	public static final DeferredItem<Item> ESPADON_RUNIQUE = armeEcho("runic_greatsword", fr.chatmort.airain.armure.ArmeItem.Type.ESPADON, 1, 14, 0.9, 0.5, 0.5, 0);
	public static final DeferredItem<Item> TWINBLADE_RUNIQUE = armeEcho("runic_twinblade", fr.chatmort.airain.armure.ArmeItem.Type.TWINBLADE, 1, 8, 1.9, 0, 0, 0);
	// Armes arcaniques (Écho, palier impérial) : comme arme(), sans le palier.
	private static DeferredItem<Item> armeArcanique(String nom, fr.chatmort.airain.armure.ArmeItem.Type type,
			double degats, double vitesse, double portee, double recul, double balayage) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.ArmeItem(TIER_IMPERIAL, type, 2, fr.chatmort.airain.armure.Lignee.ECHO,
			new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)
				.attributes(fr.chatmort.airain.armure.ArmeItem.stats(degats, vitesse, portee, recul, balayage))));
	}
	public static final DeferredItem<Item> EPEE_ARCANIQUE = armeArcanique("arcane_sword", fr.chatmort.airain.armure.ArmeItem.Type.EPEE, 13, 1.8, 1, 0, 0);
	public static final DeferredItem<Item> KATANA_ARCANIQUE = armeArcanique("arcane_katana", fr.chatmort.airain.armure.ArmeItem.Type.KATANA, 12, 2.3, 1, 0, 0);
	public static final DeferredItem<Item> ESPADON_ARCANIQUE = armeArcanique("arcane_greatsword", fr.chatmort.airain.armure.ArmeItem.Type.ESPADON, 18, 1.0, 1.5, 0.5, 0.5);
	public static final DeferredItem<Item> TWINBLADE_ARCANIQUE = armeArcanique("arcane_twinblade", fr.chatmort.airain.armure.ArmeItem.Type.TWINBLADE, 10, 2.0, 0, 0, 0);
	public static final DeferredItem<Item> PIOCHE_ARCANIQUE = ITEMS.register("arcane_pickaxe", () -> new fr.chatmort.airain.armure.PiocheItem(TIER_IMPERIAL, 2,
		fr.chatmort.airain.armure.Lignee.ECHO, new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)
			.attributes(net.minecraft.world.item.PickaxeItem.createAttributes(TIER_IMPERIAL, 6f, -2.8f))));
	public static final DeferredItem<Item> SCEPTRE_IMPERIAL = ITEMS.register("imperial_scepter", () -> new fr.chatmort.airain.armure.SceptreItem(
		fr.chatmort.airain.armure.Lignee.EMPIRE, new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	public static final DeferredItem<Item> SCEPTRE_ARCANIQUE = ITEMS.register("arcane_scepter", () -> new fr.chatmort.airain.armure.SceptreItem(
		fr.chatmort.airain.armure.Lignee.ECHO, new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	public static final DeferredItem<Item> PIOCHE_RUNIQUE = ITEMS.register("runic_pickaxe", () -> new fr.chatmort.airain.armure.PiocheItem(TIER_SACRE, 1,
		fr.chatmort.airain.armure.Lignee.ECHO, new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.RARE)
			.attributes(net.minecraft.world.item.PickaxeItem.createAttributes(TIER_SACRE, 6f, -2.8f))));
	public static final DeferredItem<Item> PIOCHE_IMPERIALE = pioche("imperial_pickaxe", 2, 2);

	// ---------------------------------------------------------------- lignée de l'Écho (fin Écho) : diadème, matériaux, palier runique
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_DIADEME =
		MATERIAUX.register("diadem", () -> materiau("diadem", 2, 0f, 0f, null));
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_RUNIQUE =
		MATERIAUX.register("runic", () -> materiauArmure("runic", 3, 9, 7, 3, 3.5f, 0.15f));
	public static final DeferredItem<Item> DIADEME = ITEMS.register("echo_diadem",
		() -> new fr.chatmort.airain.armure.DiademeItem(AIRAIN_DIADEME, false, new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)
			.component(net.minecraft.core.component.DataComponents.UNBREAKABLE, new net.minecraft.world.item.component.Unbreakable(false))));
	public static final DeferredItem<Item> CASQUE_DIADEME = ITEMS.register("diadem_helmet",
		() -> new fr.chatmort.airain.armure.DiademeItem(AIRAIN_CASQUE, true, new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.RARE)
			.durability(net.minecraft.world.item.ArmorItem.Type.HELMET.getDurability(37))));
	public static final DeferredItem<Item> LINGOT_ARCANIUM = ITEMS.register("arcanium_ingot",
		() -> new Item(new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.RARE)));
	public static final DeferredBlock<net.minecraft.world.level.block.Block> BLOC_ECHO = BLOCKS.register("primordial_echo_block",
		() -> new net.minecraft.world.level.block.Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE)
			.strength(50f, 1200f).requiresCorrectToolForDrops().sound(SoundType.AMETHYST).lightLevel(s -> 12)));
	public static final DeferredItem<BlockItem> BLOC_ECHO_ITEM = ITEMS.register("primordial_echo_block",
		() -> new BlockItem(BLOC_ECHO.get(), new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	private static DeferredItem<Item> armureEcho(String nom, net.minecraft.world.item.ArmorItem.Type type, int pal) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.ArmureItem(AIRAIN_RUNIQUE, type, pal, fr.chatmort.airain.armure.Lignee.ECHO,
			new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.RARE).durability(type.getDurability(45))));
	}
	public static final DeferredItem<Item> CASQUE_RUNIQUE = armureEcho("runic_helmet", net.minecraft.world.item.ArmorItem.Type.HELMET, 1);
	public static final DeferredItem<Item> PLASTRON_RUNIQUE = armureEcho("runic_chestplate", net.minecraft.world.item.ArmorItem.Type.CHESTPLATE, 1);
	public static final DeferredItem<Item> JAMBIERES_RUNIQUES = armureEcho("runic_leggings", net.minecraft.world.item.ArmorItem.Type.LEGGINGS, 1);
	public static final DeferredItem<Item> BOTTES_RUNIQUES = armureEcho("runic_boots", net.minecraft.world.item.ArmorItem.Type.BOOTS, 1);
	public static final DeferredHolder<net.minecraft.world.item.ArmorMaterial, net.minecraft.world.item.ArmorMaterial> AIRAIN_ARCANIQUE =
		MATERIAUX.register("arcane", () -> materiauArmure("arcane", 4, 10, 8, 4, 4.5f, 0.2f));
	private static DeferredItem<Item> armureArcanique(String nom, net.minecraft.world.item.ArmorItem.Type type) {
		return ITEMS.register(nom, () -> new fr.chatmort.airain.armure.ArmureItem(AIRAIN_ARCANIQUE, type, 2, fr.chatmort.airain.armure.Lignee.ECHO,
			new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC).durability(type.getDurability(55))));
	}
	public static final DeferredItem<Item> CASQUE_ARCANIQUE = armureArcanique("arcane_helmet", net.minecraft.world.item.ArmorItem.Type.HELMET);
	public static final DeferredItem<Item> PLASTRON_ARCANIQUE = armureArcanique("arcane_chestplate", net.minecraft.world.item.ArmorItem.Type.CHESTPLATE);
	public static final DeferredItem<Item> JAMBIERES_ARCANIQUES = armureArcanique("arcane_leggings", net.minecraft.world.item.ArmorItem.Type.LEGGINGS);
	public static final DeferredItem<Item> BOTTES_ARCANIQUES = armureArcanique("arcane_boots", net.minecraft.world.item.ArmorItem.Type.BOOTS);

	/** Modules de gardien (niveaux 1 et 2) et plaque de netherite sacrée qui sert à les améliorer. */
	public static final java.util.Map<String, DeferredItem<Item>> MODULES = new java.util.LinkedHashMap<>();
	static {
		for (fr.chatmort.airain.gardien.Module m : fr.chatmort.airain.gardien.Module.values())
			for (int n = 1; n <= 2; n++) {
				final int niv = n;
				Item.Properties pr = new Item.Properties().stacksTo(1);
				if (niv == 2) pr = pr.fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC);
				else pr = pr.rarity(net.minecraft.world.item.Rarity.UNCOMMON);
				final Item.Properties props = pr;
				MODULES.put(m.id(niv), ITEMS.register(m.id(niv), () -> new fr.chatmort.airain.gardien.ModuleItem(m, niv, props)));
			}
	}
	public static final DeferredItem<Item> PLAQUE_SACREE = ITEMS.register("sacred_netherite_plate",
		() -> new Item(new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)) {
			@Override
			public void appendHoverText(net.minecraft.world.item.ItemStack st, Item.TooltipContext c, java.util.List<Component> l, net.minecraft.world.item.TooltipFlag f) {
				l.add(Component.translatable("item.airain.sacred_netherite_plate.l1").withStyle(net.minecraft.ChatFormatting.GRAY));
				l.add(Component.translatable("item.airain.sacred_netherite_plate.l2").withStyle(net.minecraft.ChatFormatting.GRAY));
			}
		});

	/** Plaque impériale (fin de partie) : plaque sacrée + 5 blocs d'étoile du Nether au déployeur. */
	public static final DeferredBlock<net.minecraft.world.level.block.Block> BLOC_ETOILE = BLOCKS.register("star_block",
		() -> new net.minecraft.world.level.block.Block(BlockBehaviour.Properties.of().mapColor(MapColor.SNOW)
			.strength(50f, 1200f).requiresCorrectToolForDrops().sound(SoundType.NETHERITE_BLOCK).lightLevel(s -> 15)));
	public static final DeferredItem<BlockItem> BLOC_ETOILE_ITEM = ITEMS.register("star_block",
		() -> new BlockItem(BLOC_ETOILE.get(), new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	/** Sièges du pouvoir : trône impérial (fin Empire) et solium de la Prêtresse (fin Écho). */
	public static final DeferredBlock<fr.chatmort.airain.pouvoir.SiegeBlock> TRONE = BLOCKS.register("imperial_throne",
		() -> new fr.chatmort.airain.pouvoir.SiegeBlock(true, BlockBehaviour.Properties.of().mapColor(MapColor.SNOW)
			.strength(50f, 1200f).requiresCorrectToolForDrops().sound(SoundType.NETHERITE_BLOCK).lightLevel(s -> 12).noOcclusion()));
	public static final DeferredItem<BlockItem> TRONE_ITEM = ITEMS.register("imperial_throne",
		() -> new BlockItem(TRONE.get(), new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	public static final DeferredBlock<fr.chatmort.airain.pouvoir.SiegeBlock> SOLIUM = BLOCKS.register("solium",
		() -> new fr.chatmort.airain.pouvoir.SiegeBlock(false, BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE)
			.strength(50f, 1200f).requiresCorrectToolForDrops().sound(SoundType.AMETHYST).lightLevel(s -> 12).noOcclusion()));
	public static final DeferredItem<BlockItem> SOLIUM_ITEM = ITEMS.register("solium",
		() -> new BlockItem(SOLIUM.get(), new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	public static final DeferredHolder<net.minecraft.world.entity.EntityType<?>, net.minecraft.world.entity.EntityType<fr.chatmort.airain.pouvoir.Assise>> ASSISE =
		ENTITES.register("seat", () -> net.minecraft.world.entity.EntityType.Builder.<fr.chatmort.airain.pouvoir.Assise>of(
			fr.chatmort.airain.pouvoir.Assise::new, net.minecraft.world.entity.MobCategory.MISC)
			.sized(0.25f, 0.35f).noSummon().clientTrackingRange(10).build("seat"));
	public static final DeferredItem<Item> PLAQUE_IMPERIALE_INACHEVEE = ITEMS.register("incomplete_imperial_plate",
		() -> new com.simibubi.create.content.processing.sequenced.SequencedAssemblyItem(new Item.Properties().fireResistant()));
	public static final DeferredItem<Item> PLAQUE_IMPERIALE = ITEMS.register("imperial_plate",
		() -> new Item(new Item.Properties().fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)) {
			@Override
			public void appendHoverText(net.minecraft.world.item.ItemStack st, Item.TooltipContext c, java.util.List<Component> l, net.minecraft.world.item.TooltipFlag f) {
				l.add(Component.translatable("item.airain.imperial_plate.l1").withStyle(net.minecraft.ChatFormatting.GOLD, net.minecraft.ChatFormatting.ITALIC));
			}
			@Override
			public boolean isFoil(net.minecraft.world.item.ItemStack st) { return true; }
		});

	/** Plans des améliorations de capitale. */
	public static final DeferredItem<Item> PLAN_AGRANDISSEMENT = plan("expansion_plans", fr.chatmort.airain.fondation.Ameliorations.Type.AGRANDISSEMENT);
	public static final DeferredItem<Item> PLAN_INFIRMERIE = plan("infirmary_plans", fr.chatmort.airain.fondation.Ameliorations.Type.INFIRMERIE);
	public static final DeferredItem<Item> PLAN_METEO = plan("weather_station_plans", fr.chatmort.airain.fondation.Ameliorations.Type.METEO);
	public static final DeferredItem<Item> PLAN_FORGE = plan("garrison_forge_plans", fr.chatmort.airain.fondation.Ameliorations.Type.FORGE);
	private static DeferredItem<Item> plan(String id, fr.chatmort.airain.fondation.Ameliorations.Type t) {
		return ITEMS.register(id, () -> new fr.chatmort.airain.fondation.PlanItem(t, new Item.Properties().stacksTo(16).rarity(net.minecraft.world.item.Rarity.EPIC)));
	}

	/** La machine de l'Empereur : apparaît là où il tombe ; on y pose le Cœur puis on la rallume (fin Empire). Incassable. */
	public static final DeferredBlock<fr.chatmort.airain.choix.MachineEmpereurBlock> MACHINE_EMPEREUR = BLOCKS.register("emperor_machine",
		() -> new fr.chatmort.airain.choix.MachineEmpereurBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f)
			.noOcclusion().sound(SoundType.NETHERITE_BLOCK).lightLevel(s -> s.getValue(fr.chatmort.airain.choix.MachineEmpereurBlock.ETAT) == 2 ? 12 : 0)));

	/** Manuels d'armes : une page par arme et par armure de fin, dévoilée en la portant. Empire (0) et Écho (1). */
	public static final DeferredItem<Item> MANUEL_EMPIRE = ITEMS.register("imperial_arms_regulations",
		() -> new fr.chatmort.airain.manuel.ManuelItem(0, new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.UNCOMMON)));
	public static final DeferredItem<Item> MANUEL_ECHO = ITEMS.register("echo_arms_treatise",
		() -> new fr.chatmort.airain.manuel.ManuelItem(1, new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.UNCOMMON)));

	/** Chroniques oubliées : le livre de l'aventure. */
	public static final DeferredItem<Item> CHRONIQUES = ITEMS.register("chronicles",
		() -> new fr.chatmort.airain.chronique.ChroniquesItem(new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.UNCOMMON)));
	/** Reliure de l'ingénieur : huit livres sous la main, lisibles depuis le sac. */
	public static final DeferredItem<Item> RELIURE = ITEMS.register("binder",
		() -> new fr.chatmort.airain.reliure.ReliureItem(new Item.Properties().stacksTo(1)
			.component(net.minecraft.core.component.DataComponents.CONTAINER, net.minecraft.world.item.component.ItemContainerContents.EMPTY)));
	public static final DeferredHolder<MenuType<?>, MenuType<fr.chatmort.airain.reliure.ReliureMenu>> RELIURE_MENU = MENUS.register("binder",
		() -> IMenuTypeExtension.create(fr.chatmort.airain.reliure.ReliureMenu::new));
	/** Tableau de service : notes épinglées pour l'équipe. */
	public static final DeferredBlock<fr.chatmort.airain.tableau.TableauBlock> TABLEAU = BLOCKS.register("duty_board",
		() -> new fr.chatmort.airain.tableau.TableauBlock(BlockBehaviour.Properties.of()
			.mapColor(MapColor.WOOD).strength(1f).sound(SoundType.WOOD).noOcclusion().noCollission()));
	public static final DeferredItem<BlockItem> TABLEAU_ITEM = ITEMS.register("duty_board",
		() -> new BlockItem(TABLEAU.get(), new Item.Properties()));
	/** Atlas impérial : la carte de ce que l'équipe a parcouru. */
	public static final DeferredItem<Item> ATLAS = ITEMS.register("atlas",
		() -> new fr.chatmort.airain.atlas.AtlasItem(new Item.Properties().stacksTo(1)));
	/** Affiche vierge : à passer au déployeur avec un symbole. */
	public static final DeferredItem<Item> AFFICHE_VIERGE = ITEMS.register("blank_poster", () -> new Item(new Item.Properties()));
	/** Charte impériale : rallume un avant-poste (fin de l'Empire). */
	public static final DeferredItem<Item> CHARTE = ITEMS.register("imperial_charter",
		() -> new fr.chatmort.airain.suite.CharteItem(new Item.Properties().stacksTo(16).rarity(net.minecraft.world.item.Rarity.RARE)));
	/** Comptoirs des avant-postes : carte vers une structure, plan pour le canon à schémas. */
	public static final DeferredItem<Item> CARTE_EMPIRE = ITEMS.register("empire_map",
		() -> new fr.chatmort.airain.comptoir.CarteItem(new Item.Properties()));
	public static final DeferredItem<Item> PLAN = ITEMS.register("blueprint",
		() -> new fr.chatmort.airain.comptoir.PlanItem(new Item.Properties()));
	public static final DeferredItem<Item> REGISTRE = ITEMS.register("foundation_registry",
		() -> new fr.chatmort.airain.fondation.RegistreItem(new Item.Properties().stacksTo(1)));

	/** Encre runique : consommée quand la table applique le niveau ouvert par un tome ancien. */
	public static final DeferredItem<Item> ENCRE = ITEMS.register("runic_ink",
		() -> new Item(new Item.Properties().rarity(net.minecraft.world.item.Rarity.RARE)));
	public static final DeferredItem<BlockItem> DESENCH_ITEM = ITEMS.register("disenchanter",
		() -> new BlockItem(DESENCH.get(), new Item.Properties()));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<DesenchanteurBlockEntity>> DESENCH_BE =
		BLOCK_ENTITIES.register("disenchanter",
			() -> BlockEntityType.Builder.of(DesenchanteurBlockEntity::new, DESENCH.get()).build(null));

	// ---- bornes de commande (fin de partie)
	private static BlockBehaviour.Properties propBorne(boolean emp) {
		return BlockBehaviour.Properties.of().mapColor(emp ? MapColor.GOLD : MapColor.COLOR_PURPLE).strength(5f, 1200f)
			.sound(emp ? SoundType.METAL : SoundType.AMETHYST).noOcclusion().lightLevel(s -> 9);
	}
	public static final DeferredBlock<fr.chatmort.airain.borne.BorneBlock> BORNE_IMPERIALE = BLOCKS.register("difference_engine",
		() -> new fr.chatmort.airain.borne.BorneBlock(true, propBorne(true)));
	public static final DeferredBlock<fr.chatmort.airain.borne.BorneBlock> BORNE_ARCANIQUE = BLOCKS.register("resonant_archive",
		() -> new fr.chatmort.airain.borne.BorneBlock(false, propBorne(false)));
	public static final DeferredBlock<fr.chatmort.airain.borne.BornePartieBlock> BORNE_PARTIE_IMPERIALE = BLOCKS.register("difference_engine_part",
		() -> new fr.chatmort.airain.borne.BornePartieBlock(true, propBorne(true).noLootTable()));
	public static final DeferredBlock<fr.chatmort.airain.borne.BornePartieBlock> BORNE_PARTIE_ARCANIQUE = BLOCKS.register("resonant_archive_part",
		() -> new fr.chatmort.airain.borne.BornePartieBlock(false, propBorne(false).noLootTable()));
	public static final DeferredItem<BlockItem> BORNE_IMPERIALE_ITEM = ITEMS.register("difference_engine",
		() -> new BlockItem(BORNE_IMPERIALE.get(), new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	public static final DeferredItem<BlockItem> BORNE_ARCANIQUE_ITEM = ITEMS.register("resonant_archive",
		() -> new BlockItem(BORNE_ARCANIQUE.get(), new Item.Properties().stacksTo(1).fireResistant().rarity(net.minecraft.world.item.Rarity.EPIC)));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<fr.chatmort.airain.borne.BorneBlockEntity>> BORNE_BE =
		BLOCK_ENTITIES.register("order_terminal", () -> BlockEntityType.Builder.of(fr.chatmort.airain.borne.BorneBlockEntity::new,
			BORNE_IMPERIALE.get(), BORNE_ARCANIQUE.get()).build(null));
	/** Modèles de la caisse livrée et du parachute (dessinés par l'entité, jamais posés). */
	public static final DeferredBlock<net.minecraft.world.level.block.Block> CAISSE_IMPERIALE = BLOCKS.register("imperial_delivery_crate",
		() -> new net.minecraft.world.level.block.Block(BlockBehaviour.Properties.of().noLootTable().noOcclusion()));
	public static final DeferredBlock<net.minecraft.world.level.block.Block> CAISSE_ARCANIQUE = BLOCKS.register("arcane_delivery_crate",
		() -> new net.minecraft.world.level.block.Block(BlockBehaviour.Properties.of().noLootTable().noOcclusion()));
	public static final DeferredBlock<net.minecraft.world.level.block.Block> PARACHUTE = BLOCKS.register("parachute",
		() -> new net.minecraft.world.level.block.Block(BlockBehaviour.Properties.of().noLootTable().noOcclusion()));
	public static final DeferredHolder<net.minecraft.world.entity.EntityType<?>, net.minecraft.world.entity.EntityType<fr.chatmort.airain.borne.CaisseEntity>> CAISSE =
		ENTITES.register("delivery_crate", () -> net.minecraft.world.entity.EntityType.Builder.<fr.chatmort.airain.borne.CaisseEntity>of(
			fr.chatmort.airain.borne.CaisseEntity::new, net.minecraft.world.entity.MobCategory.MISC)
			.sized(0.9f, 0.9f).noSummon().fireImmune().clientTrackingRange(10).updateInterval(2).build("delivery_crate"));

	/** Anciens identifiants (français) → nouveaux (anglais) : les mondes existants retrouvent leurs objets. */
	private static final String[] ANCIENS_OBJETS = {"couronne_airain", "airain_crown", "bottes_arcaniques", "arcane_boots", "plastron_arcanique", "arcane_chestplate", "espadon_arcanique", "arcane_greatsword", "casque_arcanique", "arcane_helmet", "katana_arcanique", "arcane_katana", "jambieres_arcaniques", "arcane_leggings", "pioche_arcanique", "arcane_pickaxe", "sceptre_arcanique", "arcane_scepter", "epee_arcanique", "arcane_sword", "twinblade_arcanique", "arcane_twinblade", "lingot_arcanium", "arcanium_ingot", "module_blindage", "armor_module", "module_blindage_2", "armor_module_2", "gabarit_banniere", "banner_template", "reliure", "binder", "affiche_vierge", "blank_poster", "plan", "blueprint", "module_chaudiere", "boiler_module", "module_chaudiere_2", "boiler_module_2", "module_canon", "cannon_module", "module_canon_2", "cannon_module_2", "sceau_centurion", "centurion_seal", "chroniques", "chronicles", "visiere_colosse", "colossus_visor", "casque_couronne", "crowned_helmet", "balise_defense", "defense_beacon", "casque_diademe", "diadem_helmet", "borne_imperiale", "difference_engine", "desenchanteur", "disenchanter", "tableau_service", "duty_board", "diademe_echo", "echo_diadem", "carte_empire", "empire_map", "livre_ingenieur", "engineers_manual", "meule_fine", "fine_grindstone", "registre_fondations", "foundation_registry", "pierre_fondation", "foundation_stone", "banniere_murale", "foundation_wall_banner", "graisseur", "grease_gun", "grand_etendard", "great_standard", "oeil_gardien", "guardian_eye", "gardien_spawn_egg", "guardian_spawn_egg", "bottes_imperiales", "imperial_boots", "charte", "imperial_charter", "plastron_imperial", "imperial_chestplate", "table_enchantement", "imperial_enchanting_table", "espadon_imperial", "imperial_greatsword", "casque_imperial", "imperial_helmet", "katana_imperial", "imperial_katana", "jambieres_imperiales", "imperial_leggings", "pioche_imperiale", "imperial_pickaxe", "plaque_imperiale", "imperial_plate", "sceptre_imperial", "imperial_scepter", "epee_imperiale", "imperial_sword", "trone_imperial", "imperial_throne", "twinblade_imperiale", "imperial_twinblade", "plaque_imperiale_inachevee", "incomplete_imperial_plate", "module_lanterne", "lantern_module", "module_lanterne_2", "lantern_module_2", "coeur_magma", "magma_heart", "banc_entretien", "maintenance_bench", "bloc_echo_primordial", "primordial_echo_block", "engrenage_rodeur", "prowler_gear", "demultiplicateur", "reduction_gear", "borne_arcanique", "resonant_archive", "bottes_runiques", "runic_boots", "plastron_runique", "runic_chestplate", "espadon_runique", "runic_greatsword", "casque_runique", "runic_helmet", "encre_runique", "runic_ink", "katana_runique", "runic_katana", "jambieres_runiques", "runic_leggings", "pioche_runique", "runic_pickaxe", "epee_runique", "runic_sword", "twinblade_runique", "runic_twinblade", "bottes_sacrees", "sacred_boots", "plastron_sacre", "sacred_chestplate", "casque_couronne_sacree", "sacred_crown", "espadon_sacre", "sacred_greatsword", "katana_sacre", "sacred_katana", "jambieres_sacrees", "sacred_leggings", "plaque_netherite_sacree", "sacred_netherite_plate", "pioche_sacree", "sacred_pickaxe", "epee_sacree", "sacred_sword", "twinblade_sacree", "sacred_twinblade", "module_lunette", "scope_module", "module_lunette_2", "scope_module_2", "bloc_etoile", "star_block", "module_tesla", "tesla_module", "module_tesla_2", "tesla_module_2", "socle_trophee", "trophy_pedestal"};
	private static final String[] ANCIENS_BLOCS = {"caisse_arcanique", "arcane_delivery_crate", "balise_defense", "defense_beacon", "balise_partie", "defense_beacon_part", "borne_imperiale", "difference_engine", "borne_partie_imperiale", "difference_engine_part", "desenchanteur", "disenchanter", "tableau_service", "duty_board", "pierre_fondation", "foundation_stone", "banniere_murale", "foundation_wall_banner", "grand_etendard", "great_standard", "caisse_imperiale", "imperial_delivery_crate", "table_enchantement", "imperial_enchanting_table", "trone_imperial", "imperial_throne", "banc_entretien", "maintenance_bench", "bloc_echo_primordial", "primordial_echo_block", "borne_arcanique", "resonant_archive", "borne_partie_arcanique", "resonant_archive_part", "bloc_etoile", "star_block", "socle_trophee", "trophy_pedestal"};
	private static final String[] ANCIENNES_ENTITES = {"gardien", "guardian", "assise", "seat", "caisse_livraison", "delivery_crate"};
	private static final String[] ANCIENS_BE = {"balise_defense", "defense_beacon", "banc_entretien", "maintenance_bench", "borne", "order_terminal", "desenchanteur", "disenchanter", "pierre_fondation", "foundation_stone", "socle_trophee", "trophy_pedestal", "table_enchantement", "imperial_enchanting_table"};
	private static void alias(DeferredRegister<?> r, String[] t) {
		for (int i = 0; i < t.length; i += 2)
			r.addAlias(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(ID, t[i]), net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(ID, t[i + 1]));
	}

	public AirainMod(IEventBus bus) {
		alias(ITEMS, ANCIENS_OBJETS);
		alias(BLOCKS, ANCIENS_BLOCS);
		alias(ENTITES, ANCIENNES_ENTITES);
		alias(BLOCK_ENTITIES, ANCIENS_BE);
		BLOCKS.register(bus);
		ITEMS.register(bus);
		BLOCK_ENTITIES.register(bus);
		MENUS.register(bus);
		ENTITES.register(bus);
		SERIALISEURS.register(bus);
		MATERIAUX.register(bus);
		bus.addListener((net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent e) ->
			e.put(GARDIEN.get(), net.minecraft.world.entity.animal.IronGolem.createAttributes().build()));
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Gardiens::etendard);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Fin::commandes);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.pouvoir.Siege::commandes);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.pouvoir.Siege::mort);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.pouvoir.Siege::croissance);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Fin::cible);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Fin::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Fin::experience);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.CouronneItem::enclume);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.DiademeItem::enclume);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.chronique.Chronique::dimension);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.chronique.Chronique::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.manuel.Manuel::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.choix.ChoixFinal::mort);        // choix final dans le monde
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.choix.ChoixFinal::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.choix.ChoixFinal::resonateur);   // pages des manuels d'armes
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.tableau.Tableaux::connexion);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.atlas.Atlas::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.atlas.Atlas::mort);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.suite.Suites::diapason);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.suite.Suites::apparition);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.suite.Suites::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.suite.Suites::connexion);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Fin::vibration);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Fin::apparition);
		NeoForge.EVENT_BUS.addListener(this::tableVanilla);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::chute);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::boss);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::coups);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.trophee.Trophees::joueur);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.Armures::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.Armures::cible);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.Armes::joueur);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.Armes::critique);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.Armes::tick);
		NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.Armes::filon);
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
			.playToServer(fr.chatmort.airain.reliure.Paquets.Lire.TYPE, fr.chatmort.airain.reliure.Paquets.Lire.CODEC, fr.chatmort.airain.reliure.Paquets.Lire::traiter)
			.playToServer(fr.chatmort.airain.reliure.Paquets.Chercher.TYPE, fr.chatmort.airain.reliure.Paquets.Chercher.CODEC, fr.chatmort.airain.reliure.Paquets.Chercher::traiter)
			.playToClient(fr.chatmort.airain.reliure.Paquets.Ouvrir.TYPE, fr.chatmort.airain.reliure.Paquets.Ouvrir.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.reliure(m)))
			.playToServer(fr.chatmort.airain.tableau.PaquetsTableau.Action.TYPE, fr.chatmort.airain.tableau.PaquetsTableau.Action.CODEC,
				fr.chatmort.airain.tableau.PaquetsTableau.Action::traiter)
			.playToClient(fr.chatmort.airain.tableau.PaquetsTableau.Ouvrir.TYPE, fr.chatmort.airain.tableau.PaquetsTableau.Ouvrir.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.tableau(m)))
			.playToClient(fr.chatmort.airain.atlas.OuvrirAtlas.TYPE, fr.chatmort.airain.atlas.OuvrirAtlas.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.atlas(m)))
			.playToClient(fr.chatmort.airain.manuel.OuvrirManuel.TYPE, fr.chatmort.airain.manuel.OuvrirManuel.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.manuel(m)))
			.playToClient(fr.chatmort.airain.chronique.Theme.TYPE, fr.chatmort.airain.chronique.Theme.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.theme(m)))
			.playToClient(fr.chatmort.airain.chronique.OuvrirChroniques.TYPE, fr.chatmort.airain.chronique.OuvrirChroniques.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.chroniques(m)))
			.playToClient(fr.chatmort.airain.armure.TourbillonPaquet.TYPE, fr.chatmort.airain.armure.TourbillonPaquet.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.tourbillon(m)))
			.playToClient(fr.chatmort.airain.codex.OuvrirCodex.TYPE, fr.chatmort.airain.codex.OuvrirCodex.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.codex(m)))
			.playToClient(fr.chatmort.airain.borne.PaquetsBorne.Ouvrir.TYPE, fr.chatmort.airain.borne.PaquetsBorne.Ouvrir.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.borne(m)))
			.playToServer(fr.chatmort.airain.borne.PaquetsBorne.Commander.TYPE, fr.chatmort.airain.borne.PaquetsBorne.Commander.CODEC,
				fr.chatmort.airain.borne.PaquetsBorne.Commander::traiter)
			.playToClient(fr.chatmort.airain.fondation.OuvrirRegistre.TYPE, fr.chatmort.airain.fondation.OuvrirRegistre.CODEC,
				(m, ctx) -> ctx.enqueueWork(() -> fr.chatmort.airain.fondation.EcranClient.registre(m))));
		bus.addListener(this::setup);
		bus.addListener(this::capacites);
		ONGLETS.register(bus);
	}

	private void setup(FMLCommonSetupEvent event) {
		// Impact de stress à 1 tr/min, comme la presse mécanique
		event.enqueueWork(() -> {
			// la loupe de la couronne fait office de lunettes d'ingénieur de Create
			com.simibubi.create.content.equipment.goggles.GogglesItem.addIsWearingPredicate(
				fr.chatmort.airain.gardien.Fin::couronne);
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
