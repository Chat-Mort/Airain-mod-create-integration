package fr.chatmort.airain.fonderie;

import java.util.List;

/**
 * 1.70 : les motifs tout faits de la table du carreleur. Chaque dessin rend une tuile de rôles
 * (0 = couleur A, 1 = couleur B, 2 = accent) ; la tuile est ensuite répétée par le cordeau.
 * Pour un mur, v compte depuis le bas.
 */
public final class Generateur {
	private Generateur() {}

	public static final int SOL = 0, MUR = 1, PLAFOND = 2;
	public static final String[] TYPES = {"floor", "wall", "ceiling"};
	/** CASE : taille des cases (motifs simples) ; TAILLE : taille du motif, redessiné à cette taille (motifs complexes). */
	public enum Reglage { CASE, TAILLE }

	public enum Dessin {
		CHECKERBOARD(Reglage.CASE, 1, 4, 1, false), CHEVRONS(Reglage.CASE, 2, 4, 2, false), OFFSET_PAVERS(Reglage.CASE, 1, 4, 2, false),
		DIAMONDS(Reglage.TAILLE, 5, 21, 9, true), STRIPES(Reglage.CASE, 1, 4, 1, false), DIAGONALS(Reglage.CASE, 2, 4, 2, false),
		ROSETTE(Reglage.TAILLE, 9, 24, 15, true), CABOCHONS(Reglage.TAILLE, 3, 8, 4, false),
		RUNNING_BOND(Reglage.CASE, 1, 4, 2, false), WAINSCOT(Reglage.TAILLE, 2, 12, 4, true), PILASTERS(Reglage.TAILLE, 3, 12, 5, false),
		FRIEZE(Reglage.TAILLE, 1, 12, 4, true), COFFERS(Reglage.TAILLE, 3, 12, 5, true), CROSSED_BEAMS(Reglage.TAILLE, 4, 16, 8, false),
		GRID(Reglage.CASE, 1, 6, 3, false),
		// 1.70.2 : motifs dessinés par Liam (8 x 8 ; le réglage multiplie chaque case : 1, 2 ou 3 blocs)
		MEDALLION(Reglage.CASE, 1, 3, 1, true), RING(Reglage.CASE, 1, 3, 1, true), FRAMES(Reglage.CASE, 1, 3, 1, true), DOTTED_CHECKER(Reglage.CASE, 1, 3, 1, true);

		public final Reglage reglage; public final int min, max, defaut; public final boolean accent;
		Dessin(Reglage r, int min, int max, int d, boolean a) { reglage = r; this.min = min; this.max = max; defaut = d; accent = a; }
		public String cle() { return "airain.carreleur.motif." + name().toLowerCase(); }
		/** Soubassement et frise : posés une seule fois, depuis le bas du mur (le reste du mur en couleur A). */
		public boolean uniqueV() { return this == WAINSCOT || this == FRIEZE; }
	}

	public static final List<List<Dessin>> PAR_TYPE = List.of(
		List.of(Dessin.CHECKERBOARD, Dessin.CHEVRONS, Dessin.OFFSET_PAVERS, Dessin.DIAMONDS, Dessin.STRIPES, Dessin.DIAGONALS, Dessin.ROSETTE, Dessin.CABOCHONS,
			Dessin.MEDALLION, Dessin.RING, Dessin.FRAMES, Dessin.DOTTED_CHECKER),
		List.of(Dessin.RUNNING_BOND, Dessin.WAINSCOT, Dessin.PILASTERS, Dessin.FRIEZE, Dessin.CHECKERBOARD, Dessin.STRIPES, Dessin.DIAGONALS),
		List.of(Dessin.COFFERS, Dessin.CROSSED_BEAMS, Dessin.GRID, Dessin.CHECKERBOARD, Dessin.ROSETTE, Dessin.DIAMONDS,
			Dessin.MEDALLION, Dessin.RING, Dessin.FRAMES, Dessin.DOTTED_CHECKER));

	// motifs de Liam : A = foncé (noir), B = moyen (blanc), C = accent (rouge) ; première ligne en haut
	private static final String[] MEDAILLON = {"AAAAAAAA", "ABABBABA", "AABBBBAA", "ABBCCBBA", "ABBCCBBA", "AABBBBAA", "ABABBABA", "AAAAAAAA"};
	private static final String[] ANNEAU = {"ABABBABA", "BABAABAB", "ABACCABA", "BACBBCAB", "BACBBCAB", "ABACCABA", "BABAABAB", "ABABBABA"};
	private static final String[] CADRES = {"ACCCCCCB", "CABBAABC", "CBACCBAC", "CBCABCAC", "CACBACBC", "CABCCABC", "CBAABBAC", "BCCCCCCA"};
	private static final String[] DAMIER_POINTE = {"ABBAABBA", "BCABBACB", "BAABBAAB", "ABBAABBA", "ABBAABBA", "BAABBAAB", "BCABBACB", "ABBAABBA"};
	private static int[][] dessin(String[] g, int c) { return remplir(8 * c, 8 * c, (u, v) -> "ABC".indexOf(g[v / c].charAt(u / c))); }

	/** La tuile de rôles [v][u] du dessin pour ce réglage (borné). */
	public static int[][] tuile(Dessin d, int p) {
		p = Math.max(d.min, Math.min(d.max, p));
		int c = p, n = p;
		switch (d) {
			case CHECKERBOARD -> { return remplir(2 * c, 2 * c, (u, v) -> (u / c + v / c) % 2); }
			case STRIPES -> { return remplir(2 * c, 1, (u, v) -> (u / c) % 2); }
			// 1.70.2 : bande de c, écart de c (jamais un damier)
			case DIAGONALS -> { return remplir(2 * c, 2 * c, (u, v) -> (u + v) % (2 * c) < c ? 1 : 0); }
			// 1.70.2 : vrais chevrons en V (zigzag)
			case CHEVRONS -> { int p2 = 2 * c; return remplir(2 * p2, 2 * c, (u, v) -> ((Math.abs(u % (2 * p2) - p2) + v) / c) % 2); }
			// 1.70.2 : pavés ou briques de 2c x c en couleur A, joints d'un bloc en couleur B, rangs décalés d'une demi-brique
			case OFFSET_PAVERS, RUNNING_BOND -> {
				int l = 2 * c + 1, h = c + 1;
				return remplir(2 * l, 2 * h, (u, v) -> { if (v % h == c) return 1; int x = (u + ((v / h) % 2) * (l / 2 + 1)) % l; return x == l - 1 ? 1 : 0; });
			}
			// 1.70.2 : grands carreaux A, un cabochon B à chaque croisement
			case CABOCHONS -> { return remplir(n, n, (u, v) -> (u == 0 && v == 0) ? 1 : 0); }
			case DIAMONDS -> {
				double m = (n - 1) / 2.0;
				return remplir(n, n, (u, v) -> { double e = Math.abs(u - m) + Math.abs(v - m); return e <= 1 ? 2 : (e > m - 1.5 && e <= m + 0.01) ? 1 : 0; });
			}
			// 1.70.2 : huit pétales en ellipse autour du cœur, cercle extérieur
			case ROSETTE -> {
				double m = (n - 1) / 2.0;
				return remplir(n, n, (u, v) -> {
					double x = (u - m) / (n / 2.0), y = (v - m) / (n / 2.0), r = Math.hypot(x, y);
					if (r < 0.2) return 2;
					for (int k = 0; k < 8; k++) {
						double a = k * Math.PI / 4, dx = x - 0.55 * Math.cos(a), dy = y - 0.55 * Math.sin(a);
						double ra = dx * Math.cos(a) + dy * Math.sin(a), ta = -dx * Math.sin(a) + dy * Math.cos(a);
						if ((ra / 0.3) * (ra / 0.3) + (ta / 0.14) * (ta / 0.14) <= 1) return 1;
					}
					return r > 0.9 && r < 1.04 ? 1 : 0;
				});
			}
			// 1.70.2 : soubassement de n blocs (n - 1 en B, une ligne d'accent), posé une seule fois en bas
			case WAINSCOT -> { return remplir(1, n, (u, v) -> v < n - 1 ? 1 : 2); }
			case PILASTERS -> { return remplir(n, 1, (u, v) -> u == 0 ? 1 : 0); }
			// 1.70.2 : une seule frise, à n blocs du sol
			case FRIEZE -> { return remplir(4, n + 2, (u, v) -> v >= n ? (u % 4 < 2 ? 1 : 2) : 0); }
			case COFFERS -> { return remplir(n, n, (u, v) -> (u == 0 || v == 0) ? 1 : (u == n / 2 && v == n / 2) ? 2 : 0); }
			case CROSSED_BEAMS -> { return remplir(n, n, (u, v) -> (u == 0 || v == 0 || u == v || u == n - v) ? 1 : 0); }
			case GRID -> { return remplir(c + 1, c + 1, (u, v) -> (u == 0 || v == 0) ? 1 : 0); }
			case MEDALLION -> { return dessin(MEDAILLON, c); }
			case RING -> { return dessin(ANNEAU, c); }
			case FRAMES -> { return dessin(CADRES, c); }
			case DOTTED_CHECKER -> { return dessin(DAMIER_POINTE, c); }
			default -> { return remplir(1, 1, (u, v) -> 0); }
		}
	}
	private interface Role { int de(int u, int v); }
	private static int[][] remplir(int w, int h, Role r) {
		int[][] t = new int[h][w];
		for (int v = 0; v < h; v++) for (int u = 0; u < w; u++) t[v][u] = r.de(u, v);
		return t;
	}
}
