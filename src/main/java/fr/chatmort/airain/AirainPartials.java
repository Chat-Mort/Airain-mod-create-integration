package fr.chatmort.airain;

import dev.engine_room.flywheel.lib.model.baked.PartialModel;
import net.minecraft.resources.ResourceLocation;

/** Modèles animés, chargés à part des modèles de blocs. */
public class AirainPartials {
	public static final PartialModel MEULE = bloc("maintenance_bench/grindstone");
	public static final PartialModel HUILE = bloc("maintenance_bench/oil");
	public static final PartialModel CRISTAL = bloc("disenchanter/crystal");
	// Machines d'Écho : les pales de la turbine et l'engrenage du sourcelink, qui tournent
	public static final PartialModel ROTOR_TURBINE = bloc("echo_turbine/rotor");
	public static final PartialModel ROTOR_SOURCELINK = bloc("mechanical_sourcelink/rotor");

	// pièces d'atelier : aiguille du manomètre, réflecteur du gyrophare, flèche et planchette des bornes
	public static final PartialModel AIGUILLE = bloc("airain_gauge/needle");
	public static final PartialModel REFLECTEUR = bloc("airain_beacon_light/reflector");
	public static final PartialModel FLECHE = bloc("airain_signpost/arrow");
	public static final PartialModel PLANCHETTE = bloc("airain_signpost/board");

	// monte-charge : portail de la cabine pendant le trajet
	public static final PartialModel PORTAIL_CABINE = bloc("airain_lift_cabin/gate");

	// mécanique impériale : volant et lampes de l'allégeur, piston et voyant du surcompresseur
	public static final PartialModel[] VOLANT = teintes("airain_load_reliever/", "flywheel");
	public static final PartialModel LAMPES_ALLEGEUR = bloc("airain_load_reliever/lamps");
	public static final PartialModel[] PISTON = teintes("airain_supercharger/", "piston");
	public static final PartialModel VOYANT_SURCOMP = bloc("airain_supercharger/lamp");

	/** Une pièce animée par teinte de patine (neuf, terni, vieilli, rouge impérial). */
	private static PartialModel[] teintes(String dossier, String nom) {
		String[] p = {"", "exposed_", "weathered_", "oxidized_"};
		PartialModel[] t = new PartialModel[4];
		for (int i = 0; i < 4; i++) t[i] = bloc(dossier + p[i] + nom);
		return t;
	}
	/** Teinte (0 à 3) d'un bloc d'airain, d'après son nom (vaut aussi pour les versions cirées). */
	public static int teinte(net.minecraft.world.level.block.state.BlockState s) {
		String n = net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(s.getBlock()).getPath();
		return n.contains("oxidized_") ? 3 : n.contains("weathered_") ? 2 : n.contains("exposed_") ? 1 : 0;
	}

	private static PartialModel bloc(String chemin) {
		return PartialModel.of(ResourceLocation.fromNamespaceAndPath(AirainMod.ID, "block/" + chemin));
	}

	/** Force le chargement de la classe avant la cuisson des modèles. */
	public static void init() {
	}
}
