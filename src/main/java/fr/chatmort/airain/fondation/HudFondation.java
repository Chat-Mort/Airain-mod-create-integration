package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * Titre de fondation : le nom en grand, la devise dessous, encadrés par la bannière de l'étendard de chaque côté.
 * Placé sous la zone des barres de boss ; apparition et disparition en fondu.
 */
public final class HudFondation {
	private static final long ENTREE = 500, TENUE = 3500, SORTIE = 1000;
	private static final float TAILLE_NOM = 2.4f, TAILLE_DEVISE = 1.0f, TAILLE_BANNIERE = 1.6f;
	private static TitreFondation titre;
	private static long debut;

	private HudFondation() {}

	public static void recevoir(TitreFondation m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> { titre = m; debut = System.currentTimeMillis(); });
	}

	public static void rendre(GuiGraphics g, DeltaTracker dt) {
		if (titre == null) return;
		Minecraft mc = Minecraft.getInstance();
		long t = System.currentTimeMillis() - debut;
		if (t > ENTREE + TENUE + SORTIE) { titre = null; return; }
		if (mc.options.hideGui) return;
		float a = t < ENTREE ? t / (float) ENTREE : t < ENTREE + TENUE ? 1f : 1f - (t - ENTREE - TENUE) / (float) SORTIE;
		int alpha = Math.max(5, (int) (a * 255));
		Font f = mc.font;
		String nom = titre.nom().isEmpty() ? Component.translatable("airain.fondation.sans_nom").getString() : titre.nom();
		Component devise = titre.devise().isEmpty() ? Component.translatable("airain.fondation.sous_titre") : Component.literal(titre.devise());
		int cx = g.guiWidth() / 2, y = 44;                        // sous les barres de boss
		int largNom = (int) (f.width(nom) * TAILLE_NOM), largDev = (int) (f.width(devise) * TAILLE_DEVISE);
		int demi = Math.max(largNom, largDev) / 2;

		// nom : or vif avec ombre
		g.pose().pushPose();
		g.pose().translate(cx, y, 0);
		g.pose().scale(TAILLE_NOM, TAILLE_NOM, 1f);
		g.drawCenteredString(f, nom, 0, 0, (alpha << 24) | 0xFFD45A);
		g.pose().popPose();

		// filet décoratif : deux traits dorés et un losange au centre
		int yl = y + (int) (9 * TAILLE_NOM) + 3;
		int coul = (alpha << 24) | 0xC8962E, clair = (alpha << 24) | 0xF5D27A;
		g.fill(cx - demi, yl, cx - 4, yl + 1, coul);
		g.fill(cx + 4, yl, cx + demi, yl + 1, coul);
		g.fill(cx - 2, yl - 1, cx + 2, yl + 2, clair);
		g.fill(cx - 1, yl - 2, cx + 1, yl + 3, clair);

		// devise : parchemin clair, en italique discret
		g.pose().pushPose();
		g.pose().translate(cx, yl + 6, 0);
		g.pose().scale(TAILLE_DEVISE, TAILLE_DEVISE, 1f);
		g.drawCenteredString(f, devise, 0, 0, (alpha << 24) | 0xEDE3C8);
		g.pose().popPose();

		// bannières de l'étendard, de chaque côté
		Apparence app = Apparence.unpack(titre.apparence());
		int bw = (int) (16 * TAILLE_BANNIERE), bh = (int) (32 * TAILLE_BANNIERE);
		int by = y - 6, ecart = demi + 14;
		RenderSystem.enableBlend();
		banniere(g, app, cx - ecart - bw, by, bw, bh, a);
		banniere(g, app, cx + ecart, by, bw, bh, a);
		RenderSystem.setShaderColor(1, 1, 1, 1);
	}

	private static void banniere(GuiGraphics g, Apparence app, int x, int y, int w, int h, float a) {
		// hampe dorée au-dessus de la bannière
		g.fill(x - 2, y - 2, x + w + 2, y, ((int) (a * 255) << 24) | 0xC8962E);
		calque(g, app.texFond(), Apparence.FONDS[app.fond()], x, y, w, h, a);
		if (app.texMotif() != null) calque(g, app.texMotif(), Apparence.ORNEMENTS[app.ornement()], x, y, w, h, a);
		calque(g, app.texOrnement(), Apparence.ORNEMENTS[app.ornement()], x, y, w, h, a);
	}

	private static void calque(GuiGraphics g, ResourceLocation tex, int c, int x, int y, int w, int h, float a) {
		RenderSystem.setShaderColor((c >> 16 & 255) / 255f, (c >> 8 & 255) / 255f, (c & 255) / 255f, a);
		g.blit(tex, x, y, w, h, 0f, 0f, 16, 32, 16, 32);
	}
}
