package fr.chatmort.airain.trophee;

/**
 * Réglages du piédestal : matériau, velours (couleur et capitonnage), garnitures, présentation du trophée,
 * colonne haute, éclairage, particules, plaque gravée. Rangés sur un entier ; chaque champ est stocké en écart
 * à sa valeur par défaut, si bien qu'un 0 (piédestal plus ancien) donne les défauts.
 */
public record SocleApparence(int materiau, int velours, int capitonnage, int garniture, int presentation,
		int grand, int lumiere, int particules, int plaque) {
	/** Matériaux : marbre, tuf, fonte noire, cuivre patiné, bois sombre. */
	public static final int MATERIAUX = 5;
	/** Présentations : lévitation, posé, chevalet, cloche de verre. */
	public static final int PRESENTATIONS = 4;
	public static final int[] TAILLES = {MATERIAUX, 8, 2, 4, PRESENTATIONS, 2, 2, 2, 2};
	private static final int[] DEFAUTS = {0, 0, 1, 0, 0, 0, 0, 1, 1};
	private static final int[] BITS = {3, 3, 1, 2, 2, 1, 1, 1, 1};
	public static final SocleApparence DEFAUT = depuis(DEFAUTS.clone());

	public int[] valeurs() {
		return new int[] {materiau, velours, capitonnage, garniture, presentation, grand, lumiere, particules, plaque};
	}

	public static SocleApparence depuis(int[] v) {
		return new SocleApparence(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8]);
	}

	public boolean losange() { return capitonnage == 1; }
	public boolean haute() { return grand == 1; }
	public boolean eclaire() { return lumiere == 1; }
	public boolean avecParticules() { return particules == 1; }
	public boolean avecPlaque() { return plaque == 1; }

	public int pack() {
		int[] v = valeurs(); int r = 0, d = 0;
		for (int k = 0; k < v.length; k++) {
			r |= Math.floorMod(v[k] - DEFAUTS[k], TAILLES[k]) << d;
			d += BITS[k];
		}
		return r;
	}

	public static SocleApparence unpack(int p) {
		int[] v = new int[TAILLES.length]; int d = 0;
		for (int k = 0; k < v.length; k++) {
			v[k] = Math.floorMod((p >> d & (1 << BITS[k]) - 1) + DEFAUTS[k], TAILLES[k]);
			d += BITS[k];
		}
		return depuis(v);
	}
}
