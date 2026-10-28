package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;

/**
 * Bannière de l'étendard : un tissu maillé qui ondule au vent, peint en trois calques teintés (fond, motif, ornements).
 * Coordonnées en pixels, devant = nord, comme les modèles du mât.
 */
public class EtendardRenderer implements BlockEntityRenderer<FondationBlockEntity> {
	private static final float EPS = 0.012f;

	public EtendardRenderer(BlockEntityRendererProvider.Context ctx) {}

	@Override
	public void render(FondationBlockEntity be, float pt, PoseStack ms, MultiBufferSource buffers, int light, int overlay) {
		if (be.getLevel() == null) return;
		Apparence a = be.apparence();
		float t = be.getLevel().getGameTime() + pt + (be.getBlockPos().asLong() % 97);
		int lum = LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().above());
		Direction face = be.getBlockState().getValue(FondationBlock.FACING);
		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-face.toYRot() + 180));   // nord = 0
		ms.translate(-0.5, 0, -0.5);
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		ResourceLocation motif = a.texMotif();
		int fond = Apparence.FONDS[a.fond()], orn = Apparence.ORNEMENTS[a.ornement()];
		calque(ms, buffers, a, a.texFond(), fond, 0, t, lum);
		if (motif != null) calque(ms, buffers, a, motif, orn, 1, t, lum);
		calque(ms, buffers, a, a.texOrnement(), orn, 2, t, lum);
		ms.popPose();
	}

	/** Un calque, recto (+eps) et verso (−eps) pour rester visible des deux côtés. */
	private void calque(PoseStack ms, MultiBufferSource buffers, Apparence a, ResourceLocation tex, int couleur, int rang, float t, int lum) {
		VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(tex));
		int r = couleur >> 16 & 255, g = couleur >> 8 & 255, b = couleur & 255;
		if (rang == 0) { tissu(ms, vc, a.style(), 0, t, lum, r, g, b); return; }
		tissu(ms, vc, a.style(), EPS * rang, t, lum, r, g, b);
		tissu(ms, vc, a.style(), -EPS * rang, t, lum, r, g, b);
	}

	private void tissu(PoseStack ms, VertexConsumer vc, int style, float decal, float t, int lum, int r, int g, int b) {
		int nu = style == 2 ? 16 : 8, nv = style == 2 ? 8 : 16;
		PoseStack.Pose pose = ms.last();
		for (int i = 0; i < nu; i++)
			for (int j = 0; j < nv; j++) {
				float u0 = i / (float) nu, u1 = (i + 1) / (float) nu, v0 = j / (float) nv, v1 = (j + 1) / (float) nv;
				float[] p00 = point(style, u0, v0, t, decal), p10 = point(style, u1, v0, t, decal);
				float[] p11 = point(style, u1, v1, t, decal), p01 = point(style, u0, v1, t, decal);
				sommet(vc, pose, p00, style, u0, v0, lum, r, g, b);
				sommet(vc, pose, p01, style, u0, v1, lum, r, g, b);
				sommet(vc, pose, p11, style, u1, v1, lum, r, g, b);
				sommet(vc, pose, p10, style, u1, v0, lum, r, g, b);
			}
	}

	/** Position d'un point du tissu : (u, v) dans le maillage, ondulation selon le temps. */
	private static float[] point(int style, float u, float v, float t, float decal) {
		switch (style) {
			case 0 -> {   // potence : suspendue sous le bras, sur le côté
				float x = 16 + u * 11, y = 28.5f - v * 22, z = 8;
				float o = 1.3f * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.10f + v * 4f + u * 2f);
				return new float[] {x, y, z + o + decal};
			}
			case 1 -> {   // vexillum : devant le piédestal, sous la traverse
				float x = 1 + u * 14, y = 28.5f - v * 28, z = -1.2f;
				float o = 1.1f * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.09f + v * 3.5f + u * 1.5f);
				return new float[] {x, y, z - Math.abs(o) * 0.6f + o * 0.4f + decal};
			}
			default -> {  // cérémonie : le long du mât, flotte à l'horizontale ; u = hauteur, v = longueur
				float s = v, x = 9.5f + s * 16, y = 30.5f - u * 12 - 0.8f * s * s, z = 8;
				float o = 1.6f * (float) Math.pow(s, 1.1) * Mth.sin(t * 0.16f - s * 5f + u * 1f);
				return new float[] {x, y, z + o + decal};
			}
		}
	}

	private static void sommet(VertexConsumer vc, PoseStack.Pose pose, float[] p, int style, float u, float v, int lum, int r, int g, int b) {
		vc.addVertex(pose, p[0], p[1], p[2]).setColor(r, g, b, 255).setUv(u, v)
			.setOverlay(OverlayTexture.NO_OVERLAY).setLight(lum).setNormal(pose, 0, 0, 1);
	}

	@Override
	public boolean shouldRenderOffScreen(FondationBlockEntity be) {
		return true;
	}

	public AABB getRenderBoundingBox(FondationBlockEntity be) {
		return new AABB(be.getBlockPos()).inflate(1.5, 0, 1.5).expandTowards(0, 2, 0);
	}
}
