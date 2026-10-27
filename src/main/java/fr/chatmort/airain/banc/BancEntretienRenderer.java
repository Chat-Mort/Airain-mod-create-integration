package fr.chatmort.airain.banc;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;

import fr.chatmort.airain.AirainPartials;
import net.createmod.catnip.render.CachedBuffers;
import net.createmod.catnip.render.SuperByteBuffer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Rouage central (comme la meule de Create), meule en pierre qui tourne sur le dessus,
 * jauge d'huile en façade et objets posés sur le plan de travail.
 */
public class BancEntretienRenderer extends KineticBlockEntityRenderer<BancEntretienBlockEntity> {

	public BancEntretienRenderer(BlockEntityRendererProvider.Context context) {
		super(context);
	}

	@Override
	protected SuperByteBuffer getRotatedModel(BancEntretienBlockEntity be, BlockState state) {
		return CachedBuffers.partial(AllPartialModels.MILLSTONE_COG, state);
	}

	@Override
	protected void renderSafe(BancEntretienBlockEntity be, float partialTicks, PoseStack ms, MultiBufferSource buffer,
							  int light, int overlay) {
		BlockState state = be.getBlockState();
		Direction facing = state.getValue(BancEntretienBlock.FACING);
		float yRot = switch (facing) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };

		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-yRot));
		ms.translate(-0.5, 0, -0.5);

		// Meule en pierre : tourne autour de son axe horizontal, deux fois plus vite que le rouage
		float angle = getAngleForBe(be, be.getBlockPos(), Direction.Axis.Y) * 2f;
		ms.pushPose();
		ms.translate(8 / 16f, 20.5f / 16f, 11 / 16f);
		ms.mulPose(Axis.XP.rotation(angle));
		ms.translate(-8 / 16f, -20.5f / 16f, -11 / 16f);
		CachedBuffers.partial(AirainPartials.MEULE, state).light(light).renderInto(ms, buffer.getBuffer(RenderType.solid()));
		ms.popPose();

		// Jauge d'huile : la colonne se remplit de gauche à droite
		float plein = be.reservoir.getFluidAmount() / (float) BancEntretienBlockEntity.CAPACITE;
		if (plein > 0.001f) {
			ms.pushPose();
			ms.translate(3.25f / 16f, 0, 0);
			ms.scale(Math.min(1f, plein), 1, 1);
			ms.translate(-3.25f / 16f, 0, 0);
			CachedBuffers.partial(AirainPartials.HUILE, state).light(light).renderInto(ms, buffer.getBuffer(RenderType.solid()));
			ms.popPose();
		}

		// Objets posés devant la meule
		ItemStack a = be.inventaire.getStackInSlot(0);
		ItemStack b = be.inventaire.getStackInSlot(1);
		ItemStack c = be.inventaire.getStackInSlot(2);
		poser(be, a.isEmpty() ? c : a, 0.33f, 0.3f, ms, buffer, light, overlay);
		poser(be, b, 0.68f, 0.3f, ms, buffer, light, overlay);
		ms.popPose();

		super.renderSafe(be, partialTicks, ms, buffer, light, overlay);
	}

	private void poser(BancEntretienBlockEntity be, ItemStack stack, float x, float z, PoseStack ms, MultiBufferSource buffer,
					   int light, int overlay) {
		if (stack.isEmpty())
			return;
		ms.pushPose();
		ms.translate(x, 1.0f + 1 / 32f, z);
		ms.mulPose(Axis.XP.rotationDegrees(90));
		ms.scale(0.32f, 0.32f, 0.32f);
		Minecraft.getInstance().getItemRenderer()
			.renderStatic(stack, ItemDisplayContext.FIXED, light, overlay, ms, buffer, be.getLevel(), 0);
		ms.popPose();
	}
}
