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
		CHECKERBOARD(Reglage.CASE, 1, 4, 1, false), HERRINGBONE(Reglage.CASE, 1, 4, 1, false), OFFSET_PAVERS(Reglage.CASE, 1, 4, 1, false),
		DIAMONDS(Reglage.TAILLE, 5, 21, 9, true), STRIPES(Reglage.CASE, 1, 4, 1, false), DIAGONALS(Reglage.CASE, 1, 4, 1, false),
		ROSETTE(Reglage.TAILLE, 8, 24, 12, true), BASKETWEAVE(Reglage.CASE, 1, 4, 1, false),
		RUNNING_BOND(Reglage.CASE, 1, 4, 1, false), WAINSCOT(Reglage.TAILLE, 3, 12, 6, true), PILASTERS(Reglage.TAILLE, 3, 12, 5, false),
		FRIEZE(Reglage.TAILLE, 4, 12, 6, true), COFFERS(Reglage.TAILLE, 3, 12, 5, true), CROSSED_BEAMS(Reglage.TAILLE, 4, 16, 8, false),
		GRID(Reglage.CASE, 1, 6, 3, false);

		public final Reglage reglage; public final int min, max, defaut; public final boolean accent;
		Dessin(Reglage r, int min, int max, int d, boolean a) { reglage = r; this.min = min; this.max = max; defaut = d; accent = a; }
		public String cle() { return "airain.carreleur.motif." + name().toLowerCase(); }
	}

	public static final List<List<Dessin>> PAR_TYPE = List.of(
		List.of(Dessin.CHECKERBOARD, Dessin.HERRINGBONE, Dessin.OFFSET_PAVERS, Dessin.DIAMONDS, Dessin.STRIPES, Dessin.DIAGONALS, Dessin.ROSETTE, Dessin.BASKETWEAVE),
		List.of(Dessin.RUNNING_BOND, Dessin.WAINSCOT, Dessin.PILASTERS, Dessin.FRIEZE, Dessin.CHECKERBOARD, Dessin.STRIPES, Dessin.DIAGONALS),
		List.of(Dessin.COFFERS, Dessin.CROSSED_BEAMS, Dessin.GRID, Dessin.CHECKERBOARD, Dessin.ROSETTE, Dessin.DIAMONDS));

	/** La tuile de rôles [v][u] du dessin pour ce réglage (borné). */
	public static int[][] tuile(Dessin d, int p) {
		p = Math.max(d.min, Math.min(d.max, p));
		int c = p, n = p;
		switch (d) {
			case CHECKERBOARD -> { return remplir(2 * c, 2 * c, (u, v) -> (u / c + v / c) % 2); }
			case STRIPES -> { return remplir(2 * c, 1, (u, v) -> (u / c) % 2); }
			case DIAGONALS -> { return remplir(2 * c, 2 * c, (u, v) -> ((u + v) % (2 * c)) / c); }
			case HERRINGBONE -> { return remplir(4 * c, 4 * c, (u, v) -> ((u / c - v / c) & 3) < 2 ? 0 : 1); }
			case OFFSET_PAVERS, RUNNING_BOND -> {
				return remplir(4 * c, 2 * c, (u, v) -> { int rang = v / c; int b = ((u + (rang % 2) * c) % (4 * c)) / (2 * c); return (b + rang) % 2; });
			}
			case BASKETWEAVE -> { return remplir(4 * c, 4 * c, (u, v) -> ((u / (2 * c) + v / (2 * c)) % 2 == 0) ? (u / c) % 2 : (v / c) % 2); }
			case DIAMONDS -> {
				double m = (n - 1) / 2.0;
				return remplir(n, n, (u, v) -> { double e = Math.abs(u - m) + Math.abs(v - m); return e <= 1 ? 2 : (e > m - 1.5 && e <= m + 0.01) ? 1 : 0; });
			}
			case ROSETTE -> {
				double m = (n - 1) / 2.0;
				return remplir(n, n, (u, v) -> {
					double x = u - m, y = v - m, r = Math.hypot(x, y) / (n / 2.0), a = Math.atan2(y, x);
					if (r < 0.22) return 2;
					if (r > 0.3 && r < 0.8 && Math.cos(8 * a) > 0.45) return 1;
					if (r > 0.86 && r < 1.02) return 1;
					return 0;
				});
			}
			case WAINSCOT -> { int bas = Math.max(1, n / 3); return remplir(1, n, (u, v) -> v < bas ? 1 : v == bas ? 2 : 0); }
			case PILASTERS -> { return remplir(n, 1, (u, v) -> u == 0 ? 1 : 0); }
			case FRIEZE -> { int mi = n / 2; return remplir(4, n, (u, v) -> (v == mi || v == mi - 1) ? (u % 4 < 2 ? 1 : 2) : 0); }
			case COFFERS -> { return remplir(n, n, (u, v) -> (u == 0 || v == 0) ? 1 : (u == n / 2 && v == n / 2) ? 2 : 0); }
			case CROSSED_BEAMS -> { return remplir(n, n, (u, v) -> (u == 0 || v == 0 || u == v || u == n - v) ? 1 : 0); }
			case GRID -> { return remplir(c + 1, c + 1, (u, v) -> (u == 0 || v == 0) ? 1 : 0); }
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
