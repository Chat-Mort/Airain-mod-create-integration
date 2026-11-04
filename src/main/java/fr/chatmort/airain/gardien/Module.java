package fr.chatmort.airain.gardien;

import java.util.Locale;

/**
 * Modules de gardien : trois emplacements, deux modules au choix par emplacement, deux niveaux.
 * Le code d'un emplacement (0 = vide) vaut ordinal * 2 + niveau.
 */
public enum Module {
	LANTERNE(Emplacement.TETE), LUNETTE(Emplacement.TETE),
	CANON(Emplacement.EPAULES), TESLA(Emplacement.EPAULES),
	BLINDAGE(Emplacement.TORSE), CHAUDIERE(Emplacement.TORSE);

	public enum Emplacement { TETE, EPAULES, TORSE;
		public String nom() { return name().toLowerCase(Locale.ROOT); }
	}

	public final Emplacement emplacement;

	Module(Emplacement e) { emplacement = e; }

	public String nom() { return name().toLowerCase(Locale.ROOT); }
	private static final String[] ANGLAIS = {"lantern", "scope", "cannon", "tesla", "armor", "boiler"};
	public String id(int niveau) { return ANGLAIS[ordinal()] + "_module" + (niveau == 2 ? "_2" : ""); }
	public int code(int niveau) { return ordinal() * 2 + niveau; }

	public static Module de(int code) { return code <= 0 || code > values().length * 2 ? null : values()[(code - 1) / 2]; }
	public static int niveau(int code) { return code <= 0 ? 0 : (code - 1) % 2 + 1; }
}
