package fr.chatmort.airain.fondation;

import net.minecraft.resources.ResourceLocation;

/**
 * Apparence de l'étendard : style, couleur du fond, couleur des ornements, motif, forme du bas (listes imposées).
 * Les réglages suivants ne servent qu'au grand étendard : longueur, largeur, vent, franges, fleuron,
 * bannière double, lanternes, et « masque » (étendard décoratif : ni titre à l'écran ni ligne dans le registre).
 * Rangement sur 32 bits : 4 bits pour chacun des cinq premiers, puis 2/2/2/1/2/1/1/1 bits ; chaque réglage du grand
 * étendard est stocké en écart à sa valeur par défaut, si bien qu'un 0 (étendard plus ancien) donne les défauts.
 */
public record Apparence(int style, int fond, int ornement, int motif, int forme,
		int longueur, int largeur, int vent, int franges, int fleuron, int double_, int lanternes, int masque) {
	public static final int[] FONDS = {0x8E1A16, 0x1E3A6E, 0x1F4D2E, 0x1C1A1C, 0xE6DCC2, 0x5A1E5E, 0xB8792A, 0x5E6670};
	public static final int[] ORNEMENTS = {0xE8BE5A, 0xD8DCE0, 0xC77A48, 0x282222};
	public static final String[] MOTIFS = {"rouage", "cle", "flamme", "couronne", "ancre", "eclair", "etoile", "rouage_brise", "cristal", "fiole", "aucun"};
	public static final String[] FORMES = {"aronde", "droit", "pointe"};
	public static final int STYLES = 3;
	/** Grand étendard : longueur et largeur de la bannière en pixels, force du vent. */
	public static final int[] LONGUEURS = {48, 56, 64};
	public static final int[] LARGEURS = {20, 24, 28, 32};
	public static final float[] VENTS = {0.45f, 1f, 1.7f};
	/** Fleurons : pointe, globe, rouage, couronne. */
	public static final int FLEURONS = 4;
	/** Taille de chaque réglage, dans l'ordre du constructeur. */
	public static final int[] TAILLES = {STYLES, FONDS.length, ORNEMENTS.length, MOTIFS.length, FORMES.length,
		LONGUEURS.length, LARGEURS.length, VENTS.length, 2, FLEURONS, 2, 2, 2};
	private static final int[] DEFAUTS_GRAND = {1, 1, 1, 0, 0, 0, 0, 0};
	private static final int[] BITS_GRAND = {2, 2, 2, 1, 2, 1, 1, 1};
	public static final Apparence DEFAUT = depuis(new int[] {0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0});

	public int[] valeurs() {
		return new int[] {style, fond, ornement, motif, forme, longueur, largeur, vent, franges, fleuron, double_, lanternes, masque};
	}

	public static Apparence depuis(int[] v) {
		return new Apparence(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12]);
	}

	public boolean avecFranges() { return franges == 1; }
	public boolean estDouble() { return double_ == 1; }
	public boolean avecLanternes() { return lanternes == 1; }
	public boolean estMasque() { return masque == 1; }

	public int pack() {
		int[] v = valeurs();
		int r = style | fond << 4 | ornement << 8 | motif << 12 | forme << 16, decal = 20;
		for (int k = 0; k < BITS_GRAND.length; k++) {
			int n = TAILLES[5 + k];
			r |= Math.floorMod(v[5 + k] - DEFAUTS_GRAND[k], n) << decal;
			decal += BITS_GRAND[k];
		}
		return r;
	}

	public static Apparence unpack(int p) {
		int[] v = new int[13];
		for (int k = 0; k < 5; k++) v[k] = borne(p >> 4 * k & 15, TAILLES[k]);
		int decal = 20;
		for (int k = 0; k < BITS_GRAND.length; k++) {
			int n = TAILLES[5 + k];
			v[5 + k] = borne((p >>> decal & (1 << BITS_GRAND[k]) - 1) + DEFAUTS_GRAND[k], n);
			decal += BITS_GRAND[k];
		}
		return depuis(v);
	}

	private static int borne(int v, int n) {
		return Math.floorMod(v, n);
	}

	public ResourceLocation texFond() { return tex("fond_" + FORMES[forme]); }
	public ResourceLocation texOrnement() { return tex("ornement_" + FORMES[forme]); }
	public ResourceLocation texMotif() { return MOTIFS[motif].equals("aucun") ? null : tex("motif_" + MOTIFS[motif]); }

	private static ResourceLocation tex(String n) {
		return ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/etendard/" + n + ".png");
	}
}
