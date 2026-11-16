package fr.chatmort.airain.affichage;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;

/** Côté client : ce que le tableau a reçu de ses liaisons d'affichage (pour le menu et son aperçu). */
final class EmailClientEtat {
	private EmailClientEtat() {}
	static String valeur(BlockPos pos, int i) {
		var mc = Minecraft.getInstance();
		return mc.level != null && mc.level.getBlockEntity(pos) instanceof EmailBlockEntity e ? e.valeur(i) : "";
	}
}
