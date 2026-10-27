package fr.chatmort.airain.banc;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.simibubi.create.content.kinetics.base.ShaftRenderer;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/** Arbre de transmission (via Create) et objets posés à plat sur le plan de travail. */
public class BancEntretienRenderer extends ShaftRenderer<BancEntretienBlockEntity> {

	public BancEntretienRenderer(BlockEntityRendererProvider.Context context) {
		super(context);
	}

	@Override
	protected void renderSafe(BancEntretienBlockEntity be, float partialTicks, PoseStack ms, MultiBufferSource buffer,
							  int light, int overlay) {
		ItemStack a = be.inventaire.getStackInSlot(0);
		ItemStack b = be.inventaire.getStackInSlot(1);
		ItemStack c = be.inventaire.getStackInSlot(2);
		poser(be, a.isEmpty() ? c : a, 0.5f, 0.42f, ms, buffer, light, overlay);
		poser(be, b, 0.5f, 0.78f, ms, buffer, light, overlay);
		super.renderSafe(be, partialTicks, ms, buffer, light, overlay);
	}

	private void poser(BancEntretienBlockEntity be, ItemStack stack, float x, float z, PoseStack ms, MultiBufferSource buffer,
					   int light, int overlay) {
		if (stack.isEmpty())
			return;
		ms.pushPose();
		ms.translate(x, 1.0f + 1 / 32f, z);
		ms.mulPose(Axis.XP.rotationDegrees(90));
		ms.scale(0.45f, 0.45f, 0.45f);
		Minecraft.getInstance().getItemRenderer()
			.renderStatic(stack, ItemDisplayContext.FIXED, light, overlay, ms, buffer, be.getLevel(), 0);
		ms.popPose();
	}
}
