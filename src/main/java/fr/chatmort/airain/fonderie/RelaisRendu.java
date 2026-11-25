package fr.chatmort.airain.fonderie;

import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;
import com.simibubi.create.content.kinetics.base.OrientedRotatingVisual;

import dev.engine_room.flywheel.lib.model.Models;
import dev.engine_room.flywheel.lib.visualization.SimpleBlockEntityVisualizer;
import net.createmod.catnip.render.CachedBuffers;
import net.createmod.catnip.render.SuperByteBuffer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;

/** 1.69.3 : le demi-arbre de Create qui entre par l'arrière du relais cinétique (dans le creux de la cage). */
public class RelaisRendu extends KineticBlockEntityRenderer<Relais.BE> {
	public RelaisRendu(BlockEntityRendererProvider.Context c) { super(c); }

	@Override
	protected SuperByteBuffer getRotatedModel(Relais.BE be, BlockState state) {
		return CachedBuffers.partialFacing(AllPartialModels.SHAFT_HALF, state, state.getValue(Relais.FACING).getOpposite());
	}

	/** Avec Flywheel : le même demi-arbre, en instance. */
	public static void visuel() {
		SimpleBlockEntityVisualizer.builder(Relais.BE_TYPE.get())
			.factory((ctx, be, pt) -> new OrientedRotatingVisual<>(ctx, be, pt, Direction.SOUTH,
				be.getBlockState().getValue(Relais.FACING).getOpposite(), Models.partial(AllPartialModels.SHAFT_HALF)))
			.skipVanillaRender(be -> false)
			.apply();
	}
}
