package fr.chatmort.airain.fondation;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;

/** Seule porte vers le code client (chargée uniquement côté client). */
public final class EcranClient {
	private EcranClient() {}

	public static void codex(fr.chatmort.airain.codex.OuvrirCodex m) {
		Minecraft.getInstance().setScreen(new fr.chatmort.airain.codex.CodexScreen(m));
	}

	public static void registre(OuvrirRegistre m) {
		Minecraft.getInstance().setScreen(new RegistreScreen(m));
	}

	public static void ouvrir(BlockPos pos, String nom, String devise, Apparence a) {
		Minecraft.getInstance().setScreen(new ConfigFondationScreen(pos, nom, devise, a));
	}
}
