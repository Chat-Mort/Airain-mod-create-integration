package fr.chatmort.airain.borne;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;

import fr.chatmort.airain.AirainMod;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.inventory.InventoryMenu;

public class CaisseRenderer extends EntityRenderer<CaisseEntity> {
	public CaisseRenderer(EntityRendererProvider.Context c) { super(c); shadowRadius = 0.5f; }

	@Override
	public void render(CaisseEntity e, float yaw, float pt, PoseStack pose, MultiBufferSource buf, int lumiere) {
		var br = Minecraft.getInstance().getBlockRenderer();
		float s = e.echelle(pt);
		float t = e.age + pt;
		pose.pushPose();
		if (!e.posee()) {
			pose.mulPose(Axis.ZP.rotationDegrees(Mth.sin(t * 0.12f) * 6f));
			pose.mulPose(Axis.XP.rotationDegrees(Mth.cos(t * 0.09f) * 4f));
		}
		if (!e.empire() && s < 1f) pose.mulPose(Axis.YP.rotationDegrees((1 - s) * 360f));
		pose.scale(s, s, s);
		pose.translate(-0.5, 0, -0.5);
		br.renderSingleBlock((e.empire() ? AirainMod.CAISSE_IMPERIALE : AirainMod.CAISSE_ARCANIQUE).get().defaultBlockState(), pose, buf, lumiere, OverlayTexture.NO_OVERLAY);
		if (e.empire() && !e.posee()) br.renderSingleBlock(AirainMod.PARACHUTE.get().defaultBlockState(), pose, buf, lumiere, OverlayTexture.NO_OVERLAY);
		pose.popPose();
		super.render(e, yaw, pt, pose, buf, lumiere);
	}

	@Override
	public ResourceLocation getTextureLocation(CaisseEntity e) { return InventoryMenu.BLOCK_ATLAS; }
}
