package fr.chatmort.airain.affichage;

import net.minecraft.client.gui.Font;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.resources.ResourceLocation;

import java.util.ArrayList;
import java.util.List;
import java.util.function.IntFunction;

/**
 * Mise en page du contenu d'un tableau émaillé, partagée par le rendu dans le monde et l'aperçu du menu. Les mesures
 * sont en pixels de modèle (16 par bloc), depuis le coin en haut à gauche de la surface émaillée, y vers le bas.
 */
public final class MiseEnPage {
	private MiseEnPage() {}
	/** Taille d'un pixel de police selon la taille choisie (petite, moyenne, grande), en pixels de modèle. */
	public static final float[] ECHELLE = {0.16f, 0.25f, 0.4f};
	public static final ResourceLocation IMPERIALE = ResourceLocation.fromNamespaceAndPath("airain", "imperiale");

	/** Ce que sait dessiner celui qui affiche (monde ou écran). */
	public interface Peintre {
		/** Texte à (x, y), haut à gauche, s pixels de modèle par pixel de police ; grave : lettres en creux. */
		void texte(Component t, float x, float y, float s, int couleur, boolean grave);
		void rect(float x0, float y0, float x1, float y1, int couleur);
		/** Baguette d'airain en relief (ou simple trait). */
		void baguette(float x0, float y0, float x1, float y1);
	}

	public static Style style(Reglages r, boolean gras) {
		Style s = Style.EMPTY.withBold(gras);
		return r.police == 1 ? s.withFont(IMPERIALE) : s;
	}
	private static float hauteur(Reglages.Ligne l) {
		float s = ECHELLE[l.taille];
		return switch (l.type) { case Reglages.FILET -> 4 * s + 1; case Reglages.COLONNE -> 0; default -> 10 * s; };
	}
	/** Le texte affiché d'une ligne : la valeur reçue par la liaison d'affichage passe avant le texte écrit (titres et textes). */
	private static String affiche(Reglages.Ligne l, String v) {
		if ((l.type == Reglages.TITRE || l.type == Reglages.TEXTE) && v != null && !v.isEmpty()) return v;
		return l.texte;
	}

	/** valeur.apply(i) : la valeur reçue pour la i-ème ligne de cette face (indices de liaison). */
	public static void dessiner(Peintre p, Font f, Reglages r, List<Reglages.Ligne> lignes, IntFunction<String> valeur, float W, float H) {
		int col = -1;
		for (int i = 0; i < lignes.size(); i++) if (lignes.get(i).type == Reglages.COLONNE) { col = i; break; }
		int tete = 0;
		if (col > 0) while (tete < col && lignes.get(tete).type == Reglages.TITRE) tete++;
		List<Integer> haut = new ArrayList<>(), gauche = new ArrayList<>(), droite = new ArrayList<>();
		for (int i = 0; i < lignes.size(); i++) {
			if (i < tete) haut.add(i);
			else if (col < 0 || i < col) gauche.add(i);
			else if (i > col) droite.add(i);
		}
		float hH = 0, hG = 0, hD = 0;
		for (int i : haut) hH += hauteur(lignes.get(i));
		for (int i : gauche) hG += hauteur(lignes.get(i));
		for (int i : droite) hD += hauteur(lignes.get(i));
		boolean separe = col >= 0;
		float ecart = separe && tete > 0 ? 3 : 0;
		float total = hH + ecart + Math.max(hG, hD);
		float k = total > H && total > 0 ? H / total : 1;               // tout tient : on réduit au besoin
		float y = (H - total * k) / 2, m = 1.5f;
		for (int i : haut) { ligne(p, f, r, lignes.get(i), valeur.apply(i), m, W - m, y, k); y += hauteur(lignes.get(i)) * k; }
		if (separe && tete > 0 && r.baguettes) p.baguette(0, y + ecart * k / 2 - 0.5f, W, y + ecart * k / 2 + 0.5f);
		y += ecart * k;
		float yc = y, mi = W / 2;
		if (separe && r.baguettes) p.baguette(mi - 0.6f, yc, mi + 0.6f, Math.min(H, yc + Math.max(hG, hD) * k));
		float x1g = separe ? mi - 2 : W - m;
		for (int i : gauche) { ligne(p, f, r, lignes.get(i), valeur.apply(i), m, x1g, y, k); y += hauteur(lignes.get(i)) * k; }
		y = yc;
		for (int i : droite) { ligne(p, f, r, lignes.get(i), valeur.apply(i), mi + 2, W - m, y, k); y += hauteur(lignes.get(i)) * k; }
	}

	private static void ligne(Peintre p, Font f, Reglages r, Reglages.Ligne l, String v, float x0, float x1, float y, float k) {
		float s = ECHELLE[l.taille] * k;
		boolean grave = r.police == 2;
		int c = Reglages.PALETTE[l.couleur], cv = Reglages.PALETTE[r.coulValeur];
		float l_ = x1 - x0;
		switch (l.type) {
			case Reglages.FILET -> p.rect(x0, y + 2 * s, x1, y + 2 * s + Math.max(0.4f, 0.6f * s), c);
			case Reglages.VIDE, Reglages.COLONNE -> {}
			case Reglages.VALEUR, Reglages.BARRE -> {
				MutableComponent nom = Component.literal(l.texte).withStyle(style(r, false));
				String val = v == null || v.isEmpty() ? "—" : v;
				if (l.type == Reglages.BARRE) val = Math.round(Reglages.proportion(v) * 100) + " %";
				MutableComponent va = Component.literal(val).withStyle(style(r, false));
				float wn = f.width(nom), wv = f.width(va);
				float place = l.type == Reglages.BARRE ? wn + wv + 30 : wn + wv + 6;
				float ss = place * s > l_ ? l_ / place : s;
				float yy = y + (10 * s - 8 * ss) / 2;
				p.texte(nom, x0, yy, ss, c, grave);
				p.texte(va, x1 - wv * ss, yy, ss, cv, grave);
				if (l.type == Reglages.BARRE) {
					float b0 = x0 + (wn + 3) * ss, b1 = x1 - (wv + 3) * ss, h0 = yy + 1.5f * ss, h1 = yy + 6.5f * ss;
					if (b1 - b0 > 1) {
						p.rect(b0, h0, b1, h1, 0x3E3A34);
						float fr = Reglages.proportion(v);
						int n = Math.max(1, Math.round((b1 - b0) / (4 * ss)));
						float pas = (b1 - b0) / n;
						for (int i = 0; i < Math.round(fr * n); i++) p.rect(b0 + i * pas + 0.3f * ss, h0 + 0.5f * ss, b0 + (i + 1) * pas - 0.3f * ss, h1 - 0.5f * ss, cv);
					}
				}
			}
			default -> {
				MutableComponent t = Component.literal(affiche(l, v)).withStyle(style(r, l.type == Reglages.TITRE || l.type == Reglages.SECTION));
				float w = f.width(t);
				float ss = w * s > l_ ? l_ / w : s;
				float x = switch (l.align) { case 1 -> x0 + (l_ - w * ss) / 2; case 2 -> x1 - w * ss; default -> x0; };
				p.texte(t, x, y + (10 * s - 8 * ss) / 2, ss, c, grave);
			}
		}
	}
}
