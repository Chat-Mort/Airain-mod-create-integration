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
 * Sourcelink mécanique : entraîné par un arbre de Create (face avant), il produit de la source
 * et la verse dans les jarres à 6 blocs. Plus il tourne vite, plus il en produit.
 */
public class SourcelinkMecaBlock extends DirectionalKineticBlock implements IBE<SourcelinkMecaBlockEntity> {
	public SourcelinkMecaBlock(Properties p) { super(p); }

	@Override
	public boolean hasShaftTowards(LevelReader l, BlockPos pos, BlockState state, Direction face) { return face == state.getValue(FACING); }

	@Override
	public Axis getRotationAxis(BlockState state) { return state.getValue(FACING).getAxis(); }

	@Override
	public Class<SourcelinkMecaBlockEntity> getBlockEntityClass() { return SourcelinkMecaBlockEntity.class; }

	@Override
	public BlockEntityType<? extends SourcelinkMecaBlockEntity> getBlockEntityType() { return AirainMod.SOURCELINK_MECA_BE.get(); }
}
