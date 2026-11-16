package fr.chatmort.airain.ponder;

import com.simibubi.create.foundation.ponder.CreateSceneBuilder;
import net.createmod.ponder.api.element.ElementLink;
import net.createmod.ponder.api.element.WorldSectionElement;
import net.createmod.ponder.api.scene.SceneBuilder;
import net.createmod.ponder.api.scene.SceneBuildingUtil;
import net.createmod.ponder.api.scene.Selection;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/** 1.64 : scènes Ponder (touche W de Create) des machines et pièces du mod. Textes : {@link PonderTextes}. */
public final class ScenesAirain {
	private ScenesAirain() {}

	private static void texte(CreateSceneBuilder s, String t, Vec3 ou, int duree, boolean cle) {
		var o = s.overlay().showText(duree).text(t).placeNearTarget().pointAt(ou);
		if (cle) o.attachKeyFrame();
		s.idle(duree + 10);
	}
	private static ItemStack objet(String id) { return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(id))); }

	// ---------------------------------------------------------------- le haut-fourneau
	public static void hautFourneau(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.HAUT_FOURNEAU;
		s.title("haut_fourneau", PonderTextes.HAUT_FOURNEAU_TITRE);
		s.configureBasePlate(0, 0, 9);
		s.scaleSceneView(0.8f);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(15);
		texte(s, T[0], u.vector().topOf(4, 0, 4), 70, false);
		s.world().showSection(u.select().fromTo(2, 1, 2, 6, 1, 6), Direction.DOWN);
		s.idle(10);
		s.world().showSection(u.select().fromTo(2, 2, 2, 6, 2, 6), Direction.DOWN);
		s.idle(15);
		texte(s, T[1], u.vector().blockSurface(new BlockPos(4, 1, 2), Direction.NORTH), 90, true);
		Selection souffle = u.select().fromTo(7, 2, 4, 8, 2, 4);
		s.world().showSection(souffle, Direction.WEST);
		s.world().setKineticSpeed(souffle, 64);
		s.idle(15);
		texte(s, T[2], u.vector().blockSurface(new BlockPos(6, 2, 4), Direction.EAST), 90, true);
		s.world().showSection(u.select().fromTo(3, 3, 3, 5, 5, 5), Direction.DOWN);
		s.idle(20);
		texte(s, T[3], u.vector().topOf(4, 5, 4), 80, true);
		texte(s, T[4], u.vector().blockSurface(new BlockPos(4, 1, 2), Direction.NORTH), 90, true);
		texte(s, T[5], u.vector().topOf(4, 5, 4), 110, true);
		s.world().showSection(u.select().fromTo(4, 1, 0, 4, 1, 1), Direction.SOUTH);
		s.idle(15);
		texte(s, T[6], u.vector().topOf(4, 1, 0), 80, false);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- le laminoir
	public static void laminoir(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.LAMINOIR;
		s.title("laminoir", PonderTextes.LAMINOIR_TITRE);
		s.configureBasePlate(0, 0, 5);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		s.world().showSection(u.select().position(2, 1, 2), Direction.DOWN);
		s.idle(10);
		Selection arbre = u.select().fromTo(2, 1, 2, 4, 1, 2);
		s.world().showSection(u.select().fromTo(3, 1, 2, 4, 1, 2), Direction.WEST);
		s.world().setKineticSpeed(arbre, 32);
		s.idle(15);
		texte(s, T[0], u.vector().blockSurface(new BlockPos(3, 1, 2), Direction.UP), 70, false);
		s.world().showSection(u.select().position(2, 1, 1), Direction.DOWN);
		s.idle(10);
		s.world().createItemOnBeltLike(new BlockPos(2, 1, 1), Direction.UP, objet("airain:airain_ingot"));
		texte(s, T[1], u.vector().topOf(2, 1, 2), 90, true);
		texte(s, T[2], u.vector().topOf(2, 1, 2), 90, true);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- le téléphérique
	public static void telepherique(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.TELEPHERIQUE;
		s.title("telepherique", PonderTextes.TELEPHERIQUE_TITRE);
		s.configureBasePlate(0, 0, 15);
		s.scaleSceneView(0.65f);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		s.world().showSection(u.select().fromTo(1, 1, 2, 1, 2, 2), Direction.DOWN);
		s.world().showSection(u.select().fromTo(13, 1, 2, 13, 2, 2), Direction.DOWN);
		s.idle(15);
		texte(s, T[0], u.vector().topOf(1, 2, 2), 80, false);
		s.world().showSection(u.select().fromTo(7, 1, 2, 7, 5, 2), Direction.DOWN);
		s.idle(15);
		texte(s, T[1], u.vector().topOf(7, 5, 2), 90, true);
		texte(s, T[2], u.vector().topOf(7, 5, 2), 90, true);
		s.world().setKineticSpeed(u.select().fromTo(1, 0, 2, 1, 1, 2), 64);
		texte(s, T[3], u.vector().blockSurface(new BlockPos(1, 1, 2), Direction.WEST), 100, true);
		texte(s, T[4], u.vector().topOf(13, 2, 2), 90, true);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- le monte-charge
	public static void monteCharge(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.MONTE_CHARGE;
		s.title("monte_charge", PonderTextes.MONTE_CHARGE_TITRE);
		s.configureBasePlate(0, 0, 7);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		Selection treuil = u.select().fromTo(3, 1, 2, 5, 1, 2);
		s.world().showSection(treuil, Direction.DOWN);
		s.world().setKineticSpeed(u.select().fromTo(3, 1, 2, 4, 1, 2), 32);
		s.idle(15);
		texte(s, T[0], u.vector().topOf(3, 1, 2), 80, false);
		s.world().showSection(u.select().fromTo(3, 2, 2, 3, 6, 2), Direction.DOWN);
		s.idle(10);
		ElementLink<WorldSectionElement> cabine = s.world().showIndependentSection(u.select().fromTo(3, 2, 3, 3, 3, 3), Direction.NORTH);
		s.idle(15);
		texte(s, T[1], u.vector().blockSurface(new BlockPos(3, 3, 3), Direction.SOUTH), 80, true);
		s.world().showSection(u.select().fromTo(2, 1, 4, 4, 4, 4), Direction.NORTH);
		s.idle(15);
		texte(s, T[2], u.vector().topOf(3, 4, 4), 90, true);
		s.world().moveSection(cabine, u.vector().of(0, 3, 0), 50);
		s.idle(55);
		texte(s, T[3], u.vector().blockSurface(new BlockPos(2, 2, 4), Direction.SOUTH), 100, true);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- pont-levis et passerelle rétractable
	public static void passagesMobiles(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.PASSAGES_MOBILES;
		s.title("passages_mobiles", PonderTextes.PASSAGES_MOBILES_TITRE);
		s.configureBasePlate(0, 0, 9);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		s.world().showSection(u.select().fromTo(1, 1, 1, 1, 1, 5), Direction.DOWN);
		s.world().showSection(u.select().fromTo(7, 1, 1, 7, 1, 5), Direction.DOWN);
		s.idle(10);
		s.world().showSection(u.select().position(2, 1, 1), Direction.DOWN);
		s.world().showSection(u.select().position(2, 1, 5), Direction.DOWN);
		s.idle(15);
		texte(s, T[0], u.vector().topOf(2, 1, 1), 90, false);
		s.world().showSection(u.select().fromTo(3, 1, 1, 6, 1, 1), Direction.WEST);
		s.world().showSection(u.select().fromTo(3, 1, 5, 6, 1, 5), Direction.WEST);
		s.idle(15);
		texte(s, T[1], u.vector().topOf(4, 1, 1), 90, true);
		s.world().setKineticSpeed(u.select().fromTo(2, 0, 1, 2, 1, 1), 32);
		s.world().setKineticSpeed(u.select().fromTo(2, 0, 5, 2, 1, 5), 32);
		texte(s, T[2], u.vector().blockSurface(new BlockPos(2, 1, 5), Direction.NORTH), 100, true);
		texte(s, T[3], u.vector().topOf(6, 1, 5), 80, false);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- la conduite d'air
	public static void conduiteAir(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.CONDUITE_AIR;
		s.title("conduite_air", PonderTextes.CONDUITE_AIR_TITRE);
		s.configureBasePlate(0, 0, 9);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		Selection v = u.select().fromTo(1, 1, 2, 2, 1, 2);
		s.world().showSection(v, Direction.DOWN);
		s.world().setKineticSpeed(v, 64);
		s.idle(10);
		for (int x = 3; x <= 6; x++) { s.world().showSection(u.select().position(x, 1, 2), Direction.DOWN); s.idle(5); }
		texte(s, T[0], u.vector().topOf(4, 1, 2), 80, false);
		s.world().showSection(u.select().position(7, 1, 2), Direction.DOWN);
		s.idle(15);
		texte(s, T[1], u.vector().blockSurface(new BlockPos(7, 1, 2), Direction.EAST), 90, true);
		texte(s, T[2], u.vector().topOf(5, 1, 2), 80, false);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- le rayonnage
	public static void rayonnage(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.RAYONNAGE;
		s.title("rayonnage", PonderTextes.RAYONNAGE_TITRE);
		s.configureBasePlate(0, 0, 7);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		s.world().showSection(u.select().fromTo(2, 1, 2, 4, 1, 2), Direction.DOWN);
		s.idle(8);
		s.world().showSection(u.select().fromTo(2, 2, 2, 4, 2, 2), Direction.DOWN);
		s.idle(15);
		texte(s, T[0], u.vector().topOf(3, 2, 2), 90, false);
		s.world().showSection(u.select().position(5, 1, 2), Direction.WEST);
		s.idle(15);
		texte(s, T[1], u.vector().blockSurface(new BlockPos(5, 1, 2), Direction.EAST), 100, true);
		texte(s, T[2], u.vector().blockSurface(new BlockPos(3, 1, 2), Direction.NORTH), 80, true);
		texte(s, T[3], u.vector().blockSurface(new BlockPos(2, 2, 2), Direction.NORTH), 100, true);
		texte(s, T[4], u.vector().blockSurface(new BlockPos(4, 2, 2), Direction.NORTH), 90, true);
		s.markAsFinished();
	}

	// ---------------------------------------------------------------- le tableau émaillé
	public static void tableauEmaille(SceneBuilder b, SceneBuildingUtil u) {
		CreateSceneBuilder s = new CreateSceneBuilder(b);
		String[] T = PonderTextes.TABLEAU_EMAILLE;
		s.title("tableau_emaille", PonderTextes.TABLEAU_EMAILLE_TITRE);
		s.configureBasePlate(0, 0, 7);
		s.world().showSection(u.select().layer(0), Direction.UP);
		s.idle(10);
		s.world().showSection(u.select().fromTo(1, 1, 3, 5, 3, 3), Direction.DOWN);
		s.idle(10);
		s.world().showSection(u.select().fromTo(2, 2, 2, 4, 3, 2), Direction.SOUTH);
		s.idle(15);
		texte(s, T[0], u.vector().blockSurface(new BlockPos(3, 3, 2), Direction.NORTH), 80, false);
		texte(s, T[1], u.vector().blockSurface(new BlockPos(3, 2, 2), Direction.NORTH), 90, true);
		Selection meca = u.select().fromTo(4, 1, 1, 6, 1, 1);
		s.world().showSection(meca, Direction.DOWN);
		s.world().setKineticSpeed(meca, 64);
		s.idle(10);
		s.world().showSection(u.select().position(5, 2, 1), Direction.DOWN);
		s.idle(15);
		texte(s, T[2], u.vector().topOf(5, 2, 1), 110, true);
		texte(s, T[3], u.vector().blockSurface(new BlockPos(2, 3, 2), Direction.NORTH), 90, true);
		s.markAsFinished();
	}
}
