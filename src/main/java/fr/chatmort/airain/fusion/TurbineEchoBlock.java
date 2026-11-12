package fr.chatmort.airain.fusion;

import com.simibubi.create.content.kinetics.base.DirectionalKineticBlock;
import com.simibubi.create.foundation.block.IBE;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Direction.Axis;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Turbine d'Écho : un moteur de Create qui brûle la source d'Ars Nouveau.
 * L'arbre sort sur la face avant ; elle puise la source des jarres à 6 blocs et tourne à 64 tr/min tant qu'il y en a.
 */
public class TurbineEchoBlock extends DirectionalKineticBlock implements IBE<TurbineEchoBlockEntity> {
	public TurbineEchoBlock(Properties p) { super(p); }

	@Override
	public boolean hasShaftTowards(LevelReader l, BlockPos pos, BlockState state, Direction face) { return face == state.getValue(FACING); }

	@Override
	public Axis getRotationAxis(BlockState state) { return state.getValue(FACING).getAxis(); }

	@Override
	public boolean hideStressImpact() { return true; }   // elle fournit de la force, elle n'en consomme pas

	@Override
	public Class<TurbineEchoBlockEntity> getBlockEntityClass() { return TurbineEchoBlockEntity.class; }

	@Override
	public BlockEntityType<? extends TurbineEchoBlockEntity> getBlockEntityType() { return AirainMod.TURBINE_ECHO_BE.get(); }
}
