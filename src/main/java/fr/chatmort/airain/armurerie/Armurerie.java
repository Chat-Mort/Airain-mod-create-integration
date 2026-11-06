package fr.chatmort.airain.armurerie;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Les deux manuels des armes : le Règlement des armes de l'Empire et le Traité des armes de l'Écho.
 * Une entrée par arme, par ensemble d'armure ou par coiffe. Une entrée se dévoile quand l'un de ses objets
 * a été porté une fois dans l'inventaire (suivi partagé dans les Chroniques, voir Chronique.armes).
 * Textes : airain.armurerie.<clé>.sous_titre / .citation / .p1, .p2… (pouvoirs) dans les fichiers de langue.
 */
public final class Armurerie {
	private Armurerie() {}

	/** sorte : ARME (statistiques d'arme), ENSEMBLE (quatre pièces d'armure), COIFFE (une ou plusieurs coiffes). */
	public enum Sorte { ARME, ENSEMBLE, COIFFE }

	/** Une page du manuel : sa clé de texte, sa sorte, et les objets qu'elle présente (identifiants sans « airain: »). */
	public record Entree(String cle, Sorte sorte, List<String> objets) {}

	private static Entree arme(String id) { return new Entree(id, Sorte.ARME, List.of(id)); }

	/** Le Règlement des armes de l'Empire, dans l'ordre des pages. */
	public static final List<Entree> EMPIRE = List.of(
		arme("sacred_sword"), arme("sacred_katana"), arme("sacred_greatsword"), arme("sacred_twinblade"), arme("sacred_pickaxe"),
		arme("imperial_sword"), arme("imperial_katana"), arme("imperial_greatsword"), arme("imperial_twinblade"), arme("imperial_pickaxe"),
		arme("imperial_scepter"),
		new Entree("couronnes", Sorte.COIFFE, List.of("airain_crown", "crowned_helmet", "sacred_crown")),
		new Entree("armure_sacree", Sorte.ENSEMBLE, List.of("sacred_crown", "sacred_chestplate", "sacred_leggings", "sacred_boots")),
		new Entree("armure_imperiale", Sorte.ENSEMBLE, List.of("imperial_helmet", "imperial_chestplate", "imperial_leggings", "imperial_boots")));

	/** Le Traité des armes de l'Écho, dans l'ordre des pages. */
	public static final List<Entree> ECHO = List.of(
		arme("runic_sword"), arme("runic_katana"), arme("runic_greatsword"), arme("runic_twinblade"), arme("runic_pickaxe"),
		arme("arcane_sword"), arme("arcane_katana"), arme("arcane_greatsword"), arme("arcane_twinblade"), arme("arcane_pickaxe"),
		arme("arcane_scepter"),
		new Entree("diademe", Sorte.COIFFE, List.of("echo_diadem", "diadem_helmet")),
		new Entree("armure_runique", Sorte.ENSEMBLE, List.of("runic_helmet", "runic_chestplate", "runic_leggings", "runic_boots")),
		new Entree("armure_arcanique", Sorte.ENSEMBLE, List.of("arcane_helmet", "arcane_chestplate", "arcane_leggings", "arcane_boots")));

	public static List<Entree> de(boolean echo) { return echo ? ECHO : EMPIRE; }

	/** Tous les objets suivis (pour repérer ceux qu'un joueur porte). */
	public static final Set<String> SUIVIS = new HashSet<>();
	static {
		for (Entree e : EMPIRE) SUIVIS.addAll(e.objets());
		for (Entree e : ECHO) SUIVIS.addAll(e.objets());
	}
}
