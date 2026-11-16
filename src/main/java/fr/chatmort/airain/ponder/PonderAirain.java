package fr.chatmort.airain.ponder;

import net.createmod.ponder.api.registration.PonderPlugin;
import net.createmod.ponder.api.registration.PonderSceneRegistrationHelper;
import net.minecraft.resources.ResourceLocation;

/** 1.64 : les scènes Ponder du mod, rattachées aux objets (touche W au survol, comme pour Create). */
public class PonderAirain implements PonderPlugin {
	@Override public String getModId() { return "airain"; }

	private static ResourceLocation rl(String p) { return ResourceLocation.fromNamespaceAndPath("airain", p); }

	@Override
	public void registerScenes(PonderSceneRegistrationHelper<ResourceLocation> h) {
		h.forComponents(rl("blast_furnace_taphole"), rl("blast_furnace_tuyere"), rl("blast_furnace_hopper"), rl("fire_bricks"))
			.addStoryBoard("haut_fourneau", ScenesAirain::hautFourneau);
		h.forComponents(rl("airain_rolling_mill"), rl("airain_wire"), rl("airain_cable"))
			.addStoryBoard("laminoir", ScenesAirain::laminoir);
		h.forComponents(rl("airain_cable_station"), rl("airain_pylon"), rl("airain_pylon_head"), rl("airain_gondola"))
			.addStoryBoard("telepherique", ScenesAirain::telepherique);
		h.forComponents(rl("airain_lift_winch"), rl("airain_lift_mast"), rl("airain_lift_call_box"))
			.addStoryBoard("monte_charge", ScenesAirain::monteCharge);
		h.forComponents(rl("airain_catwalk_drawbridge"), rl("airain_catwalk_telescopic"))
			.addStoryBoard("passages_mobiles", ScenesAirain::passagesMobiles);
		h.forComponents(rl("airain_air_duct"), rl("airain_air_vent"))
			.addStoryBoard("conduite_air", ScenesAirain::conduiteAir);
		h.forComponents(rl("airain_rack"), rl("rack_reinforcement_1"), rl("rack_reinforcement_2"), rl("rack_reinforcement_3"), rl("rack_reinforcement_4"))
			.addStoryBoard("rayonnage", ScenesAirain::rayonnage);
		h.forComponents(rl("enamel_board"))
			.addStoryBoard("tableau_emaille", ScenesAirain::tableauEmaille);
	}
}
