package fr.chatmort.airain.balise;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;

/** Dessine toute la tour depuis le cœur : bâtisse, jambes, sirène tournante, phare et ses faisceaux. */
public class BaliseRenderer implements BlockEntityRenderer<BaliseBlockEntity> {
	private static final ResourceLocation TEX = ResourceLocation.fromNamespaceAndPath("airain", "textures/block/balise_tour.png");
	private static final int FONTE = 0, LAITON = 2, LAITON_S = 11, FAISCEAU = 12;
	private static final float C = 24f;

	public BaliseRenderer(BlockEntityRendererProvider.Context ctx) {}

	@Override
	public void render(BaliseBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int lumiere, int overlay) {
		if (be.getLevel() == null) return;
		int[] lum = new int[8];
		for (int k = 0; k < 8; k++) lum[k] = LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().above(k));
		var facing = be.getBlockState().getValue(BaliseBlock.FACING);
		float regime = Mth.lerp(pt, be.oRegime, be.regime);
		float angle = Mth.lerp(pt, be.oAngle, be.angle);

		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-facing.toYRot() + 180));
		ms.translate(-1.5, 0, -1.5);
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		VertexConsumer vc = buf.getBuffer(RenderType.entityCutoutNoCull(TEX));
		for (float[] b : BaliseGeo.FIXES) boite(vc, ms.last(), b, lum[ligne(b)], 255);
		// jambes de fonte, des angles du socle vers le fût
		for (int k = 0; k < 4; k++) {
			float sx = (k & 1) == 0 ? 1 : -1, sz = (k & 2) == 0 ? 1 : -1;
			float fx = C - sx * 20, fz = C - sz * 20, tx = C - sx * 8.5f, tz = C - sz * 8.5f;
			float dx = tx - fx, dz = tz - fz, dy = 30f, h = Mth.sqrt(dx * dx + dz * dz), lng = Mth.sqrt(h * h + dy * dy);
			ms.pushPose();
			ms.translate(fx, 6, fz);
			ms.mulPose(Axis.YP.rotation((float) Math.atan2(dx, dz)));
			ms.mulPose(Axis.XP.rotation((float) Math.atan2(h, dy)));
			boite(vc, ms.last(), new float[] {-1.5f, 0, -1.5f, 1.5f, lng, 1.5f, FONTE}, lum[1], 255);
			for (float y = 6; y < lng - 2; y += 9)
				boite(vc, ms.last(), new float[] {-2, y, -2, 2, y + 1.2f, 2, LAITON}, lum[1], 255);
			ms.popPose();
		}
		// la sirène : tourne autour de l'axe à mesure qu'elle monte en régime
		ms.pushPose();
		ms.translate(C, 0, C);
		ms.mulPose(Axis.YP.rotationDegrees(angle));
		for (float[] b : BaliseGeo.SIRENE) boite(vc, ms.last(), b, lum[2], 255);
		ms.popPose();
		// hublots et feu du phare : éclatants en alerte, sombres sinon
		int lampe = regime > 0.05f ? LightTexture.FULL_BRIGHT : lum[5];
		int teinte = (int) (110 + 145 * regime);
		for (float[] b : BaliseGeo.LAMPES) boite(vc, ms.last(), b, lampe, teinte);
		// vitres du phare
		VertexConsumer vitre = buf.getBuffer(RenderType.entityTranslucent(TEX));
		for (float[] b : BaliseGeo.VITRES) boite(vitre, ms.last(), b, lum[5], 255);
		// faisceaux tournants
		if (regime > 0.05f) {
			VertexConsumer f = buf.getBuffer(RenderType.entityTranslucentEmissive(TEX));
			ms.pushPose();
			ms.translate(C, 94, C);
			ms.mulPose(Axis.YP.rotationDegrees(-angle * 0.6f));
			for (int s = 0; s < 2; s++) {
				ms.mulPose(Axis.YP.rotationDegrees(180));
				faisceau(f, ms.last(), regime);
			}
			ms.popPose();
		}
		ms.popPose();
	}

	private static int ligne(float[] b) { return Mth.clamp((int) ((b[1] + b[4]) / 32f), 0, 7); }

	/** Faisceau : pyramide tronquée qui s'élargit et s'efface en s'éloignant (5 blocs). */
	private static void faisceau(VertexConsumer vc, PoseStack.Pose p, float regime) {
		float x0 = 7, x1 = 80, r0 = 3, r1 = 14;
		int a = (int) (200 * regime);
		float u0 = (FAISCEAU % 4) * 16 / 64f, v0 = (FAISCEAU / 4) * 16 / 64f, u1 = u0 + 16 / 64f, v1 = v0 + 16 / 64f;
		// quatre faces : dessus, dessous, gauche, droite
		quadF(vc, p, x0, r0, -r0, x1, r1, -r1, x1, r1, r1, x0, r0, r0, u0, v0, u1, v1, a);
		quadF(vc, p, x0, -r0, -r0, x1, -r1, -r1, x1, -r1, r1, x0, -r0, r0, u0, v0, u1, v1, a);
		quadF(vc, p, x0, -r0, -r0, x1, -r1, -r1, x1, r1, -r1, x0, r0, -r0, u0, v0, u1, v1, a);
		quadF(vc, p, x0, -r0, r0, x1, -r1, r1, x1, r1, r1, x0, r0, r0, u0, v0, u1, v1, a);
	}

	private static void quadF(VertexConsumer vc, PoseStack.Pose p, float ax, float ay, float az, float bx, float by, float bz,
							  float cx, float cy, float cz, float dx, float dy, float dz, float u0, float v0, float u1, float v1, int a) {
		vc.addVertex(p, ax, ay, az).setColor(255, 90, 60, a).setUv(u0, v0).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(p, 0, 1, 0);
		vc.addVertex(p, bx, by, bz).setColor(255, 90, 60, 0).setUv(u0, v1).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(p, 0, 1, 0);
		vc.addVertex(p, cx, cy, cz).setColor(255, 90, 60, 0).setUv(u1, v1).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(p, 0, 1, 0);
		vc.addVertex(p, dx, dy, dz).setColor(255, 90, 60, a).setUv(u1, v0).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(p, 0, 1, 0);
	}

	/** Boîte texturée : chaque face est découpée en carreaux de 16 px pour répéter la texture du matériau. */
	static void boite(VertexConsumer vc, PoseStack.Pose p, float[] b, int lum, int teinte) {
		float x0 = b[0], y0 = b[1], z0 = b[2], x1 = b[3], y1 = b[4], z1 = b[5];
		int m = (int) b[6];
		float tu = (m % 4) * 16, tv = (m / 4) * 16;
		// (origine, axe u, axe v, normale) pour chaque face
		face(vc, p, lum, teinte, tu, tv, x0, y1, z0, x1 - x0, 0, 0, 0, 0, z1 - z0, 0, 1, 0);      // dessus
		face(vc, p, lum, teinte, tu, tv, x0, y0, z1, x1 - x0, 0, 0, 0, 0, z0 - z1, 0, -1, 0);     // dessous
		face(vc, p, lum, teinte, tu, tv, x1, y1, z0, x0 - x1, 0, 0, 0, y0 - y1, 0, 0, 0, -1);     // nord
		face(vc, p, lum, teinte, tu, tv, x0, y1, z1, x1 - x0, 0, 0, 0, y0 - y1, 0, 0, 0, 1);      // sud
		face(vc, p, lum, teinte, tu, tv, x0, y1, z0, 0, 0, z1 - z0, 0, y0 - y1, 0, -1, 0, 0);     // ouest
		face(vc, p, lum, teinte, tu, tv, x1, y1, z1, 0, 0, z0 - z1, 0, y0 - y1, 0, 1, 0, 0);      // est
	}

	private static void face(VertexConsumer vc, PoseStack.Pose p, int lum, int teinte, float tu, float tv,
							 float ox, float oy, float oz, float ux, float uy, float uz, float vx, float vy, float vz,
							 float nx, float ny, float nz) {
		float lu = Math.abs(ux + uy + uz), lv = Math.abs(vx + vy + vz);
		if (lu < 0.01f || lv < 0.01f) return;
		for (float a = 0; a < lu - 0.001f; a += 16) {
			float a1 = Math.min(lu, a + 16);
			for (float c = 0; c < lv - 0.001f; c += 16) {
				float c1 = Math.min(lv, c + 16);
				float[][] pts = {{a, c}, {a1, c}, {a1, c1}, {a, c1}};
				for (float[] q : pts) {
					float fu = q[0] / lu, fv = q[1] / lv;
					float x = ox + ux * fu + vx * fv, y = oy + uy * fu + vy * fv, z = oz + uz * fu + vz * fv;
					float u = (tu + (q[0] - a)) / 64f, v = (tv + (q[1] - c)) / 64f;
					vc.addVertex(p, x, y, z).setColor(teinte, teinte, teinte, 255).setUv(u, v)
						.setOverlay(OverlayTexture.NO_OVERLAY).setLight(lum).setNormal(p, nx, ny, nz);
				}
			}
		}
	}

	@Override
	public boolean shouldRenderOffScreen(BaliseBlockEntity be) { return true; }

	@Override
	public int getViewDistance() { return 160; }

	public AABB getRenderBoundingBox(BaliseBlockEntity be) { return be.boite(); }
}
