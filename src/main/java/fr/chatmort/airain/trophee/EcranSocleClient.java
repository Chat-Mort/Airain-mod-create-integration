package fr.chatmort.airain.trophee;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;

/** Seule porte vers l'écran du piédestal (chargée uniquement côté client). */
public final class EcranSocleClient {
	private EcranSocleClient() {}

	public static void ouvrir(BlockPos pos, SocleApparence a, String plaque) {
		Minecraft.getInstance().setScreen(new SocleScreen(pos, a, plaque));
	}
}
