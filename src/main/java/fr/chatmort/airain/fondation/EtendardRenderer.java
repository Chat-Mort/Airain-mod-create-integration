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
	private static final ResourceLocation FER = ResourceLocation.fromNamespaceAndPath("create", "textures/block/industrial_iron_block.png");
	private static final ResourceLocation LAITON = ResourceLocation.fromNamespaceAndPath("create", "textures/block/brass_block.png");

	/** Géométrie d'une bannière : style, taille (grand étendard) et force du vent. */
	private record Geo(int style, boolean grand, float w, float l, float vent) {}

	public EtendardRenderer(BlockEntityRendererProvider.Context ctx) {}

	@Override
	public void render(FondationBlockEntity be, float pt, PoseStack ms, MultiBufferSource buffers, int light, int overlay) {
		if (be.getLevel() == null) return;
		Apparence a = be.apparence();
		float t = be.getLevel().getGameTime() + pt + (be.getBlockPos().asLong() % 97);
		boolean grand = be.getBlockState().getBlock() instanceof GrandEtendardBlock;
		int lum = LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().above(grand ? 5 : 1));
		Direction face = be.getBlockState().getValue(FondationBlock.FACING);
		Geo geo = grand ? new Geo(a.style(), true, Apparence.LARGEURS[a.largeur()], Apparence.LONGUEURS[a.longueur()], Apparence.VENTS[a.vent()])
			: new Geo(a.style(), false, 0, 0, 1);
		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-face.toYRot() + 180));   // nord = 0
		ms.translate(-0.5, 0, -0.5);
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		ResourceLocation motif = a.texMotif();
		int fond = Apparence.FONDS[a.fond()], orn = Apparence.ORNEMENTS[a.ornement()];
		if (grand) ferrures(ms, buffers, geo, lum);
		calque(ms, buffers, geo, a.texFond(), fond, 0, t, lum);
		if (motif != null) calque(ms, buffers, geo, motif, orn, 1, t, lum);
		calque(ms, buffers, geo, a.texOrnement(), orn, 2, t, lum);
		ms.popPose();
	}

	/** Un calque, recto (+eps) et verso (−eps) pour rester visible des deux côtés. */
	private void calque(PoseStack ms, MultiBufferSource buffers, Geo geo, ResourceLocation tex, int couleur, int rang, float t, int lum) {
		VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(tex));
		int r = couleur >> 16 & 255, g = couleur >> 8 & 255, b = couleur & 255;
		if (rang == 0) { tissu(ms, vc, geo, 0, t, lum, r, g, b); return; }
		tissu(ms, vc, geo, EPS * rang, t, lum, r, g, b);
		tissu(ms, vc, geo, -EPS * rang, t, lum, r, g, b);
	}

	private void tissu(PoseStack ms, VertexConsumer vc, Geo geo, float decal, float t, int lum, int r, int g, int b) {
		int style = geo.style();
		int nu = geo.grand() ? 12 : style == 2 ? 16 : 8, nv = geo.grand() ? 24 : style == 2 ? 8 : 16;
		PoseStack.Pose pose = ms.last();
		for (int i = 0; i < nu; i++)
			for (int j = 0; j < nv; j++) {
				float u0 = i / (float) nu, u1 = (i + 1) / (float) nu, v0 = j / (float) nv, v1 = (j + 1) / (float) nv;
				float[] p00 = point(geo, u0, v0, t, decal), p10 = point(geo, u1, v0, t, decal);
				float[] p11 = point(geo, u1, v1, t, decal), p01 = point(geo, u0, v1, t, decal);
				sommet(vc, pose, p00, style, u0, v0, lum, r, g, b);
				sommet(vc, pose, p01, style, u0, v1, lum, r, g, b);
				sommet(vc, pose, p11, style, u1, v1, lum, r, g, b);
				sommet(vc, pose, p10, style, u1, v0, lum, r, g, b);
			}
	}

	/** Position d'un point du tissu : (u, v) dans le maillage, ondulation selon le temps. */
	private static float[] point(Geo geo, float u, float v, float t, float decal) {
		if (geo.grand()) return pointGrand(geo, u, v, t, decal);
		switch (geo.style()) {
			case 0 -> {   // potence : suspendue sous le bras, sur le côté
				float x = 16 + u * 11, y = 44.5f - v * 22, z = 8;
				float o = 1.3f * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.10f + v * 4f + u * 2f);
				return new float[] {x, y, z + o + decal};
			}
			case 1 -> {   // vexillum : devant le piédestal, sous la traverse
				float x = 1 + u * 14, y = 44.5f - v * 28, z = -1.2f;
				float o = 1.1f * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.09f + v * 3.5f + u * 1.5f);
				return new float[] {x, y, z - Math.abs(o) * 0.6f + o * 0.4f + decal};
			}
			default -> {  // cérémonie : le long du mât, flotte à l'horizontale ; u = hauteur, v = longueur
				float s = v, x = 9.5f + s * 16, y = 46.5f - u * 12 - 0.8f * s * s, z = 8;
				float o = 1.6f * (float) Math.pow(s, 1.1) * Mth.sin(t * 0.16f - s * 5f + u * 1f);
				return new float[] {x, y, z + o + decal};
			}
		}
	}

	/** Grand étendard : sommet du mât à 108 px ; la bannière part juste sous les ferrures. */
	private static float[] pointGrand(Geo geo, float u, float v, float t, float decal) {
		float W = geo.w(), L = geo.l(), vent = geo.vent(), vit = 0.7f + 0.3f * vent;
		switch (geo.style()) {
			case 0 -> {   // potence : pend sous le bras
				float x = 10.5f + u * W, y = 102.5f - v * L, z = 8;
				float o = 2.2f * vent * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.08f * vit + v * 3f + u * 2f);
				return new float[] {x, y, z + o + decal};
			}
			case 1 -> {   // vexillum : pend sous la traverse, devant le mât
				float x = 8 - W / 2 + u * W, y = 101.5f - v * L, z = -2f;
				float o = 1.8f * vent * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.07f * vit + v * 3f + u * 1.5f);
				return new float[] {x, y, z - Math.abs(o) * 0.6f + o * 0.4f + decal};
			}
			default -> {  // cérémonie : flotte à l'horizontale ; u = hauteur, v = longueur
				float s = v, x = 9.5f + s * L, y = 104f - u * W - Math.min(10f, 2.4f / vent) * s * s, z = 8;
				float o = 2.6f * vent * (float) Math.pow(s, 1.1) * Mth.sin(t * 0.13f * vit - s * 5f + u);
				return new float[] {x, y, z + o + decal};
			}
		}
	}

	/** Bras, traverse ou anneaux du grand étendard : leur taille suit la largeur de la bannière. */
	private void ferrures(PoseStack ms, MultiBufferSource buffers, Geo geo, int lum) {
		VertexConsumer fer = buffers.getBuffer(RenderType.entityCutoutNoCull(FER));
		float W = geo.w();
		switch (geo.style()) {
			case 0 -> {
				boite(ms, fer, 9.5f, 102.5f, 7.25f, 12.5f + W, 104f, 8.75f, lum);
				boite(ms, fer, 9.5f, 99f, 7.5f, 11f, 102.5f, 8.5f, lum);                       // jambe de force
				VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
				boite(ms, or, 11.5f + W, 102f, 7f, 13.5f + W, 104.5f, 9f, lum);               // embout
				boite(ms, or, 5.5f, 101.5f, 5.5f, 10.5f, 103f, 10.5f, lum);                   // collier
			}
			case 1 -> {
				boite(ms, fer, 7.25f, 101f, -2.5f, 8.75f, 102.5f, 6f, lum);                    // potence avant
				boite(ms, fer, 8 - W / 2 - 1, 101.5f, -2.75f, 8 + W / 2 + 1, 103f, -1.25f, lum); // traverse
				VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
				boite(ms, or, 8 - W / 2 - 2.5f, 101f, -3.25f, 8 - W / 2 - 1, 103.5f, -0.75f, lum);
				boite(ms, or, 8 + W / 2 + 1, 101f, -3.25f, 8 + W / 2 + 2.5f, 103.5f, -0.75f, lum);
				boite(ms, or, 5.5f, 100.5f, 5.5f, 10.5f, 102f, 10.5f, lum);
			}
			default -> {
				VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
				boite(ms, or, 5.5f, 103.5f, 5.5f, 10.5f, 105f, 10.5f, lum);                   // anneaux qui tiennent la hampe
				boite(ms, or, 5.5f, 103.5f - W, 5.5f, 10.5f, 105f - W, 10.5f, lum);
			}
		}
	}

	/** Pavé texturé (coordonnées en pixels). */
	private static void boite(PoseStack ms, VertexConsumer vc, float x0, float y0, float z0, float x1, float y1, float z1, int lum) {
		PoseStack.Pose p = ms.last();
		float du = Math.min(1f, (x1 - x0) / 16f), dv = Math.min(1f, (y1 - y0) / 16f), dw = Math.min(1f, (z1 - z0) / 16f);
		face(vc, p, lum, 0, 0, -1, du, dv, x1, y1, z0, x0, y1, z0, x0, y0, z0, x1, y0, z0);
		face(vc, p, lum, 0, 0, 1, du, dv, x0, y1, z1, x1, y1, z1, x1, y0, z1, x0, y0, z1);
		face(vc, p, lum, -1, 0, 0, dw, dv, x0, y1, z0, x0, y1, z1, x0, y0, z1, x0, y0, z0);
		face(vc, p, lum, 1, 0, 0, dw, dv, x1, y1, z1, x1, y1, z0, x1, y0, z0, x1, y0, z1);
		face(vc, p, lum, 0, 1, 0, du, dw, x0, y1, z0, x1, y1, z0, x1, y1, z1, x0, y1, z1);
		face(vc, p, lum, 0, -1, 0, du, dw, x0, y0, z1, x1, y0, z1, x1, y0, z0, x0, y0, z0);
	}

	private static void face(VertexConsumer vc, PoseStack.Pose p, int lum, float nx, float ny, float nz, float du, float dv, float... q) {
		float[][] uv = {{0, 0}, {du, 0}, {du, dv}, {0, dv}};
		for (int k = 0; k < 4; k++)
			vc.addVertex(p, q[k * 3], q[k * 3 + 1], q[k * 3 + 2]).setColor(255, 255, 255, 255).setUv(uv[k][0], uv[k][1])
				.setOverlay(OverlayTexture.NO_OVERLAY).setLight(lum).setNormal(p, nx, ny, nz);
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
		if (be.getBlockState().getBlock() instanceof GrandEtendardBlock)
			return new AABB(be.getBlockPos()).inflate(3.5, 0, 3.5).expandTowards(0, 8, 0);
		return new AABB(be.getBlockPos()).inflate(1.5, 0, 1.5).expandTowards(0, 3, 0);
	}
}
