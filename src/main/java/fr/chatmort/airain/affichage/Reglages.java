package fr.chatmort.airain.affichage;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.util.ArrayList;
import java.util.List;

/**
 * 1.60 : tout ce que le menu du tableau émaillé règle, dans les deux sens (serveur ↔ écran). Les valeurs reçues par la
 * liaison d'affichage de Create sont gardées à part (elles ne viennent pas de l'écran).
 */
public final class Reglages {
	// ---- types de ligne
	public static final int TITRE = 0, SECTION = 1, TEXTE = 2, VALEUR = 3, BARRE = 4, FILET = 5, VIDE = 6, COLONNE = 7;
	public static final int NB_TYPES = 8;
	public static final int MAX_LIGNES = 24, MAX_TEXTE = 48;
	/** Couleurs du texte : crème, or, rouge, vert, bleu ciel, blanc, gris, encre. */
	public static final int[] PALETTE = {0xECE4CE, 0xE8C46E, 0xD64030, 0x78C878, 0x8CBEF0, 0xFFFFFF, 0x9A9A9A, 0x241A12};

	public static final class Ligne {
		public int type = TEXTE, align = 0, taille = 1, couleur = 0;
		public String texte = "";
		public Ligne() {}
		public Ligne(int type, String texte, int align, int taille, int couleur) { this.type = type; this.texte = texte; this.align = align; this.taille = taille; this.couleur = couleur; }
		public Ligne copie() { return new Ligne(type, texte, align, taille, couleur); }
		CompoundTag ecrire() {
			CompoundTag t = new CompoundTag();
			t.putByte("t", (byte) type); t.putString("x", texte); t.putByte("a", (byte) align); t.putByte("s", (byte) taille); t.putByte("c", (byte) couleur);
			return t;
		}
		static Ligne lire(CompoundTag t) {
			Ligne l = new Ligne(borne(t.getByte("t"), NB_TYPES), t.getString("x"), borne(t.getByte("a"), 3), borne(t.getByte("s"), 3), borne(t.getByte("c"), PALETTE.length));
			if (l.texte.length() > MAX_TEXTE) l.texte = l.texte.substring(0, MAX_TEXTE);
			return l;
		}
		/** Les lignes qui reçoivent une liaison d'affichage. */
		public boolean liee() { return type == VALEUR || type == BARRE || type == TEXTE || type == TITRE; }
	}

	public final List<Ligne> avant = new ArrayList<>(), arriere = new ArrayList<>();
	// style
	public int email = 15, cadre = 0, airain = 0;           // émail : couleur de colorant (15 = noir) ; cadre : riveté, lisse, marbre, aucun
	public boolean mat = false, ecusson = true, rosaces = true, baguettes = true;
	// police
	public int police = 0, coulTexte = 0, coulValeur = 1;    // Minecraft, impériale, gravée
	// lumière
	public int eclairage = 0, intensite = 10, allumage = 0;  // éteint, rétroéclairé, lettres ; toujours, redstone, alerte seulement
	public int alerteLigne = 0, seuil = 90, alerteAction = 0, alerteCouleur = 2;   // ligne 0 : pas d'alerte ; clignote ou s'allume
	// pose
	public int accrochage = 0;                               // auto, mur, pendu, sur pied
	public boolean memeFace = true;

	public static Reglages neufs() {
		Reglages r = new Reglages();
		r.avant.add(new Ligne(TITRE, "", 1, 2, 0));
		return r;
	}
	public boolean vide() { return avant.isEmpty() || (avant.size() == 1 && avant.get(0).texte.isEmpty() && arriere.isEmpty()); }

	private static int borne(int v, int n) { return Math.floorMod(v, n); }

	public CompoundTag ecrire() {
		CompoundTag t = new CompoundTag();
		t.put("avant", liste(avant)); t.put("arriere", liste(arriere));
		t.putByte("email", (byte) email); t.putByte("cadre", (byte) cadre); t.putByte("airain", (byte) airain);
		t.putBoolean("mat", mat); t.putBoolean("ecusson", ecusson); t.putBoolean("rosaces", rosaces); t.putBoolean("baguettes", baguettes);
		t.putByte("police", (byte) police); t.putByte("coulTexte", (byte) coulTexte); t.putByte("coulValeur", (byte) coulValeur);
		t.putByte("eclairage", (byte) eclairage); t.putByte("intensite", (byte) intensite); t.putByte("allumage", (byte) allumage);
		t.putByte("alerteLigne", (byte) alerteLigne); t.putInt("seuil", seuil); t.putByte("alerteAction", (byte) alerteAction); t.putByte("alerteCouleur", (byte) alerteCouleur);
		t.putByte("accrochage", (byte) accrochage); t.putBoolean("memeFace", memeFace);
		return t;
	}
	private static ListTag liste(List<Ligne> l) { ListTag t = new ListTag(); for (Ligne x : l) t.add(x.ecrire()); return t; }

	/** Lecture tolérante : tout est borné (le paquet vient du client). */
	public static Reglages lire(CompoundTag t) {
		Reglages r = new Reglages();
		if (!t.contains("avant")) return neufs();
		for (Tag x : t.getList("avant", Tag.TAG_COMPOUND)) if (r.avant.size() < MAX_LIGNES) r.avant.add(Ligne.lire((CompoundTag) x));
		for (Tag x : t.getList("arriere", Tag.TAG_COMPOUND)) if (r.arriere.size() < MAX_LIGNES) r.arriere.add(Ligne.lire((CompoundTag) x));
		r.email = borne(t.getByte("email"), 16); r.cadre = borne(t.getByte("cadre"), 4); r.airain = borne(t.getByte("airain"), 4);
		r.mat = t.getBoolean("mat"); r.ecusson = t.getBoolean("ecusson"); r.rosaces = t.getBoolean("rosaces"); r.baguettes = t.getBoolean("baguettes");
		r.police = borne(t.getByte("police"), 3); r.coulTexte = borne(t.getByte("coulTexte"), PALETTE.length); r.coulValeur = borne(t.getByte("coulValeur"), PALETTE.length);
		r.eclairage = borne(t.getByte("eclairage"), 3); r.intensite = Math.max(0, Math.min(15, t.getByte("intensite"))); r.allumage = borne(t.getByte("allumage"), 3);
		r.alerteLigne = Math.max(0, Math.min(MAX_LIGNES, t.getByte("alerteLigne"))); r.seuil = Math.max(-99999, Math.min(99999, t.getInt("seuil")));
		r.alerteAction = borne(t.getByte("alerteAction"), 2); r.alerteCouleur = borne(t.getByte("alerteCouleur"), PALETTE.length);
		r.accrochage = borne(t.getByte("accrochage"), 4); r.memeFace = t.getBoolean("memeFace");
		return r;
	}
	public Reglages copie() { return lire(ecrire()); }

	/** Lignes de la face (arrière : celles de l'avant si les deux faces sont pareilles). */
	public List<Ligne> face(boolean derriere) { return derriere && !memeFace ? arriere : avant; }

	// ---------------------------------------------------------------- lecture des valeurs reçues
	/** Proportion 0..1 tirée d'un texte : barre de Create (█ ▒), pourcentage, « a/b », ou nombre entre 0 et 1. */
	public static float proportion(String v) {
		if (v == null || v.isEmpty()) return 0;
		int plein = 0, vide = 0;
		for (char c : v.toCharArray()) { if (c == '█') plein++; else if (c == '▒') vide++; }
		if (plein + vide > 0) return plein / (float) (plein + vide);
		Double n = nombre(v);
		if (n == null) return 0;
		int barre = v.indexOf('/');
		if (barre > 0) {
			Double d = nombre(v.substring(barre + 1)), a = nombre(v.substring(0, barre));
			if (a != null && d != null && d > 0) return (float) Math.max(0, Math.min(1, a / d));
		}
		if (v.contains("%")) return (float) Math.max(0, Math.min(1, n / 100));
		return (float) Math.max(0, Math.min(1, n));
	}
	/** Premier nombre d'un texte (espaces et virgules de milliers ignorés, « , » ou « . » décimal). */
	public static Double nombre(String v) {
		if (v == null) return null;
		StringBuilder b = new StringBuilder(); boolean dedans = false;
		for (int i = 0; i < v.length(); i++) {
			char c = v.charAt(i);
			if (Character.isDigit(c) || (c == '-' && !dedans && i + 1 < v.length() && Character.isDigit(v.charAt(i + 1)))) { b.append(c); dedans = true; }
			else if (dedans && (c == ' ' || c == ' ' || c == ' ') && i + 1 < v.length() && Character.isDigit(v.charAt(i + 1))) continue;
			else if (dedans && (c == '.' || c == ',') && i + 1 < v.length() && Character.isDigit(v.charAt(i + 1))) b.append('.');
			else if (dedans) break;
		}
		try { return b.length() == 0 ? null : Double.parseDouble(b.toString()); } catch (NumberFormatException e) { return null; }
	}
	/** La valeur à comparer au seuil d'alerte : pourcentage si la ligne en montre un, sinon le nombre. */
	public static Double mesure(String v) {
		if (v == null || v.isEmpty()) return null;
		if (v.indexOf('█') >= 0 || v.indexOf('▒') >= 0 || v.contains("%")) return (double) (proportion(v) * 100);
		return nombre(v);
	}
}
