package fr.chatmort.airain.fusion;

import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;

import net.createmod.catnip.render.CachedBuffers;
import net.createmod.catnip.render.SuperByteBuffer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.level.block.state.BlockState;

/** Un demi-arbre de Create qui sort de la face avant (comme le moteur créatif). */
public class ArbreRenderer<T extends KineticBlockEntity> extends KineticBlockEntityRenderer<T> {
	public ArbreRenderer(BlockEntityRendererProvider.Context c) { super(c); }

	@Override
	protected SuperByteBuffer getRotatedModel(T be, BlockState state) { return CachedBuffers.partialFacing(AllPartialModels.SHAFT_HALF, state); }
}
