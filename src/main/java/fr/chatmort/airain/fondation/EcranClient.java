package fr.chatmort.airain.fondation;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;

/** Seule porte vers le code client (chargée uniquement côté client). */
public final class EcranClient {
	private EcranClient() {}

	public static void tourbillon(fr.chatmort.airain.armure.TourbillonPaquet m) { fr.chatmort.airain.armure.TourbillonClient.demarrer(m); }

	public static void codex(fr.chatmort.airain.codex.OuvrirCodex m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.codex.CodexScreen(m));
	}

	public static void chroniques(fr.chatmort.airain.chronique.OuvrirChroniques m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.chronique.ChroniquesScreen(m.donnees()));
	}

	public static void reliure(fr.chatmort.airain.reliure.Paquets.Ouvrir m) {
		fr.chatmort.airain.reliure.LectureClient.ouvrir(m);
	}

	public static void tableau(fr.chatmort.airain.tableau.PaquetsTableau.Ouvrir m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.tableau.TableauScreen(m));
	}

	public static void atlas(fr.chatmort.airain.atlas.OuvrirAtlas m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.atlas.AtlasScreen(m.donnees()));
	}

	public static void registre(OuvrirRegistre m) {
		Minecraft.getInstance().setScreen(new RegistreScreen(m));
	}

	public static void ouvrir(BlockPos pos, String nom, String devise, Apparence a) {
		Minecraft.getInstance().setScreen(new ConfigFondationScreen(pos, nom, devise, a));
	}
}
