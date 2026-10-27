package fr.chatmort.airain.enchant;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Table d'enchantement de l'Empire : on choisit l'enchantement parmi les livres des bibliothèques sculptées voisines. */
public class TableEmpireBlock extends Block {
	private static final VoxelShape FORME = Block.box(0, 0, 0, 16, 12, 16);

	public TableEmpireBlock(Properties properties) {
		super(properties);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
		return FORME;
	}

	@Override
	protected boolean useShapeForLightOcclusion(BlockState state) {
		return true;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
		if (level.isClientSide)
			return InteractionResult.SUCCESS;
		if (player instanceof ServerPlayer sp) {
			sp.openMenu(new SimpleMenuProvider((id, inv, p) -> new TableEmpireMenu(id, inv, ContainerLevelAccess.create(level, pos)),
				Component.translatable("block.airain.table_enchantement")), buf -> buf.writeBlockPos(pos));
		}
		return InteractionResult.CONSUME;
	}
}
