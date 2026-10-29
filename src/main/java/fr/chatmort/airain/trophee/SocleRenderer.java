package fr.chatmort.airain.trophee;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import fr.chatmort.airain.fondation.Apparence;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

/**
 * Piédestal de l'Empire, entièrement dessiné ici : socle (matériau, garnitures teintées, velours simple ou capitonné),
 * colonne haute, plaque gravée, présentation du trophée (lévitation, posé, chevalet, cloche de verre), halo lumineux.
 * Coordonnées en pixels, devant = nord. Utilisé aussi pour l'aperçu de l'écran de réglages.
 */
public class SocleRenderer implements BlockEntityRenderer<SocleBlockEntity> {
	/** Éléments du modèle d'origine : de (x, y, z), à (x, y, z), matière (0 socle, 1 colonne, 2 garniture, 3 velours). */
	private static final float[][] ELEMENTS = {
		{0.0f, 0.0f, 0.0f, 16.0f, 2.0f, 16.0f, 0},
		{0.5f, 2.0f, 0.5f, 15.5f, 2.6f, 15.5f, 2},
		{1.5f, 2.6f, 1.5f, 14.5f, 4.0f, 14.5f, 0},
		{2.5f, 4.0f, 2.5f, 13.5f, 4.6f, 13.5f, 2},
		{3.5f, 4.6f, 3.5f, 12.5f, 10.0f, 12.5f, 1},
		{3.0f, 4.6f, 3.0f, 4.2f, 10.0f, 4.2f, 2},
		{3.0f, 4.6f, 11.8f, 4.2f, 10.0f, 13.0f, 2},
		{11.8f, 4.6f, 3.0f, 13.0f, 10.0f, 4.2f, 2},
		{11.8f, 4.6f, 11.8f, 13.0f, 10.0f, 13.0f, 2},
		{2.5f, 10.0f, 2.5f, 13.5f, 10.6f, 13.5f, 2},
		{1.0f, 10.6f, 1.0f, 15.0f, 12.0f, 15.0f, 0},
		{0.6f, 11.4f, 0.6f, 15.4f, 12.0f, 15.4f, 2},
		{2.0f, 12.0f, 2.0f, 14.0f, 13.0f, 14.0f, 3},
		{1.2f, 9.4f, 1.2f, 2.0f, 10.6f, 2.0f, 2},
		{1.2f, 9.4f, 14.0f, 2.0f, 10.6f, 14.8f, 2},
		{14.0f, 9.4f, 1.2f, 14.8f, 10.6f, 2.0f, 2},
		{14.0f, 9.4f, 14.0f, 14.8f, 10.6f, 14.8f, 2},
		{1.0f, 12.0f, 1.0f, 2.0f, 13.5f, 2.0f, 2},
		{1.0f, 12.0f, 14.0f, 2.0f, 13.5f, 15.0f, 2},
		{14.0f, 12.0f, 1.0f, 15.0f, 13.5f, 2.0f, 2},
		{14.0f, 12.0f, 14.0f, 15.0f, 13.5f, 15.0f, 2}

	};
	private static final String[][] MATERIAUX = {
		{"airain:textures/block/socle_marbre.png", "airain:textures/block/socle_colonne.png"},
		{"minecraft:textures/block/polished_tuff.png", "minecraft:textures/block/tuff_bricks.png"},
		{"minecraft:textures/block/polished_blackstone.png", "minecraft:textures/block/polished_blackstone_bricks.png"},
		{"minecraft:textures/block/weathered_cut_copper.png", "minecraft:textures/block/weathered_copper.png"},
		{"minecraft:textures/block/dark_oak_planks.png", "minecraft:textures/block/stripped_dark_oak_log.png"}};
	private static final ResourceLocation GARNITURE = rl("airain:textures/block/socle_garniture.png");
	private static final ResourceLocation NOIR = rl("minecraft:textures/block/black_concrete.png");
	private static final ResourceLocation HALO = rl("airain:textures/block/socle_halo.png");
	private static final ResourceLocation VERRE = rl("airain:textures/block/socle_verre.png");

	public SocleRenderer(BlockEntityRendererProvider.Context ctx) {}

	private static ResourceLocation rl(String s) {
		return ResourceLocation.parse(s);
	}

	@Override
	public void render(SocleBlockEntity be, float pt, PoseStack ms, MultiBufferSource buffers, int light, int overlay) {
		if (be.getLevel() == null) return;
		Direction face = be.getBlockState().hasProperty(SocleBlock.FACING) ? be.getBlockState().getValue(SocleBlock.FACING) : Direction.NORTH;
		dessiner(ms, buffers, be.apparence(), be.trophee(), be.plaque(), be.jour(), be.getLevel().getGameTime() + pt, light, face, be.getLevel());
	}

	/** Dessine tout le piédestal ; l'origine est le coin du bloc du bas. */
	public static void dessiner(PoseStack ms, MultiBufferSource buffers, SocleApparence a, ItemStack trophee, String plaque, int jour,
			float t, int light, Direction face, Level level) {
		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-face.toYRot() + 180));   // nord = 0
		ms.translate(-0.5, 0, -0.5);
		ms.pushPose();
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		int garn = Apparence.ORNEMENTS[a.garniture()], vel = Apparence.FONDS[a.velours()];
		VertexConsumer socle = buffers.getBuffer(RenderType.entityCutoutNoCull(rl(MATERIAUX[a.materiau()][0])));
		VertexConsumer colonne = buffers.getBuffer(RenderType.entityCutoutNoCull(rl(MATERIAUX[a.materiau()][1])));
		VertexConsumer or = buffers.getBuffer(RenderType.entityCutoutNoCull(GARNITURE));
		VertexConsumer velours = buffers.getBuffer(RenderType.entityCutoutNoCull(
			rl("airain:textures/block/socle_velours_" + (a.losange() ? "losange" : "simple") + ".png")));
		boolean haute = a.haute();
		for (float[] e : ELEMENTS) {
			float y0 = e[1], y1 = e[4];
			if (haute) {                                       // colonne haute : la colonne s'allonge, le haut monte de 16 px
				if (y0 >= 4.6f && y1 <= 10f) y1 += 16;
				else if (y0 >= 9.4f) { y0 += 16; y1 += 16; }
			}
			int m = (int) e[6];
			VertexConsumer vc = m == 0 ? socle : m == 1 ? colonne : m == 2 ? or : velours;
			int c = m == 2 ? garn : m == 3 ? vel : 0xFFFFFF;
			boite(ms, vc, e[0], y0, e[2], e[3], y1, e[5], c, light);
		}
		float haut = haute ? 29 : 13;                          // dessus du velours
		// garnitures sur le velours (passepoil, boutons du capitonnage)
		VertexConsumer garni = buffers.getBuffer(RenderType.entityCutoutNoCull(
			rl("airain:textures/block/socle_garni_" + (a.losange() ? "losange" : "simple") + ".png")));
		quadHaut(ms, garni, 2, haut + 0.02f, 2, 14, 14, garn, light);
		// plaque gravée sur la colonne
		if (a.avecPlaque()) {
			float py = haute ? 13.5f : 5.5f;
			boite(ms, or, 4.4f, py, 3.3f, 11.6f, py + 3.6f, 3.5f, garn, light);
			boite(ms, buffers.getBuffer(RenderType.entityCutoutNoCull(NOIR)), 4.8f, py + 0.4f, 3.2f, 11.2f, py + 3.2f, 3.3f, 0x2A2420, light);
		}
		// chevalet
		if (a.presentation() == 2 && !trophee.isEmpty()) {
			boite(ms, or, 4.5f, haut, 9.2f, 5.5f, haut + 9, 10.2f, garn, light);
			boite(ms, or, 10.5f, haut, 9.2f, 11.5f, haut + 9, 10.2f, garn, light);
			boite(ms, or, 4.5f, haut + 1.8f, 7.6f, 11.5f, haut + 2.6f, 10.2f, garn, light);   // tablette
		}
		// halo lumineux sous le trophée
		if (a.eclaire()) {
			VertexConsumer h = buffers.getBuffer(RenderType.entityTranslucentEmissive(HALO));
			quadHaut(ms, h, 2.5f, haut + 0.06f, 2.5f, 13.5f, 13.5f, 0xFFFFFF, LightTexture.FULL_BRIGHT);
		}
		// cloche de verre : anneau, dôme en gradins, bouton
		if (a.presentation() == 3) {
			boite(ms, or, 2.3f, haut, 2.3f, 13.7f, haut + 0.7f, 13.7f, garn, light);
			boite(ms, or, 7.2f, haut + 13.5f, 7.2f, 8.8f, haut + 15f, 8.8f, garn, light);
			VertexConsumer v = buffers.getBuffer(RenderType.entityTranslucent(VERRE));
			float[][] gradins = {{5.4f, 0.7f, 9f}, {4.7f, 9f, 11f}, {3.5f, 11f, 12.5f}, {2f, 12.5f, 13.5f}};
			for (int k = 0; k < gradins.length; k++) {
				float r = gradins[k][0];
				cotes(ms, v, 8 - r, haut + gradins[k][1], 8 - r, 8 + r, haut + gradins[k][2], 8 + r, light);
				float rs = k + 1 < gradins.length ? gradins[k + 1][0] : 0;   // couronne de verre entre deux gradins
				anneau(ms, v, r, rs, haut + gradins[k][2], light);
			}
		}
		ms.popPose();
		// plaque : le texte
		if (a.avecPlaque() && !plaque.isEmpty()) texte(ms, buffers, plaque, jour, haute, light);
		// le trophée
		if (!trophee.isEmpty()) trophee(ms, buffers, a, trophee, t, haut / 16f, light, level);
		ms.popPose();
	}

	private static void trophee(PoseStack ms, MultiBufferSource buffers, SocleApparence a, ItemStack p, float t, float haut, int light, Level level) {
		int lum = a.eclaire() ? LightTexture.FULL_BRIGHT : light;
		ms.pushPose();
		switch (a.presentation()) {
			case 1 -> {   // posé, de face
				ms.translate(0.5, haut + 0.31, 0.5);
				ms.scale(0.6f, 0.6f, 0.6f);
			}
			case 2 -> {   // sur le chevalet, incliné vers l'arrière
				ms.translate(0.5, haut + 0.42, 0.55);
				ms.mulPose(Axis.XP.rotationDegrees(-14));
				ms.scale(0.62f, 0.62f, 0.62f);
			}
			case 3 -> {   // sous cloche : plus petit, tourne lentement
				ms.translate(0.5, haut + 0.36 + Mth.sin(t / 25f) * 0.02, 0.5);
				ms.mulPose(Axis.YP.rotationDegrees(t * 0.8f));
				ms.scale(0.5f, 0.5f, 0.5f);
			}
			default -> {  // lévitation
				ms.translate(0.5, haut + 0.41 + Mth.sin(t / 20f) * 0.04, 0.5);
				ms.mulPose(Axis.YP.rotationDegrees(t * 1.5f));
				ms.scale(0.75f, 0.75f, 0.75f);
			}
		}
		if (a.presentation() == 1 || a.presentation() == 2) ms.mulPose(Axis.YP.rotationDegrees(180));   // face vers l'avant
		Minecraft.getInstance().getItemRenderer().renderStatic(p, ItemDisplayContext.FIXED, lum, OverlayTexture.NO_OVERLAY, ms, buffers, level, 0);
		ms.popPose();
	}

	/** Texte de la plaque : le nom gravé et le jour de la victoire, réduits pour tenir dans la plaque. */
	private static void texte(PoseStack ms, MultiBufferSource buffers, String plaque, int jour, boolean haute, int light) {
		Font f = Minecraft.getInstance().font;
		Component l2 = Component.translatable("airain.socle.jour", jour);
		float py = (haute ? 13.5f : 5.5f) / 16f, largeur = 6f / 16f;
		ms.pushPose();
		ms.translate(0.5, py + 1.8f / 16f, 3.18f / 16f);
		ms.mulPose(Axis.YP.rotationDegrees(180));
		float s = Math.min(0.0062f, largeur / Math.max(1, Math.max(f.width(plaque), f.width(l2))));
		ms.scale(s, -s, s);
		int or = 0xF0D080;
		f.drawInBatch(plaque, -f.width(plaque) / 2f, -9.5f, or, false, ms.last().pose(), buffers, Font.DisplayMode.POLYGON_OFFSET, 0, light);
		f.drawInBatch(l2, -f.width(l2) / 2f, 0.5f, 0xB8A070, false, ms.last().pose(), buffers, Font.DisplayMode.POLYGON_OFFSET, 0, light);
		ms.popPose();
	}

	// ------------------------------------------------------------------ primitives
	private static void boite(PoseStack ms, VertexConsumer vc, float x0, float y0, float z0, float x1, float y1, float z1, int c, int lum) {
		if (y0 < 16 && y1 > 16) {                             // coupé à la limite du bloc : l'UV reste dans la texture
			boite(ms, vc, x0, y0, z0, x1, 16, z1, c, lum);
			boite(ms, vc, x0, 16, z0, x1, y1, z1, c, lum);
			return;
		}
		PoseStack.Pose p = ms.last();
		float vy0 = 16 - (y1 > 16 ? y1 - 16 : y1), vy1 = 16 - (y1 > 16 ? y0 - 16 : y0);
		face(vc, p, c, lum, 0, 0, -1, x0, vy0, x1, vy1, x1, y1, z0, x0, y1, z0, x0, y0, z0, x1, y0, z0);
		face(vc, p, c, lum, 0, 0, 1, x0, vy0, x1, vy1, x0, y1, z1, x1, y1, z1, x1, y0, z1, x0, y0, z1);
		face(vc, p, c, lum, -1, 0, 0, z0, vy0, z1, vy1, x0, y1, z0, x0, y1, z1, x0, y0, z1, x0, y0, z0);
		face(vc, p, c, lum, 1, 0, 0, z0, vy0, z1, vy1, x1, y1, z1, x1, y1, z0, x1, y0, z0, x1, y0, z1);
		face(vc, p, c, lum, 0, 1, 0, x0, z0, x1, z1, x0, y1, z0, x1, y1, z0, x1, y1, z1, x0, y1, z1);
		face(vc, p, c, lum, 0, -1, 0, x0, z0, x1, z1, x0, y0, z1, x1, y0, z1, x1, y0, z0, x0, y0, z0);
	}

	/** Seulement les quatre côtés (verre de la cloche). */
	private static void cotes(PoseStack ms, VertexConsumer vc, float x0, float y0, float z0, float x1, float y1, float z1, int lum) {
		PoseStack.Pose p = ms.last();
		face(vc, p, 0xFFFFFF, lum, 0, 0, -1, 0, 0, 16, 16, x1, y1, z0, x0, y1, z0, x0, y0, z0, x1, y0, z0);
		face(vc, p, 0xFFFFFF, lum, 0, 0, 1, 0, 0, 16, 16, x0, y1, z1, x1, y1, z1, x1, y0, z1, x0, y0, z1);
		face(vc, p, 0xFFFFFF, lum, -1, 0, 0, 0, 0, 16, 16, x0, y1, z0, x0, y1, z1, x0, y0, z1, x0, y0, z0);
		face(vc, p, 0xFFFFFF, lum, 1, 0, 0, 0, 0, 16, 16, x1, y1, z1, x1, y1, z0, x1, y0, z0, x1, y0, z1);
	}

	/** Couronne horizontale entre deux carrés centrés (rayons r > rs), à la hauteur y. */
	private static void anneau(PoseStack ms, VertexConsumer vc, float r, float rs, float y, int lum) {
		PoseStack.Pose p = ms.last();
		float a = 8 - r, b = 8 + r, c = 8 - rs, d = 8 + rs;
		face(vc, p, 0xFFFFFF, lum, 0, 1, 0, 0, 0, 16, 4, a, y, a, b, y, a, b, y, c, a, y, c);
		face(vc, p, 0xFFFFFF, lum, 0, 1, 0, 0, 0, 16, 4, a, y, d, b, y, d, b, y, b, a, y, b);
		face(vc, p, 0xFFFFFF, lum, 0, 1, 0, 0, 0, 4, 16, a, y, c, c, y, c, c, y, d, a, y, d);
		face(vc, p, 0xFFFFFF, lum, 0, 1, 0, 0, 0, 4, 16, d, y, c, b, y, c, b, y, d, d, y, d);
	}

	private static void quadHaut(PoseStack ms, VertexConsumer vc, float x0, float y, float z0, float x1, float z1, int c, int lum) {
		face(vc, ms.last(), c, lum, 0, 1, 0, x0, z0, x1, z1, x0, y, z0, x1, y, z0, x1, y, z1, x0, y, z1);
	}

	/** Un quadrilatère : normale, rectangle d'UV (en pixels de texture 16), quatre sommets (haut-gauche, haut-droite, bas-droite, bas-gauche). */
	private static void face(VertexConsumer vc, PoseStack.Pose p, int c, int lum, float nx, float ny, float nz,
			float u0, float v0, float u1, float v1, float... q) {
		float[][] uv = {{u0, v0}, {u1, v0}, {u1, v1}, {u0, v1}};
		int r = c >> 16 & 255, g = c >> 8 & 255, b = c & 255;
		for (int k = 0; k < 4; k++)
			vc.addVertex(p, q[k * 3], q[k * 3 + 1], q[k * 3 + 2]).setColor(r, g, b, 255).setUv(uv[k][0] / 16f, uv[k][1] / 16f)
				.setOverlay(OverlayTexture.NO_OVERLAY).setLight(lum).setNormal(p, nx, ny, nz);
	}

	@Override
	public boolean shouldRenderOffScreen(SocleBlockEntity be) {
		return true;
	}

	public AABB getRenderBoundingBox(SocleBlockEntity be) {
		return new AABB(be.getBlockPos()).expandTowards(0, 3, 0);
	}
}
