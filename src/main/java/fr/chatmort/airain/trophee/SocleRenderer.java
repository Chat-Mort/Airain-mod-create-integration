package fr.chatmort.airain.trophee;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/** Le trophée flotte et tourne lentement au-dessus du socle. */
public class SocleRenderer implements BlockEntityRenderer<SocleBlockEntity> {
	public SocleRenderer(BlockEntityRendererProvider.Context ctx) {}

	@Override
	public void render(SocleBlockEntity be, float pt, PoseStack ms, MultiBufferSource buffers, int light, int overlay) {
		ItemStack p = be.trophee();
		if (p.isEmpty() || be.getLevel() == null)
			return;
		float t = be.getLevel().getGameTime() + pt;
		ms.pushPose();
		ms.translate(0.5, 1.15 + Mth.sin(t / 20f) * 0.04, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(t * 1.5f));
		ms.scale(0.75f, 0.75f, 0.75f);
		Minecraft.getInstance().getItemRenderer().renderStatic(p, ItemDisplayContext.FIXED, light, OverlayTexture.NO_OVERLAY, ms, buffers, be.getLevel(), 0);
		ms.popPose();
	}
}
