package fr.chatmort.airain.fondation;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.fml.loading.FMLEnvironment;

/** Pierre de fondation : nomme une base ; en entrant dans sa zone, le nom s'affiche à l'écran. */
public class FondationBlock extends Block implements EntityBlock {
	public FondationBlock(Properties p) {
		super(p);
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new FondationBlockEntity(pos, state);
	}

	@Override
	public void setPlacedBy(Level level, BlockPos pos, BlockState state, LivingEntity qui, ItemStack pile) {
		super.setPlacedBy(level, pos, state, qui, pile);
		if (level.getBlockEntity(pos) instanceof FondationBlockEntity f) {
			f.enregistrer();
			if (level.isClientSide && FMLEnvironment.dist.isClient())
				EcranClient.ouvrir(pos, f.nom());
		}
	}

	@Override
	protected ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur, InteractionHand main, BlockHitResult hit) {
		if (!BuiltInRegistries.ITEM.getKey(pile.getItem()).toString().equals("create:wrench"))
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (!(level.getBlockEntity(pos) instanceof FondationBlockEntity f))
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (!level.isClientSide) {
			int r = f.rayon() + (joueur.isShiftKeyDown() ? -FondationBlockEntity.PAS : FondationBlockEntity.PAS);
			if (r > FondationBlockEntity.RAYON_MAX) r = FondationBlockEntity.RAYON_MIN;
			if (r < FondationBlockEntity.RAYON_MIN) r = FondationBlockEntity.RAYON_MAX;
			f.regler(r);
			joueur.displayClientMessage(Component.translatable("airain.fondation.rayon", f.rayon()), true);
			level.playSound(null, pos, SoundEvents.UI_BUTTON_CLICK.value(), SoundSource.BLOCKS, 0.5f, 1.2f);
			if (level instanceof ServerLevel sl)                       // cercle de particules : la limite de la zone
				for (int k = 0; k < 96; k++) {
					double a = k * Math.PI * 2 / 96;
					sl.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5 + Math.cos(a) * f.rayon(), pos.getY() + 1.2,
						pos.getZ() + 0.5 + Math.sin(a) * f.rayon(), 1, 0, 0.2, 0, 0);
				}
		}
		return ItemInteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		if (level.isClientSide && FMLEnvironment.dist.isClient() && level.getBlockEntity(pos) instanceof FondationBlockEntity f)
			EcranClient.ouvrir(pos, f.nom());
		return InteractionResult.sidedSuccess(level.isClientSide);
	}

	@Override
	protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState neuf, boolean deplace) {
		if (!state.is(neuf.getBlock()) && level instanceof ServerLevel sl)
			FondationRegistre.de(sl.getServer()).retirer(level, pos);
		super.onRemove(state, level, pos, neuf, deplace);
	}
}
