package fr.chatmort.airain.atelier;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.StackedContents;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.ArrayList;
import java.util.List;

/** Établi d'atelier : une table de craft dont la grille garde ses objets quand on la quitte (et pour tout le monde). */
public class Etabli extends BaseEntityBlock {
	public static final MapCodec<Etabli> CODEC = simpleCodec(Etabli::new);
	private static final VoxelShape FORME = Shapes.or(Block.box(0, 13, 0, 16, 16, 16), Block.box(0.5, 0, 0.5, 15.5, 13, 15.5));
	public Etabli(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)); }
	@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING); }
	@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, c.getHorizontalDirection().getOpposite()); }
	@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
	@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new EtabliBlockEntity(p, s); }
	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
		if (!l.isClientSide && j instanceof ServerPlayer sp && l.getBlockEntity(p) instanceof EtabliBlockEntity be)
			sp.openMenu(new SimpleMenuProvider((id, inv, pl) -> new EtabliMenu(id, inv, be), Component.translatable("block.airain.airain_workbench")), buf -> buf.writeBlockPos(p));
		return InteractionResult.sidedSuccess(l.isClientSide);
	}
	@Override
	protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
		if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof EtabliBlockEntity be) Containers.dropContents(l, p, be);
		super.onRemove(s, l, p, n, deplace);
	}

	/** La grille 3 × 3 de l'établi, sauvegardée avec le bloc ; chaque changement prévient les écrans ouverts. */
	public static class EtabliBlockEntity extends BlockEntity implements CraftingContainer {
		private final NonNullList<ItemStack> objets = NonNullList.withSize(9, ItemStack.EMPTY);
		final List<EtabliMenu> ouverts = new ArrayList<>();
		public EtabliBlockEntity(BlockPos p, BlockState s) { super(Atelier.ETABLI_BE.get(), p, s); }
		private void change() {
			setChanged();
			for (EtabliMenu m : List.copyOf(ouverts)) m.slotsChanged(this);
		}
		@Override public int getWidth() { return 3; }
		@Override public int getHeight() { return 3; }
		@Override public List<ItemStack> getItems() { return List.copyOf(objets); }
		@Override public int getContainerSize() { return 9; }
		@Override public boolean isEmpty() { for (ItemStack s : objets) if (!s.isEmpty()) return false; return true; }
		@Override public ItemStack getItem(int i) { return objets.get(i); }
		@Override public ItemStack removeItem(int i, int n) { ItemStack r = ContainerHelper.removeItem(objets, i, n); if (!r.isEmpty()) change(); return r; }
		@Override public ItemStack removeItemNoUpdate(int i) { return ContainerHelper.takeItem(objets, i); }
		@Override public void setItem(int i, ItemStack s) { objets.set(i, s); change(); }
		@Override public boolean stillValid(Player j) { return level != null && level.getBlockEntity(worldPosition) == this && j.distanceToSqr(worldPosition.getCenter()) < 64; }
		@Override public void clearContent() { objets.clear(); change(); }
		@Override public void fillStackedContents(StackedContents c) { for (ItemStack s : objets) c.accountSimpleStack(s); }
		@Override protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); ContainerHelper.saveAllItems(t, objets, r); }
		@Override protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); objets.clear(); ContainerHelper.loadAllItems(t, objets, r); }
	}
}
