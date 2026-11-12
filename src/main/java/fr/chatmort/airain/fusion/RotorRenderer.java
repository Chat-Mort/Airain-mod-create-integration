package fr.chatmort.airain.fusion;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;

import dev.engine_room.flywheel.lib.model.baked.PartialModel;
import net.createmod.catnip.render.CachedBuffers;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * Le demi-arbre de Create (ArbreRenderer) plus une pièce qui tourne avec la machine :
 * les pales de la turbine (autour de l'axe de l'arbre) ou l'engrenage et la gemme du sourcelink (autour de la verticale du modèle).
 * La pièce est dessinée tournée comme le bloc (mêmes rotations que le blockstate, modèle dessiné face au nord).
 */
public class RotorRenderer<T extends KineticBlockEntity> extends ArbreRenderer<T> {
	private final PartialModel piece;
	private final boolean autourDeLArbre;

	public RotorRenderer(BlockEntityRendererProvider.Context c, PartialModel piece, boolean autourDeLArbre) {
		super(c); this.piece = piece; this.autourDeLArbre = autourDeLArbre;
	}

	@Override
	protected void renderSafe(T be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
		super.renderSafe(be, pt, ms, buf, light, overlay);            // l'arbre (sans Flywheel)
		BlockState s = be.getBlockState();
		Direction f = s.getValue(BlockStateProperties.FACING);
		int y = switch (f) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };
		int x = f == Direction.UP ? 270 : f == Direction.DOWN ? 90 : 0;
		float angle = getAngleForBe(be, be.getBlockPos(), f.getAxis());
		ms.pushPose();
		ms.translate(0.5, 0.5, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-y));                         // comme le blockstate
		ms.mulPose(Axis.XP.rotationDegrees(-x));
		if (autourDeLArbre) ms.mulPose(Axis.ZP.rotation(angle));         // les pales tournent autour de l'arbre (axe nord-sud du modèle)
		else ms.mulPose(Axis.YP.rotation(angle));                         // l'engrenage tourne à plat sur le dessus
		ms.translate(-0.5, -0.5, -0.5);
		CachedBuffers.partial(piece, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutoutMipped()));
		ms.popPose();
	}
}
