package fr.chatmort.airain.fondation;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;

/** Seule porte vers le code client (chargée uniquement côté client). */
public final class EcranClient {
	private EcranClient() {}

	public static void ouvrir(BlockPos pos, String nom) {
		Minecraft.getInstance().setScreen(new NomFondationScreen(pos, nom));
	}
}
