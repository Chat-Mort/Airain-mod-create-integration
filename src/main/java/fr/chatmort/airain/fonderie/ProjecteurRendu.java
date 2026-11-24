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

/** 1.69.1 : le demi-arbre de Create qui entre par le dessous du projecteur de chantier. */
public class ProjecteurRendu extends KineticBlockEntityRenderer<Projecteur.BE> {
	public ProjecteurRendu(BlockEntityRendererProvider.Context c) { super(c); }

	@Override
	protected SuperByteBuffer getRotatedModel(Projecteur.BE be, BlockState state) {
		return CachedBuffers.partialFacing(AllPartialModels.SHAFT_HALF, state, Direction.DOWN);
	}

	/** Avec Flywheel : le même demi-arbre, en instance. */
	public static void visuel() {
		SimpleBlockEntityVisualizer.builder(Projecteur.BE_TYPE.get())
			.factory((ctx, be, pt) -> new OrientedRotatingVisual<>(ctx, be, pt, Direction.SOUTH, Direction.DOWN, Models.partial(AllPartialModels.SHAFT_HALF)))
			.skipVanillaRender(be -> false)
			.apply();
	}
}
