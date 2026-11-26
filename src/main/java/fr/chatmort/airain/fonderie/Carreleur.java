package fr.chatmort.airain.fonderie;

import com.mojang.serialization.MapCodec;

import fr.chatmort.airain.AirainMod;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.core.component.DataComponentMap;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.ItemContainerContents;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * 1.70 : la table du carreleur. Onglet Création : un motif tout fait, les blocs de ses rôles, ses réglages, un nom ;
 * « Print » écrit le motif sur un carton vierge. Onglets Sols / Murs / Plafonds : rangement partagé des cartons
 * (36 par onglet), gardé dans l'objet quand on casse la table.
 */
public final class Carreleur {
	private Carreleur() {}

	public static final int RANGEMENT = 36, ROLES = 108, ENTREE = 112, SORTIE = 113, TAILLE = 114;
	public static final int ROLE_A = 0, ROLE_B = 1, ROLE_ACCENT = 2, ROLE_BORD = 3;

	public static final DeferredBlock<Table> TABLE = AirainMod.BLOCKS.register("tilers_table", () -> new Table(BlockBehaviour.Properties.of()
		.mapColor(MapColor.GOLD).strength(2.5f, 6f).sound(SoundType.COPPER).noOcclusion()));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TableBE>> TABLE_BE = AirainMod.BLOCK_ENTITIES.register("tilers_table",
		() -> BlockEntityType.Builder.of(TableBE::new, TABLE.get()).build(null));
	public static final DeferredHolder<MenuType<?>, MenuType<CarreleurMenu>> MENU = AirainMod.MENUS.register("tilers_table",
		() -> IMenuTypeExtension.create(CarreleurMenu::new));

	public static void charger() {
		AirainMod.ITEMS.register("tilers_table", () -> new BlockItem(TABLE.get(), new Item.Properties()));
	}

	// ------------------------------------------------------------------ le bloc
	public static class Table extends BaseEntityBlock {
		public static final MapCodec<Table> CODEC = simpleCodec(Table::new);
		public Table(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)); }
		@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, c.getHorizontalDirection().getOpposite()); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new TableBE(p, s); }
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!l.isClientSide && j instanceof ServerPlayer sp && l.getBlockEntity(p) instanceof TableBE be)
				sp.openMenu(new SimpleMenuProvider((id, inv, pl) -> new CarreleurMenu(id, inv, be), Component.translatable("block.airain.tilers_table")), buf -> buf.writeBlockPos(p));
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
	}

	// ------------------------------------------------------------------ l'entité : 3 x 36 cartons rangés, 4 rôles, carton vierge, carton imprimé
	public static class TableBE extends BlockEntity implements Container {
		private final NonNullList<ItemStack> objets = NonNullList.withSize(TAILLE, ItemStack.EMPTY);
		public TableBE(BlockPos p, BlockState s) { super(TABLE_BE.get(), p, s); }
		@Override public int getContainerSize() { return TAILLE; }
		@Override public boolean isEmpty() { for (ItemStack s : objets) if (!s.isEmpty()) return false; return true; }
		@Override public ItemStack getItem(int i) { return objets.get(i); }
		@Override public ItemStack removeItem(int i, int n) { ItemStack r = ContainerHelper.removeItem(objets, i, n); if (!r.isEmpty()) setChanged(); return r; }
		@Override public ItemStack removeItemNoUpdate(int i) { return ContainerHelper.takeItem(objets, i); }
		@Override public void setItem(int i, ItemStack s) { objets.set(i, s); setChanged(); }
		@Override public boolean stillValid(Player j) { return level != null && level.getBlockEntity(worldPosition) == this && j.distanceToSqr(worldPosition.getCenter()) < 64; }
		@Override public void clearContent() { objets.clear(); setChanged(); }
		@Override protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); ContainerHelper.saveAllItems(t, objets, r); }
		@Override protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); objets.clear(); ContainerHelper.loadAllItems(t, objets, r); }
		// la table cassée garde son contenu dans l'objet (comme une boîte de shulker)
		@Override protected void collectImplicitComponents(DataComponentMap.Builder b) { super.collectImplicitComponents(b); b.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(objets)); }
		@Override protected void applyImplicitComponents(BlockEntity.DataComponentInput c) {
			super.applyImplicitComponents(c);
			c.getOrDefault(DataComponents.CONTAINER, ItemContainerContents.EMPTY).copyInto(objets);
		}
		@Override public void removeComponentsFromTag(CompoundTag t) { t.remove("Items"); }
	}

	// ------------------------------------------------------------------ impression (paquet client -> serveur)
	public record Imprimer(int genre, int dessin, int reglage, int bordL, String nom) implements CustomPacketPayload {
		public static final Type<Imprimer> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "carreleur_imprimer"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Imprimer> CODEC = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, Imprimer::genre, ByteBufCodecs.VAR_INT, Imprimer::dessin, ByteBufCodecs.VAR_INT, Imprimer::reglage,
			ByteBufCodecs.VAR_INT, Imprimer::bordL, ByteBufCodecs.stringUtf8(40), Imprimer::nom, Imprimer::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Imprimer m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p) || !(p.containerMenu instanceof CarreleurMenu menu) || !menu.stillValid(p)) return;
				if (m.genre() < 0 || m.genre() > 2) return;
				var liste = Generateur.PAR_TYPE.get(m.genre());
				if (m.dessin() < 0 || m.dessin() >= liste.size()) return;
				Generateur.Dessin d = liste.get(m.dessin());
				Container c = menu.table;
				ItemStack entree = c.getItem(ENTREE);
				if (!entree.is(Motif.CARTON.get()) || Motif.enregistre(entree) || !c.getItem(SORTIE).isEmpty()) return;
				BlockState[] roles = new BlockState[3];
				for (int k = 0; k < 3; k++) roles[k] = etatDe(c.getItem(ROLES + k));
				BlockState bord = m.bordL() > 0 ? etatDe(c.getItem(ROLES + ROLE_BORD)) : null;
				if (roles[0] == null || roles[1] == null || (d.accent && roles[2] == null) || (m.bordL() > 0 && bord == null)) {
					p.displayClientMessage(Component.translatable("airain.carreleur.roles_manquants").withStyle(ChatFormatting.RED), true); return;
				}
				if (!d.accent) roles[2] = roles[0];
				ItemStack carton = new ItemStack(Motif.CARTON.get());
				Motif.ecrireGenere(carton, Generateur.TYPES[m.genre()], Generateur.tuile(d, m.reglage()), roles, bord, Math.min(3, Math.max(0, m.bordL())));
				String nom = m.nom().strip();
				if (!nom.isEmpty()) carton.set(DataComponents.CUSTOM_NAME, Component.literal(nom));
				entree.shrink(1);
				c.setItem(ENTREE, entree);
				c.setItem(SORTIE, carton);
				p.level().playSound(null, p.blockPosition(), SoundEvents.UI_CARTOGRAPHY_TABLE_TAKE_RESULT, SoundSource.BLOCKS, 0.9f, 1.1f);
			});
		}
	}

	/** L'état d'un bloc posé dans une case de rôle (bloc plein seulement pour cette première version). */
	public static BlockState etatDe(ItemStack s) {
		return s.getItem() instanceof BlockItem bi ? bi.getBlock().defaultBlockState() : null;
	}
}
