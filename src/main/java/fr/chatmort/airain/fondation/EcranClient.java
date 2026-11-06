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

	/** Un manuel d'armes. */
	public static void manuel(fr.chatmort.airain.manuel.OuvrirManuel m) { Minecraft.getInstance().setScreen(new fr.chatmort.airain.manuel.ManuelScreen(m)); }

	/** Un thème de l'histoire : coupe la musique en cours, joue sans position. */
	public static void theme(fr.chatmort.airain.chronique.Theme m) {
		var mc = Minecraft.getInstance();
		mc.getMusicManager().stopPlaying();
		mc.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forMusic(
			net.minecraft.sounds.SoundEvent.createVariableRangeEvent(net.minecraft.resources.ResourceLocation.parse(m.son()))));
	}

	public static void armurerie(fr.chatmort.airain.armurerie.OuvrirArmurerie m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.armurerie.ArmurerieScreen(m.echo(), m.vus()));
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

	public static void borne(fr.chatmort.airain.borne.PaquetsBorne.Ouvrir m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.borne.BorneScreen(m));
	}

	public static void registre(OuvrirRegistre m) {
		Minecraft.getInstance().setScreen(new RegistreScreen(m));
	}

	public static void ouvrir(BlockPos pos, String nom, String devise, Apparence a) {
		Minecraft.getInstance().setScreen(new ConfigFondationScreen(pos, nom, devise, a));
	}
}
