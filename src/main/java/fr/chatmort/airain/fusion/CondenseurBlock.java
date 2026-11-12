package fr.chatmort.airain.fusion;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * Condenseur d'Écho. Deux modes, changés d'un clic droit à main nue :
 * condenser (la source des jarres à 6 blocs devient de l'Écho liquide, que les tuyaux viennent prendre)
 * ou évaporer (l'Écho liquide versé par les tuyaux redevient de la source dans les jarres, avec 10 % de perte).
 */
public class CondenseurBlock extends BaseEntityBlock {
	public static final com.mojang.serialization.MapCodec<CondenseurBlock> CODEC = simpleCodec(CondenseurBlock::new);
	/** Vrai : évapore (liquide → jarres) ; faux : condense (jarres → liquide). */
	public static final BooleanProperty EVAPORE = BooleanProperty.create("evapore");

	public CondenseurBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(EVAPORE, false));
	}

	@Override
	protected com.mojang.serialization.MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(EVAPORE); }

	@Override
	protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new CondenseurBlockEntity(pos, state); }

	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> type) {
		return l.isClientSide || type != AirainMod.CONDENSEUR_BE.get() ? null : (lv, p, st, be) -> ((CondenseurBlockEntity) be).tickServeur();
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
		if (!l.isClientSide) {
			boolean ev = !s.getValue(EVAPORE);
			l.setBlock(p, s.setValue(EVAPORE, ev), Block.UPDATE_ALL);
			l.playSound(null, p, SoundEvents.COPPER_BULB_TURN_ON, SoundSource.BLOCKS, 0.8f, ev ? 0.7f : 1.2f);
			j.displayClientMessage(Component.translatable(ev ? "airain.condenseur.evapore" : "airain.condenseur.condense"), true);
		}
		return InteractionResult.sidedSuccess(l.isClientSide);
	}
}
