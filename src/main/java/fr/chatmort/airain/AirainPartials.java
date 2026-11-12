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

	private static PartialModel bloc(String chemin) {
		return PartialModel.of(ResourceLocation.fromNamespaceAndPath(AirainMod.ID, "block/" + chemin));
	}

	/** Force le chargement de la classe avant la cuisson des modèles. */
	public static void init() {
	}
}
