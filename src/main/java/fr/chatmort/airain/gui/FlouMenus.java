package fr.chatmort.airain.gui;

import java.nio.file.Files;
import java.nio.file.Path;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.TitleScreen;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.client.event.ScreenEvent;

/** Flou derrière les menus mis à 0 une seule fois, au premier écran titre : le monde reste net derrière le menu pause.
 *  Un repère dans config/ retient que c'est fait ; ensuite le joueur règle le flou comme il veut, le mod n'y touche plus. */
public final class FlouMenus {
	private static boolean vu;

	private FlouMenus() {}

	public static void ecran(ScreenEvent.Init.Post e) {
		if (vu || !(e.getScreen() instanceof TitleScreen)) return;
		vu = true;
		Path repere = FMLPaths.CONFIGDIR.get().resolve("airain-flou-menus.txt");
		if (Files.exists(repere)) return;
		try {
			Minecraft mc = Minecraft.getInstance();
			mc.options.menuBackgroundBlurriness().set(0);
			mc.options.save();
			Files.writeString(repere, "Flou des menus mis à 0 par le mod Airain (une seule fois). Supprimer ce fichier pour le refaire.\n");
		} catch (Exception ignore) {
			// sans accès au dossier config, on ne réessaie pas à chaque lancement de cette session
		}
	}
}
