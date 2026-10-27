package fr.chatmort.airain.banc;

import com.simibubi.create.content.kinetics.base.HorizontalAxisKineticBlock;
import com.simibubi.create.foundation.block.IBE;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.BlockHitResult;

/**
 * Banc d'entretien : bloc cinétique traversé par un arbre (axe horizontal, choisi à la pose).
 * Clic droit avec un objet : le pose sur le banc (objet abîmé, matériau, ou huile).
 * Clic droit main vide : reprend l'objet réparé, sinon le matériau, sinon l'objet en cours.
 */
public class BancEntretienBlock extends HorizontalAxisKineticBlock implements IBE<BancEntretienBlockEntity> {

	public BancEntretienBlock(Properties properties) {
		super(properties);
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
											  InteractionHand hand, BlockHitResult hit) {
		if (stack.isEmpty())
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (level.isClientSide)
			return ItemInteractionResult.SUCCESS;
		return onBlockEntityUseItemOn(level, pos, be -> be.utiliserObjet(player, hand, stack)
			? ItemInteractionResult.SUCCESS : ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
		if (level.isClientSide)
			return InteractionResult.SUCCESS;
		withBlockEntityDo(level, pos, be -> be.reprendre(player));
		return InteractionResult.SUCCESS;
	}

	@Override
	public Class<BancEntretienBlockEntity> getBlockEntityClass() {
		return BancEntretienBlockEntity.class;
	}

	@Override
	public BlockEntityType<? extends BancEntretienBlockEntity> getBlockEntityType() {
		return AirainMod.BANC_BE.get();
	}

	@Override
	protected boolean isPathfindable(BlockState state, PathComputationType type) {
		return false;
	}
}
