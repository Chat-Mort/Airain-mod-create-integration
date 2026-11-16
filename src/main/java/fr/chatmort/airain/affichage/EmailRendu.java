package fr.chatmort.airain.affichage;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.phys.AABB;

import java.util.List;

/**
 * Rendu du tableau émaillé, par le bloc du coin : contre-plaque (au mur), cadre en saillie, émail en retrait, rosaces,
 * écusson, baguettes en relief, texte et barres. Repère : u vers la droite, v vers le bas depuis le haut du tableau,
 * z vers l'avant (pixels de modèle).
 */
public class EmailRendu implements BlockEntityRenderer<EmailBlockEntity> {
	private static final String[] STADES = {"", "exposed_", "weathered_", "oxidized_"};
	private final Font font;
	public EmailRendu(BlockEntityRendererProvider.Context c) { font = c.getFont(); }

	private static TextureAtlasSprite sprite(String nom) {
		return Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(ResourceLocation.fromNamespaceAndPath("airain", "block/" + nom));
	}
	public static int couleurEmail(Reglages r) { return DyeColor.byId(r.email).getTextureDiffuseColor() & 0xFFFFFF; }
	static int melange(int a, int b, float t) {
		int r = (int) (((a >> 16) & 255) * (1 - t) + ((b >> 16) & 255) * t), g = (int) (((a >> 8) & 255) * (1 - t) + ((b >> 8) & 255) * t), bl = (int) ((a & 255) * (1 - t) + (b & 255) * t);
		return (r << 16) | (g << 8) | bl;
	}

	@Override
	public void render(EmailBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int lumiere, int overlay) {
		if (!be.estControleur() || be.reglages() == null || be.getLevel() == null) return;
		Reglages r = be.reglages();
		Direction f = be.face();
		EmailBlock.Montage mo = be.getBlockState().getValue(EmailBlock.MONTAGE);
		int lum = LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().relative(f));
		long t = be.getLevel().getGameTime();
		boolean alerte = be.alerte && r.alerteLigne > 0;
		boolean phase = alerte && (r.alerteAction == 1 || (t / 10) % 2 == 0);
		boolean retro = (be.allume && r.eclairage == 1) || phase;
		boolean lettres = be.allume && r.eclairage >= 1 || phase;
		int email = couleurEmail(r);
		if (phase) email = melange(email, Reglages.PALETTE[r.alerteCouleur], 0.55f);

		ms.pushPose();
		ms.translate(0.5, 0.5, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-f.toYRot()));
		ms.translate(-0.5, 0.5, 0);            // u = 0 au bord gauche, v = 0 en haut du bloc du coin
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		Boite b = new Boite(ms, buf.getBuffer(RenderType.cutout()), lum);
		float W = be.largeur * 16, H = be.hauteur * 16;
		boolean mur = mo == EmailBlock.Montage.MUR;
		float v0 = mo == EmailBlock.Montage.PENDU ? 4 : 0;
		String p = STADES[r.airain];
		float ep = r.cadre == 3 ? 0.5f : be.hauteur == 1 ? 2 : 3;
		float zAr = mur ? -8 : -3, zAv = mur ? -2.5f : 3, zEm = mur ? -5 : 2.2f;
		TextureAtlasSprite tc = r.cadre == 2 ? sprite("polished_white_marble") : sprite(p + (r.cadre == 0 ? "airain_beam_plate" : "airain_block"));
		TextureAtlasSprite te = sprite(r.mat ? "enamel_matte" : "enamel");
		// émail (une plaque pleine, en retrait du cadre ; deux faces quand le tableau n'est pas au mur)
		b.lum = retro ? LightTexture.FULL_BRIGHT : lum;
		b.boite(te, ep, v0 + ep, mur ? -6 : -zEm, W - ep, H - ep, zEm, email);
		b.lum = lum;
		if (mur) b.boite(sprite(p + "cut_airain"), 0, 0, -8, W, H, -6, 0x8C8C8C);            // contre-plaque
		if (r.cadre != 3) {
			b.boite(tc, 0, v0, zAr, W, v0 + ep, zAv, 0xFFFFFF); b.boite(tc, 0, H - ep, zAr, W, H, zAv, 0xFFFFFF);
			b.boite(tc, 0, v0 + ep, zAr, ep, H - ep, zAv, 0xFFFFFF); b.boite(tc, W - ep, v0 + ep, zAr, W, H - ep, zAv, 0xFFFFFF);
		}
		TextureAtlasSprite ci = sprite(p + "chiseled_airain");
		if (r.rosaces && r.cadre != 3) {
			float a = 0.5f, c = 2;
			for (float[] q : new float[][] {{a, v0 + a}, {W - a - c, v0 + a}, {a, H - a - c}, {W - a - c, H - a - c}}) {
				b.boite(ci, q[0], q[1], zAv, q[0] + c, q[1] + c, zAv + 1, 0xFFFFFF);
				if (!mur) b.boite(ci, q[0], q[1], zAr - 1, q[0] + c, q[1] + c, zAr, 0xFFFFFF);
			}
		}
		if (r.ecusson && r.cadre != 3 && mo != EmailBlock.Montage.PENDU) {     // écusson ciselé au fronton
			float cx = W / 2;
			b.boite(ci, cx - 5, -6, mur ? -7 : -2.5f, cx + 5, 1, mur ? -3 : 2.5f, 0xFFFFFF);
			b.boite(sprite(p + "airain_beam_plate"), cx - 3, -8, mur ? -6.5f : -2, cx + 3, -6, mur ? -3.5f : 2, 0xFFFFFF);
		}
		if (mo == EmailBlock.Montage.PENDU) {                                     // deux tiges jusqu'au plafond
			TextureAtlasSprite ti = sprite(p + "airain_rod");
			for (float x : new float[] {Math.min(8, W / 4), W - Math.min(8, W / 4)}) b.boite(ti, x - 0.5f, -0.01f, -0.5f, x + 0.5f, v0, 0.5f, 0xFFFFFF);
		}
		// contenu, sur chaque face visible
		TextureAtlasSprite tb = sprite(p + "airain_lattice_bar");
		for (boolean derriere : mur ? new boolean[] {false} : new boolean[] {false, true}) {
			ms.pushPose();
			if (derriere) { ms.translate(W / 2, 0, 0); ms.mulPose(Axis.YP.rotationDegrees(180)); ms.translate(-W / 2, 0, 0); }
			float ox = ep, oy = v0 + ep, z = zEm;
			List<Reglages.Ligne> L = r.face(derriere);
			int base = derriere && !r.memeFace ? r.avant.size() : 0;
			Boite bb = new Boite(ms, buf.getBuffer(RenderType.cutout()), lettres ? LightTexture.FULL_BRIGHT : lum);
			Boite barres = new Boite(ms, buf.getBuffer(RenderType.cutout()), retro || lettres ? LightTexture.FULL_BRIGHT : lum);
			int lt = lettres ? LightTexture.FULL_BRIGHT : lum;
			MiseEnPage.dessiner(new MiseEnPage.Peintre() {
				@Override
				public void texte(Component c, float x, float y, float s, int col, boolean grave) {
					if (grave) {     // en creux : un liseré clair dessous, la lettre sombre
						int fond = couleurEmail(r);
						trace(c, x, y + 0.6f * s, s, melange(fond, 0xFFFFFF, 0.35f), z + 0.02f);
						trace(c, x, y, s, melange(fond, 0x000000, 0.6f), z + 0.03f);
					} else trace(c, x, y, s, col, z + 0.03f);
				}
				private void trace(Component c, float x, float y, float s, int col, float zz) {
					ms.pushPose();
					ms.translate(ox + x, -(oy + y), zz);
					ms.scale(s, -s, s);
					font.drawInBatch(c, 0, 0, 0xFF000000 | col, false, ms.last().pose(), buf, Font.DisplayMode.POLYGON_OFFSET, 0, lt);
					ms.popPose();
				}
				@Override public void rect(float x0, float y0, float x1, float y1, int col) { barres.face(te, ox + x0, oy + y0, ox + x1, oy + y1, z + 0.02f, col); }
				@Override public void baguette(float x0, float y0, float x1, float y1) { bb.lum = lum; bb.boite(tb, ox + x0, oy + y0, z, ox + x1, oy + y1, z + 1, 0xFFFFFF); }
			}, font, r, L, i -> be.valeur(base + i), W - 2 * ep, H - v0 - 2 * ep);
			ms.popPose();
		}
		ms.popPose();
	}

	@Override public boolean shouldRenderOffScreen(EmailBlockEntity be) { return true; }
	@Override public AABB getRenderBoundingBox(EmailBlockEntity be) { return be.getRenderBoundingBox(); }

	/** Boîtes texturées pixel pour pixel (uv à la position, par carreaux de 16 : jamais étirées). */
	static final class Boite {
		final PoseStack ms; final VertexConsumer vc; int lum;
		Boite(PoseStack ms, VertexConsumer vc, int lum) { this.ms = ms; this.vc = vc; this.lum = lum; }
		/** u0..u1 vers la droite, v0..v1 vers le bas, z0..z1 vers l'avant. */
		void boite(TextureAtlasSprite s, float u0, float v0, float z0, float u1, float v1, float z1, int col) {
			for (float a = u0; a < u1 - 1e-4f; ) {
				float a1 = Math.min(u1, (float) Math.floor(a / 16 + 1e-4f) * 16 + 16);
				for (float c = v0; c < v1 - 1e-4f; ) {
					float c1 = Math.min(v1, (float) Math.floor(c / 16 + 1e-4f) * 16 + 16);
					morceau(s, a, c, z0, a1, c1, z1, col, a == u0, a1 == u1, c == v0, c1 == v1);
					c = c1;
				}
				a = a1;
			}
		}
		private void morceau(TextureAtlasSprite s, float u0, float v0, float z0, float u1, float v1, float z1, int col, boolean g, boolean d, boolean h, boolean b) {
			float bu = (float) Math.floor(u0 / 16 + 1e-4f) * 16, bv = (float) Math.floor(v0 / 16 + 1e-4f) * 16;
			float U0 = u0 - bu, U1 = u1 - bu, V0 = v0 - bv, V1 = v1 - bv;
			float Z0 = Math.floorMod((int) Math.floor(z0), 16) + (z0 - (float) Math.floor(z0)), Z1 = Z0 + (z1 - z0);
			if (Z1 > 16) { Z0 -= Z1 - 16; Z1 = 16; }
			// y du modèle = -v
			quad(s, new float[][] {{u0, -v1, z1}, {u1, -v1, z1}, {u1, -v0, z1}, {u0, -v0, z1}}, U0, V1, U1, V0, 0, 0, 1, col, 1f);          // avant
			quad(s, new float[][] {{u1, -v1, z0}, {u0, -v1, z0}, {u0, -v0, z0}, {u1, -v0, z0}}, 16 - U1, V1, 16 - U0, V0, 0, 0, -1, col, 1f);  // arrière
			if (h) quad(s, new float[][] {{u0, -v0, z1}, {u1, -v0, z1}, {u1, -v0, z0}, {u0, -v0, z0}}, U0, Z1, U1, Z0, 0, 1, 0, col, 0.92f);   // dessus
			if (b) quad(s, new float[][] {{u0, -v1, z0}, {u1, -v1, z0}, {u1, -v1, z1}, {u0, -v1, z1}}, U0, Z0, U1, Z1, 0, -1, 0, col, 0.6f);   // dessous
			if (g) quad(s, new float[][] {{u0, -v1, z0}, {u0, -v1, z1}, {u0, -v0, z1}, {u0, -v0, z0}}, Z0, V1, Z1, V0, -1, 0, 0, col, 0.75f);  // gauche
			if (d) quad(s, new float[][] {{u1, -v1, z1}, {u1, -v1, z0}, {u1, -v0, z0}, {u1, -v0, z1}}, 16 - Z1, V1, 16 - Z0, V0, 1, 0, 0, col, 0.75f);  // droite
		}
		/** Une seule face avant (barres, filets). */
		void face(TextureAtlasSprite s, float u0, float v0, float u1, float v1, float z, int col) {
			quad(s, new float[][] {{u0, -v1, z}, {u1, -v1, z}, {u1, -v0, z}, {u0, -v0, z}}, 4, 12, 12, 4, 0, 0, 1, col, 1f);
		}
		private void quad(TextureAtlasSprite s, float[][] p, float ua, float va, float ub, float vb, float nx, float ny, float nz, int col, float ombre) {
			int r = (int) (((col >> 16) & 255) * ombre), g = (int) (((col >> 8) & 255) * ombre), bl = (int) ((col & 255) * ombre);
			PoseStack.Pose pz = ms.last();
			float[][] uv = {{ua, va}, {ub, va}, {ub, vb}, {ua, vb}};
			for (int i = 0; i < 4; i++)
				vc.addVertex(pz, p[i][0], p[i][1], p[i][2]).setColor(r, g, bl, 255).setUv(s.getU(uv[i][0] / 16f), s.getV(uv[i][1] / 16f)).setLight(lum).setNormal(pz, nx, ny, nz);
		}
	}
}
