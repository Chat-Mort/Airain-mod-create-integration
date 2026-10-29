package fr.chatmort.airain.fondation;

import net.minecraft.resources.ResourceLocation;

/**
 * Apparence de l'étendard : style, couleur du fond, couleur des ornements, motif, forme du bas (listes imposées).
 * Longueur, largeur et vent ne servent qu'au grand étendard.
 */
public record Apparence(int style, int fond, int ornement, int motif, int forme, int longueur, int largeur, int vent) {
	public static final int[] FONDS = {0x8E1A16, 0x1E3A6E, 0x1F4D2E, 0x1C1A1C, 0xE6DCC2, 0x5A1E5E, 0xB8792A, 0x5E6670};
	public static final int[] ORNEMENTS = {0xE8BE5A, 0xD8DCE0, 0xC77A48, 0x282222};
	public static final String[] MOTIFS = {"rouage", "cle", "flamme", "couronne", "ancre", "eclair", "etoile", "rouage_brise", "cristal", "fiole", "aucun"};
	public static final String[] FORMES = {"aronde", "droit", "pointe"};
	public static final int STYLES = 3;
	/** Grand étendard : longueur et largeur de la bannière en pixels, force du vent. */
	public static final int[] LONGUEURS = {48, 56, 64};
	public static final int[] LARGEURS = {20, 24, 28, 32};
	public static final float[] VENTS = {0.45f, 1f, 1.7f};
	public static final Apparence DEFAUT = new Apparence(0, 0, 0, 0, 0, 1, 1, 1);

	public int pack() {
		return style | fond << 4 | ornement << 8 | motif << 12 | forme << 16 | (longueur + 1) << 20 | (largeur + 1) << 24 | (vent + 1) << 28;
	}

	public static Apparence unpack(int v) {
		return new Apparence(borne(v & 15, STYLES), borne(v >> 4 & 15, FONDS.length), borne(v >> 8 & 15, ORNEMENTS.length),
			borne(v >> 12 & 15, MOTIFS.length), borne(v >> 16 & 15, FORMES.length),
			grand(v >> 20 & 15, LONGUEURS.length, 1), grand(v >> 24 & 15, LARGEURS.length, 1), grand(v >>> 28 & 15, VENTS.length, 1));
	}

	/** Stocké +1 : 0 = ancien étendard sans réglage, on prend la valeur par défaut. */
	private static int grand(int v, int n, int defaut) {
		return v == 0 ? defaut : borne(v - 1, n);
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
