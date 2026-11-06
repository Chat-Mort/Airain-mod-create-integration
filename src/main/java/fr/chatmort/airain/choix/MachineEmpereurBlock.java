package fr.chatmort.airain.choix;

import com.mojang.serialization.MapCodec;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * La machine de l'Empereur, au berceau : elle apparaît, éteinte, là où l'Empereur est tombé.
 * ETAT 0 : éteinte · 1 : le Cœur éteint y est posé (clic droit à main nue pour le reprendre)
 * · 2 : rallumée par un cœur du Gardien des enfers (fin Empire, définitif). Incassable.
 */
public class MachineEmpereurBlock extends HorizontalDirectionalBlock {
	public static final MapCodec<MachineEmpereurBlock> CODEC = simpleCodec(MachineEmpereurBlock::new);
	public static final IntegerProperty ETAT = IntegerProperty.create("etat", 0, 2);
	private static final VoxelShape FORME = Block.box(0, 0, 0, 16, 16, 16);

	public MachineEmpereurBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(ETAT, 0));
	}

	@Override
	protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, ETAT); }

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }

	/** Poser le Cœur (état 0), puis l'allumer avec le cœur du Gardien des enfers (état 1). */
	@Override
	protected ItemInteractionResult useItemOn(ItemStack pile, BlockState state, Level level, BlockPos pos, Player joueur, InteractionHand main, BlockHitResult hit) {
		if (!(level instanceof ServerLevel sl) || !(joueur instanceof ServerPlayer p)) return ItemInteractionResult.sidedSuccess(level.isClientSide);
		int etat = state.getValue(ETAT);
		var fin = fr.chatmort.airain.gardien.Fin.de(sl.getServer());
		if (fin.echo()) { p.displayClientMessage(Component.translatable("airain.choix.machine.trop_tard"), true); return ItemInteractionResult.SUCCESS; }
		if (etat == 0 && ChoixFinal.coeur(pile)) {                                   // le Cœur se loge dans la niche
			if (!p.getAbilities().instabuild) pile.shrink(1);
			level.setBlock(pos, state.setValue(ETAT, 1), Block.UPDATE_ALL);
			level.playSound(null, pos, SoundEvents.IRON_TRAPDOOR_OPEN, SoundSource.BLOCKS, 1f, 0.6f);
			level.playSound(null, pos, SoundEvents.ARMOR_EQUIP_IRON.value(), SoundSource.BLOCKS, 1f, 0.7f);
			p.displayClientMessage(Component.translatable("airain.choix.machine.pose"), true);
			return ItemInteractionResult.SUCCESS;
		}
		if (pile.is(net.minecraft.world.item.Items.NETHER_STAR)) {
			if (etat == 0) { p.displayClientMessage(Component.translatable("airain.choix.machine.coeur_d_abord"), true); return ItemInteractionResult.SUCCESS; }
			if (etat == 1 && ChoixFinal.choisir(p, "empire")) {                          // fin Empire : la machine repart
				if (!p.getAbilities().instabuild) pile.shrink(1);
				level.setBlock(pos, state.setValue(ETAT, 2), Block.UPDATE_ALL);
				ChoixFinal.rallumer(sl, pos);
			}
			return ItemInteractionResult.SUCCESS;
		}
		return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
	}

	/** Main nue : reprendre le Cœur tant que la machine n'est pas rallumée. */
	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player joueur, BlockHitResult hit) {
		if (level.isClientSide) return InteractionResult.SUCCESS;
		int etat = state.getValue(ETAT);
		if (etat == 1) {
			level.setBlock(pos, state.setValue(ETAT, 0), Block.UPDATE_ALL);
			joueur.getInventory().placeItemBackInInventory(ChoixFinal.coeurEteint());
			level.playSound(null, pos, SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.BLOCKS, 1f, 0.6f);
		} else joueur.displayClientMessage(Component.translatable(etat == 2 ? "airain.choix.machine.bat" : "airain.choix.machine.aide"), true);
		return InteractionResult.SUCCESS;
	}

	/** Rallumée : un peu de vapeur de temps en temps. */
	@Override
	public void animateTick(BlockState s, Level l, BlockPos p, net.minecraft.util.RandomSource r) {
		if (s.getValue(ETAT) == 2 && r.nextInt(3) == 0)
			l.addParticle(ParticleTypes.CLOUD, p.getX() + 0.15 + r.nextDouble() * 0.1, p.getY() + 2.05, p.getZ() + 0.75, 0, 0.06, 0);
	}
}
