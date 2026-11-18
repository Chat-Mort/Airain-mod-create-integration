package fr.chatmort.airain.gui;

import com.mojang.blaze3d.systems.RenderSystem;

import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

/**
 * Panneau de réglages commun de l'interface HD (socle des trophées, étendard, tableau émaillé) :
 * planche textures/gui/panel_hd.png, présente seulement dans le pack « Airain-Interface-HD ».
 * Coordonnées en « code » : le panneau est dessiné en (x - 10, y - 10), comme l'ancien.
 * Dans le panneau : bac des réglages de (x - 1, y + 24) à (x + 200, y + 176), vitrine de (x + 210, y + 4) à (x + 292, y + 176).
 */
public final class PanneauHD {
	public static final ResourceLocation ATLAS = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/panel_hd.png");
	/** Haut des onglets, haut du bac, première rangée de réglages, pas des rangées (par rapport à y). */
	public static final int Y_ONGLETS = 8, Y_BAC = 24, Y_LIGNES = 32, PAS = 21;
	/** Bouton « Terminé » / « Annuler » : 99 px de large, 101 px d'écart. */
	public static final int BOUTON = 99, ECART_BOUTONS = 101;

	private PanneauHD() {}

	private static void blit(GuiGraphics g, int x, int y, int u, int v, int w, int h) {
		g.blit(ATLAS, x, y, u, v, w, h, 512, 256);
	}

	/** Pièce de 100 px de large posée à la largeur voulue : deux bouts fixes, le milieu étiré. */
	private static void troisTranches(GuiGraphics g, int x, int y, int w, int h, int u, int v, int bord) {
		blit(g, x, y, u, v, bord, h);
		g.blit(ATLAS, x + bord, y, w - 2 * bord, h, u + bord, v, 100 - 2 * bord, h, 512, 256);
		blit(g, x + w - bord, y, u + 100 - bord, v, bord, h);
	}

	public static void fond(GuiGraphics g, int x, int y) { blit(g, x - 10, y - 10, 0, 0, 310, 226); }

	/** Train d'engrenages gravé au bas du bac (atlas 312,200, 101x30), posé seulement si le contenu de l'onglet
	 *  s'arrête au moins 5 px au-dessus : le tableau émaillé, qui remplit son bac, ne l'appelle pas. */
	public static void garniture(GuiGraphics g, int x, int y, int finContenu) {
		if (finContenu + 5 <= y + 142) blit(g, x + 49, y + 142, 312, 200, 101, 30);
	}

	/** Reflets de la vitre, posés après l'aperçu pour passer devant lui. */
	public static void reflets(GuiGraphics g, int x, int y) {
		g.pose().pushPose();
		g.pose().translate(0, 0, 400);      // devant l'aperçu en 3D
		// l'aperçu (franges, rendu 3D) peut laisser le mélange coupé : sans lui, les reflets à 10 % sortaient en blanc plein
		RenderSystem.enableBlend(); RenderSystem.defaultBlendFunc();
		blit(g, x + 210, y + 4, 420, 48, 82, 172);
		RenderSystem.disableBlend();
		g.pose().popPose();
	}

	/** Onglet de classeur : l'actif (cramoisi) s'ouvre dans le bac, les autres s'arrêtent sur son rebord. */
	public static void onglet(GuiGraphics g, Font font, int x, int y, int w, Component txt, boolean actif, boolean survol) {
		if (actif) troisTranches(g, x, y, w, 16, 320, 0, 8);
		else troisTranches(g, x, y + 1, w, 14, 320, 16, 8);
		int c = actif ? InterfaceHD.AIRAIN : survol ? 0xD8DCE2 : InterfaceHD.ARDOISE_TEXTE;
		g.drawString(font, txt, x + w / 2 - font.width(txt) / 2, y + 4, c, true);
	}

	/** Flèche ronde 16x16. */
	public static void fleche(GuiGraphics g, int x, int y, boolean droite, boolean survol) {
		blit(g, x, y, 320 + (droite ? 16 : 0) + (survol ? 32 : 0), 32, 16, 16);
	}

	/** Nom d'un réglage (y = haut de la rangée de 16) : engrenage en puce, texte airain, points de conduite jusqu'à xFin. */
	public static void libelle(GuiGraphics g, Font font, int x, int y, int xFin, Component txt) {
		blit(g, x - 1, y + 4, 384, 32, 9, 9);
		g.drawString(font, txt, x + 10, y + 4, InterfaceHD.AIRAIN_SOMBRE, true);
		int x0 = x + 10 + font.width(txt) + 2, w = xFin - 2 - x0;
		if (w > 0) g.blit(ATLAS, x0, y + 10, w, 1, 320, 160, Math.min(w, 100), 1, 512, 256);
	}

	/** Valeur d'un réglage dans un cartouche émaillé (texte crème, ou gris si le réglage est sans effet). */
	public static void cartouche(GuiGraphics g, Font font, int x, int y, int w, Component txt, boolean sansEffet) {
		troisTranches(g, x, y, w, 16, 320, 48, 6);
		g.drawString(font, txt, x + w / 2 - font.width(txt) / 2, y + 4, sansEffet ? 0x7A7468 : 0xFFE9B0, true);
	}

	/** Creux d'un champ de saisie (cramoisi pendant la saisie). */
	public static void champ(GuiGraphics g, int x, int y, int w, boolean saisie) { troisTranches(g, x, y, w, 16, 320, saisie ? 80 : 64, 3); }

	/** Touche émaillée (choix parmi quelques valeurs) ; l'active est cramoisie et enfoncée. */
	public static void touche(GuiGraphics g, int x, int y, int w, boolean active) { troisTranches(g, x, y, w, 16, 320, active ? 112 : 96, 3); }

	/** Pastille d'émail 10x10 sertie d'airain ; la choisie porte un anneau cramoisi. */
	public static void email(GuiGraphics g, int x, int y, int couleur, boolean choisie) {
		g.fill(x + 1, y + 1, x + 9, y + 9, 0xFF000000 | couleur);
		blit(g, x, y, choisie ? 410 : 400, 32, 10, 10);
	}

	/** Lampe verte 14x14 (une liaison est active). */
	public static void lampe(GuiGraphics g, int x, int y) { blit(g, x, y, 420, 32, 14, 14); }

	/** Bouton rond 16x16 : 0 plus, 1 moins, 2 haut, 3 bas. */
	public static void rond(GuiGraphics g, int x, int y, int symbole, boolean survol) { blit(g, x, y, 320 + symbole * 16, survol ? 144 : 128, 16, 16); }

	/** Bouton radio 11x11 (douille d'airain, perle quand il est choisi). */
	public static void radio(GuiGraphics g, int x, int y, boolean choisi, boolean survol) { blit(g, x, y, 440 + (choisi ? 11 : 0) + (survol ? 22 : 0), 32, 11, 11); }

	/** Case à cocher 11x11 (coche d'airain). */
	public static void caseACocher(GuiGraphics g, int x, int y, boolean cochee) { blit(g, x, y, cochee ? 495 : 484, 32, 11, 11); }

	/** Touche à texte : active (cramoisie, enfoncée), survolée (rebord cramoisi) ou normale. */
	public static void toucheTexte(GuiGraphics g, Font font, int x, int y, int w, boolean active, boolean survol, Component txt) {
		troisTranches(g, x, y, w, 16, 320, active ? 112 : survol ? 176 : 96, 3);
		if (txt != null) g.drawString(font, txt, x + w / 2 - font.width(txt) / 2, y + 4, active ? 0xFFE9B0 : InterfaceHD.AIRAIN_SOMBRE, true);
	}

	/** Rainure gravée horizontale. */
	public static void rainure(GuiGraphics g, int x0, int x1, int y) {
		g.fill(x0, y, x1, y + 1, 0xFF25282F);
		g.fill(x0, y + 1, x1, y + 2, 0xFF454A56);
	}

	/** Abscisses des onglets (largeur = texte + 10) : ils se chevauchent s'ils ne tiennent pas dans les 197 px du bac. */
	public static int[] placeOnglets(Font font, Component[] noms, int x) {
		int n = noms.length, somme = 0;
		int[] l = new int[n];
		for (int k = 0; k < n; k++) { l[k] = font.width(noms[k]) + 10; somme += l[k]; }
		float recouvre = n > 1 ? Math.max(0, (somme - 197) / (float) (n - 1)) : 0;
		int[] xs = new int[2 * n];
		float cx = x + 1;
		for (int k = 0; k < n; k++) { xs[k] = Math.round(cx); xs[n + k] = l[k]; cx += l[k] - recouvre; }
		return xs;
	}
}
