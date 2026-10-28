package fr.chatmort.airain.trophee;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.Containers;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Socle de l'Empire : on y expose un trophée de boss ; tant qu'il y reste, son effet profite à toute l'équipe. */
public class SocleBlock extends Block implements EntityBlock {
	private static final VoxelShape FORME = Shapes.or(Block.box(1, 0, 1, 15, 2, 15), Block.box(3, 2, 3, 13, 10, 13), Block.box(1, 10, 1, 15, 12, 15));

	public SocleBlock(Properties p) {
		super(p);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return FORME;
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new SocleBlockEntity(pos, state);
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur, InteractionHand main, BlockHitResult hit) {
		if (!(level.getBlockEntity(pos) instanceof SocleBlockEntity socle) || !socle.trophee().isEmpty())
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (!Trophees.estTrophee(pile)) {
			if (!level.isClientSide)
				joueur.displayClientMessage(Component.translatable("airain.socle.pas_trophee"), true);
			return ItemInteractionResult.CONSUME;
		}
		if (!level.isClientSide) {
			socle.exposer(pile);
			if (!joueur.getAbilities().instabuild) pile.shrink(1);
			level.playSound(null, pos, SoundEvents.ARMOR_EQUIP_GOLD.value(), SoundSource.BLOCKS, 1f, 0.8f);
			joueur.displayClientMessage(Component.translatable("airain.socle.expose"), true);
		}
		return ItemInteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		if (!(level.getBlockEntity(pos) instanceof SocleBlockEntity socle) || socle.trophee().isEmpty())
			return InteractionResult.PASS;
		if (!level.isClientSide) {
			ItemStack p = socle.reprendre();
			if (!joueur.addItem(p)) joueur.drop(p, false);
			level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.6f, 1f);
		}
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && level.getBlockEntity(pos) instanceof SocleBlockEntity socle && level instanceof ServerLevel) {
			ItemStack p = socle.reprendre();
			if (!p.isEmpty()) Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, p);
		}
		super.onRemove(state, level, pos, neuf, deplace);
	}
}
