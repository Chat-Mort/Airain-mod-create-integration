package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.phys.AABB;

/**
 * Bannière de l'étendard : un tissu maillé qui ondule au vent, peint avec la toile composée par TexturesBanniere.
 * Coordonnées en pixels, devant = nord, comme les modèles du mât.
 */
public class EtendardRenderer implements BlockEntityRenderer<FondationBlockEntity> {
	private static final float EPS = 0.012f;
	private static final ResourceLocation FER = ResourceLocation.fromNamespaceAndPath("create", "textures/block/industrial_iron_block.png");
	private static final ResourceLocation LAITON = ResourceLocation.fromNamespaceAndPath("create", "textures/block/brass_block.png");

	/** Géométrie d'une bannière : style, taille (grand étendard) et force du vent. */
	private record Geo(int style, boolean grand, boolean murale, float w, float l, float vent, int forme, boolean lanternes, float meteo) {}
	private static final ResourceLocation OR = ResourceLocation.withDefaultNamespace("textures/block/gold_block.png");
	private static final ResourceLocation FRANGE = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/etendard/frange.png");
	private static final int PLEIN_FEU = LightTexture.FULL_BRIGHT;

	public EtendardRenderer(BlockEntityRendererProvider.Context ctx) {}

	@Override
	public void render(FondationBlockEntity be, float pt, PoseStack ms, MultiBufferSource buffers, int light, int overlay) {
		if (be.getLevel() == null) return;
		Apparence a = be.apparence();
		float t = be.getLevel().getGameTime() + pt + (a.synchronise() ? 0 : be.getBlockPos().asLong() % 97);   // vent commun : même phase partout
		boolean grand = be.grand(), murale = be.murale();
		float meteo = be.meteo(), hisse = be.hisse(pt);
		int lum = LevelRenderer.getLightColor(be.getLevel(), murale ? be.getBlockPos() : be.getBlockPos().above(grand ? be.hauteur() - 1 : 1));
		Direction face = be.getBlockState().getValue(FondationBlock.FACING);
		Geo geo;
		if (grand) geo = new Geo(a.style(), true, false, Apparence.LARGEURS[a.largeur()], Apparence.LONGUEURS[a.longueur()],
			Apparence.VENTS[a.vent()] * meteo, a.forme(), a.avecLanternes(), meteo);
		else if (murale) geo = new Geo(1, false, true, BanniereMuraleBlock.LARGEURS[a.largeur()],
			BanniereMuraleBlock.LONGUEURS[a.longueur()] * (1 - 0.8f * hisse), Apparence.VENTS[a.vent()] * meteo, a.forme(), a.avecLanternes(), meteo);
		else geo = new Geo(a.style(), false, false, 0, 0, 1, a.forme(), false, meteo);
		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-face.toYRot() + 180));   // nord = 0
		ms.translate(-0.5, 0, -0.5);
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		int orn = Apparence.ORNEMENTS[a.ornement()];
		// les lanternes éclairent la bannière la nuit
		int lumB = a.avecLanternes() && (grand || murale) ? LightTexture.pack(Math.max(LightTexture.block(lum), 14), LightTexture.sky(lum)) : lum;
		if (murale) {
			murale(ms, buffers, geo, a, t, lum, lumB, orn);
		} else if (!grand) {
			toile(ms, buffers, geo, a, t, lum);
		} else {
			ms.translate(0, (be.hauteur() - GrandEtendardBlock.MAT) * 16, 0);   // la géométrie est écrite pour un mât de six blocs
			fleuron(ms, buffers, a.fleuron(), t, lum);
			// mise en berne : la bannière et ses ferrures descendent le long du mât
			float bas = a.style() == 2 ? 104 - geo.w() - 10 : (a.style() == 1 ? 101.5f : 102.5f) - geo.l();
			float descente = Math.max(0, bas + (be.hauteur() - GrandEtendardBlock.MAT) * 16 - 22) * hisse;
			int cotes = a.estDouble() && a.style() != 1 ? 2 : 1;
			for (int c = 0; c < cotes; c++) {
				ms.pushPose();
				ms.translate(0, -descente, 0);
				if (c == 1) { ms.translate(16, 0, 0); ms.scale(-1, 1, 1); }   // seconde bannière, en miroir de l'autre côté du mât
				ferrures(ms, buffers, geo, lumB);
				toile(ms, buffers, geo, a, t, lumB);
				if (a.avecFranges()) franges(ms, buffers, geo, orn, t, lumB);
				ms.popPose();
			}
			if (a.avecLanternes() && a.style() == 2) {          // cérémonie : deux lanternes sur des potences avant et arrière
				VertexConsumer fer = buffers.getBuffer(RenderType.entityCutoutNoCull(FER));
				boite(ms, fer, 7.25f, 100f, -3f, 8.75f, 101.5f, 6.5f, lum);
				boite(ms, fer, 7.25f, 100f, 9.5f, 8.75f, 101.5f, 19f, lum);
				lanterne(ms, buffers, 8, 100, -2);
				lanterne(ms, buffers, 8, 100, 18);
			}
		}
		ms.popPose();
	}

	/** Bannière murale : tringle, supports, embouts (fleurons couchés), lanternes, toile et franges. Mur côté sud (z = 16). */
	private void murale(PoseStack ms, MultiBufferSource buffers, Geo geo, Apparence a, float t, int lum, int lumB, int orn) {
		float W = geo.w(), e = a.avecLanternes() ? 6.5f : 1.5f;
		VertexConsumer fer = buffers.getBuffer(RenderType.entityCutoutNoCull(FER));
		boite(ms, fer, 8 - W / 2 - e, 12.25f, 11.75f, 8 + W / 2 + e, 13.75f, 13.25f, lum);            // tringle
		VertexConsumer laiton = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
		for (float x : new float[] {8 - W / 2 + 1, 8 + W / 2 - 1}) {                                  // supports scellés au mur
			boite(ms, laiton, x - 0.75f, 12, 13.25f, x + 0.75f, 14, 16, lum);
			boite(ms, laiton, x - 1.5f, 11, 15.4f, x + 1.5f, 15, 16, lum);
		}
		for (int c = 0; c < 2; c++) {                                                                // embouts
			ms.pushPose();
			ms.translate(c == 0 ? 8 + W / 2 + e : 8 - W / 2 - e, 13, 12.5f);
			ms.mulPose(Axis.ZP.rotationDegrees(c == 0 ? -90 : 90));
			ms.scale(0.4f, 0.4f, 0.4f);
			ms.translate(-8, -108, -8);
			fleuron(ms, buffers, a.fleuron(), t, lum);
			ms.popPose();
		}
		if (a.avecLanternes()) {
			lanterne(ms, buffers, 8 - W / 2 - 3.5f, 12.25f, 12.5f);
			lanterne(ms, buffers, 8 + W / 2 + 3.5f, 12.25f, 12.5f);
		}
		toile(ms, buffers, geo, a, t, lumB);
		if (a.avecFranges()) franges(ms, buffers, geo, orn, t, lumB);
	}

	/** La toile composée (une seule texture, visible des deux côtés). */
	private void toile(PoseStack ms, MultiBufferSource buffers, Geo geo, Apparence a, float t, int lum) {
		tissu(ms, buffers.getBuffer(RenderType.entityCutoutNoCull(TexturesBanniere.de(a))), geo, 0, t, lum, 255, 255, 255);
		if (a.brille()) {   // broderie lumineuse : motif et ornements repeints en pleine lumière, juste devant et derrière la toile
			VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(TexturesBanniere.lueur(a)));
			tissu(ms, vc, geo, EPS, t, PLEIN_FEU, 255, 255, 255);
			tissu(ms, vc, geo, -EPS, t, PLEIN_FEU, 255, 255, 255);
		}
	}

	private void tissu(PoseStack ms, VertexConsumer vc, Geo geo, float decal, float t, int lum, int r, int g, int b) {
		int style = geo.style();
		int nu = geo.grand() || geo.murale() ? 12 : style == 2 ? 16 : 8, nv = geo.grand() || geo.murale() ? 24 : style == 2 ? 8 : 16;
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
		if (geo.murale()) {   // contre le mur : ondule à peine, sans jamais traverser le mur
			float x = 8 - geo.w() / 2 + u * geo.w(), y = 12.75f - v * geo.l();
			float o = 0.7f * geo.vent() * (float) Math.pow(v, 1.2) * Mth.sin(t * 0.06f * (0.7f + 0.3f * geo.vent()) + v * 3f + u * 2f);
			return new float[] {x, y, 12.5f - Math.abs(o) + decal};
		}
		float m = geo.meteo();
		switch (geo.style()) {
			case 0 -> {   // potence : suspendue sous le bras, sur le côté
				float x = 16 + u * 11, y = 44.5f - v * 22, z = 8;
				float o = m * 1.3f * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.10f + v * 4f + u * 2f);
				return new float[] {x, y, z + o + decal};
			}
			case 1 -> {   // vexillum : devant le piédestal, sous la traverse
				float x = 1 + u * 14, y = 44.5f - v * 28, z = -1.2f;
				float o = m * 1.1f * (float) Math.pow(v, 1.3) * Mth.sin(t * 0.09f + v * 3.5f + u * 1.5f);
				return new float[] {x, y, z - Math.abs(o) * 0.6f + o * 0.4f + decal};
			}
			default -> {  // cérémonie : le long du mât, flotte à l'horizontale ; u = hauteur, v = longueur
				float s = v, x = 9.5f + s * 16, y = 46.5f - u * 12 - 0.8f * s * s, z = 8;
				float o = m * 1.6f * (float) Math.pow(s, 1.1) * Mth.sin(t * 0.16f - s * 5f + u * 1f);
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
				float e = geo.lanternes() ? 6 : 3;                                            // bras rallongé pour la lanterne
				boite(ms, fer, 9.5f, 102.5f, 7.25f, 9.5f + e + W, 104f, 8.75f, lum);
				boite(ms, fer, 9.5f, 99f, 7.5f, 11f, 102.5f, 8.5f, lum);                       // jambe de force
				VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
				boite(ms, or, 8.5f + e + W, 102f, 7f, 10.5f + e + W, 104.5f, 9f, lum);         // embout
				boite(ms, or, 5.5f, 101.5f, 5.5f, 10.5f, 103f, 10.5f, lum);                   // collier
				if (geo.lanternes()) lanterne(ms, buffers, 15.5f + W, 102.5f, 8);
			}
			case 1 -> {
				float e = geo.lanternes() ? 5 : 1;
				boite(ms, fer, 7.25f, 101f, -2.5f, 8.75f, 102.5f, 6f, lum);                    // potence avant
				boite(ms, fer, 8 - W / 2 - e, 101.5f, -2.75f, 8 + W / 2 + e, 103f, -1.25f, lum); // traverse
				VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
				boite(ms, or, 8 - W / 2 - e - 1.5f, 101f, -3.25f, 8 - W / 2 - e, 103.5f, -0.75f, lum);
				boite(ms, or, 8 + W / 2 + e, 101f, -3.25f, 8 + W / 2 + e + 1.5f, 103.5f, -0.75f, lum);
				boite(ms, or, 5.5f, 100.5f, 5.5f, 10.5f, 102f, 10.5f, lum);
				if (geo.lanternes()) {
					lanterne(ms, buffers, 8 - W / 2 - 4, 101.5f, -2);
					lanterne(ms, buffers, 8 + W / 2 + 4, 101.5f, -2);
				}
			}
			default -> {
				VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(LAITON));
				boite(ms, or, 5.5f, 103.5f, 5.5f, 10.5f, 105f, 10.5f, lum);                   // anneaux qui tiennent la hampe
				boite(ms, or, 5.5f, 103.5f - W, 5.5f, 10.5f, 105f - W, 10.5f, lum);
			}
		}
	}

	/** Lanterne suspendue (vraie lanterne du jeu), son sommet accroché en (x, y, z) ; toujours allumée. */
	private static void lanterne(PoseStack ms, MultiBufferSource buffers, float x, float y, float z) {
		ms.pushPose();
		ms.translate(x - 8, y - 16, z - 8);
		ms.scale(16, 16, 16);
		Minecraft.getInstance().getBlockRenderer().renderSingleBlock(
			Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, true), ms, buffers, PLEIN_FEU, OverlayTexture.NO_OVERLAY);
		ms.popPose();
	}

	/** Fleuron doré au sommet du mât (108 px) : pointe, globe, rouage qui tourne, couronne. */
	private static void fleuron(PoseStack ms, MultiBufferSource buffers, int type, float t, int lum) {
		VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(OR));
		switch (type) {
			case 0 -> {
				boite(ms, or, 6.25f, 108, 6.25f, 9.75f, 111.5f, 9.75f, lum);
				boite(ms, or, 5.75f, 108.75f, 5.75f, 10.25f, 110.75f, 10.25f, lum);
				boite(ms, or, 7.25f, 111.5f, 7.25f, 8.75f, 115, 8.75f, lum);
				boite(ms, or, 7.6f, 115, 7.6f, 8.4f, 117, 8.4f, lum);
			}
			case 1 -> {
				boite(ms, or, 7.25f, 108, 7.25f, 8.75f, 109.5f, 8.75f, lum);
				boite(ms, or, 5.5f, 110.5f, 6.5f, 10.5f, 113.5f, 9.5f, lum);
				boite(ms, or, 6.5f, 110.5f, 5.5f, 9.5f, 113.5f, 10.5f, lum);
				boite(ms, or, 6.5f, 109.5f, 6.5f, 9.5f, 114.5f, 9.5f, lum);
				boite(ms, or, 7.5f, 114.5f, 7.5f, 8.5f, 115.5f, 8.5f, lum);
			}
			case 2 -> {
				boite(ms, or, 7.25f, 108, 7.25f, 8.75f, 110.5f, 8.75f, lum);
				ms.pushPose();
				ms.translate(8, 114.5f, 8);
				ms.mulPose(Axis.ZP.rotationDegrees(t * 1.5f));
				boite(ms, or, -1.25f, -1.25f, -0.9f, 1.25f, 1.25f, 0.9f, lum);                   // moyeu
				for (int k = 0; k < 8; k++) {
					ms.pushPose();
					ms.mulPose(Axis.ZP.rotationDegrees(k * 45));
					boite(ms, or, -1.3f, 2.4f, -0.6f, 1.3f, 3.4f, 0.6f, lum);                    // jante
					boite(ms, or, -0.8f, 3.4f, -0.6f, 0.8f, 4.6f, 0.6f, lum);                    // dent
					if (k % 2 == 0) boite(ms, or, -0.4f, 1.25f, -0.4f, 0.4f, 2.4f, 0.4f, lum);   // rayon
					ms.popPose();
				}
				ms.popPose();
			}
			default -> {
				boite(ms, or, 7, 108, 7, 9, 109, 9, lum);
				boite(ms, or, 5.5f, 109, 5.5f, 10.5f, 111, 10.5f, lum);
				for (float[] c : new float[][] {{5.5f, 5.5f}, {9.5f, 5.5f}, {5.5f, 9.5f}, {9.5f, 9.5f}})
					boite(ms, or, c[0], 111, c[1], c[0] + 1, 113, c[1] + 1, lum);
				for (float[] c : new float[][] {{7.5f, 5.5f}, {7.5f, 9.5f}, {5.5f, 7.5f}, {9.5f, 7.5f}})
					boite(ms, or, c[0], 111, c[1], c[0] + 1, 112.5f, c[1] + 1, lum);
				boite(ms, or, 7.25f, 111, 7.25f, 8.75f, 113.5f, 8.75f, lum);
				boite(ms, or, 7.6f, 113.5f, 7.6f, 8.4f, 115.5f, 8.4f, lum);
				boite(ms, or, 7, 114.2f, 7.6f, 9, 114.8f, 8.4f, lum);
			}
		}
	}

	/** Bas de la bannière (en v) pour la colonne u, selon la forme : suit la découpe des textures. */
	private static float basForme(int forme, float u) {
		float x = u * 16 - 0.5f, d = Math.abs(x - 7.5f) * 0.85f;
		float rang = switch (forme) { case 0 -> 25 + d; case 2 -> 31.4f - d; default -> 31; };
		return Math.min(1f, (rang + 1) / 32f);
	}

	/** Franges teintes aux ornements, sous le bord inférieur de la bannière. */
	private static void franges(PoseStack ms, MultiBufferSource buffers, Geo geo, int couleur, float t, int lum) {
		VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(FRANGE));
		int r = couleur >> 16 & 255, g = couleur >> 8 & 255, b = couleur & 255;
		PoseStack.Pose pose = ms.last();
		float h = 4f;
		int n = 24;
		for (int i = 0; i < n; i++) {
			float a0 = i / (float) n, a1 = (i + 1) / (float) n;
			float[] h0, h1;
			float tu0, tu1;
			if (geo.style() == 2 && geo.grand()) {   // cérémonie : le long du bord bas, jusqu'à la découpe du bout
				float fin = basForme(geo.forme(), 1f);
				h0 = point(geo, 1f, a0 * fin, t, 0); h1 = point(geo, 1f, a1 * fin, t, 0);
				tu0 = a0 * fin * geo.l() / 16f; tu1 = a1 * fin * geo.l() / 16f;
			} else {
				h0 = point(geo, a0, basForme(geo.forme(), a0), t, 0); h1 = point(geo, a1, basForme(geo.forme(), a1), t, 0);
				tu0 = a0 * geo.w() / 16f; tu1 = a1 * geo.w() / 16f;
			}
			float[] b0 = {h0[0], h0[1] - h, h0[2]}, b1 = {h1[0], h1[1] - h, h1[2]};
			for (float[][] q : new float[][][] {{h0, b0, b1, h1}}) {
				float[][] uv = {{tu0, 0}, {tu0, 1}, {tu1, 1}, {tu1, 0}};
				for (int k = 0; k < 4; k++)
					vc.addVertex(pose, q[k][0], q[k][1], q[k][2]).setColor(r, g, b, 255).setUv(uv[k][0], uv[k][1])
						.setOverlay(OverlayTexture.NO_OVERLAY).setLight(lum).setNormal(pose, 0, 0, 1);
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
		if (be.murale())
			return new AABB(be.getBlockPos()).inflate(2.5, 0, 2.5).expandTowards(0, -5, 0);
		if (be.getBlockState().getBlock() instanceof GrandEtendardBlock)
			return new AABB(be.getBlockPos()).inflate(3.5, 0, 3.5).expandTowards(0, be.hauteur() + 2, 0);
		return new AABB(be.getBlockPos()).inflate(1.5, 0, 1.5).expandTowards(0, 3, 0);
	}
}
