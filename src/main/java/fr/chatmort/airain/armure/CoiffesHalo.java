package fr.chatmort.airain.armure;

import com.mojang.blaze3d.vertex.PoseStack;

import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.entity.EquipmentSlot;

/** Le halo du Nimbe : un anneau en pleine lumière qui flotte et ondule au-dessus de la tête. */
public class CoiffesHalo extends RenderLayer<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> {
	private final ModelPart halo;

	public CoiffesHalo(RenderLayerParent<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> parent, EntityModelSet modeles) {
		super(parent);
		this.halo = modeles.bakeLayer(CoiffesModele.HALO);
	}

	@Override
	public void render(PoseStack pose, MultiBufferSource tampons, int lumiere, AbstractClientPlayer p, float balancement, float amplitude,
			float partiel, float age, float lacet, float tangage) {
		if (p.isInvisible() || !p.getItemBySlot(EquipmentSlot.HEAD).is(fr.chatmort.airain.AirainMod.CASQUE_ARCANIQUE.get())) return;
		pose.pushPose();
		getParentModel().head.translateAndRotate(pose);
		pose.translate(0, Math.sin(age * 0.08f) * 0.03f, 0);
		halo.render(pose, tampons.getBuffer(RenderType.entityCutoutNoCull(CoiffesModele.TEXTURE)), 0xF000F0, OverlayTexture.NO_OVERLAY);
		pose.popPose();
	}
}
