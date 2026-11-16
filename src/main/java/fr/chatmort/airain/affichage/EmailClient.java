package fr.chatmort.airain.affichage;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;

/** Côté client seulement : ouvre le menu du tableau dont pos est le coin qui garde les réglages. */
public final class EmailClient {
	private EmailClient() {}
	public static void ouvrir(BlockPos pos) {
		var mc = Minecraft.getInstance();
		if (mc.level != null && mc.level.getBlockEntity(pos) instanceof EmailBlockEntity e)
			mc.setScreen(new EmailScreen(pos, e.reglages() != null ? e.reglages().copie() : Reglages.neufs()));
	}
}
