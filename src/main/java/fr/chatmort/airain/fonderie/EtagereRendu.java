package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/** 1.71 : les objets posés sur l'étagère impériale (2 niveaux de 3 places), tournés vers l'avant du meuble. */
public class EtagereRendu implements BlockEntityRenderer<Mobilier.Presentoir> {
	public EtagereRendu(BlockEntityRendererProvider.Context c) {}

	@Override
	public void render(Mobilier.Presentoir be, float pt, PoseStack ms, MultiBufferSource buf, int lum, int ov) {
		var f = be.getBlockState().getValue(BlockStateProperties.HORIZONTAL_FACING);
		float y0 = switch (f) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };
		for (int i = 0; i < 6; i++) {
			ItemStack s = be.objets.get(i);
			if (s.isEmpty()) continue;
			ms.pushPose();
			// repère du modèle (avant au nord), tourné comme l'état du bloc
			ms.translate(0.5, 0, 0.5);
			ms.mulPose(Axis.YP.rotationDegrees(-y0));
			ms.translate(-0.5, 0, -0.5);
			double x = (1.5 + (i % 3 + 0.5) * 13 / 3.0) / 16, y = (i < 3 ? 1.5 : 8.5) / 16;
			ms.translate(x, y + 0.19, 9.5 / 16);
			ms.mulPose(Axis.YP.rotationDegrees(180));          // face de l'objet vers l'avant (nord du modèle)
			ms.scale(0.42f, 0.42f, 0.42f);
			Minecraft.getInstance().getItemRenderer().renderStatic(s, ItemDisplayContext.FIXED, lum, ov, ms, buf, be.getLevel(), (int) be.getBlockPos().asLong() + i);
			ms.popPose();
		}
	}
}
