package fr.chatmort.airain.fonderie;

import net.minecraft.world.InteractionHand;
import net.neoforged.neoforge.network.PacketDistributor;

/** 1.69 : côté client du marteau-pilon (la touche Ctrl n'est connue que du jeu du joueur). */
final class MarteauClient {
	private MarteauClient() {}
	static boolean ctrl() { return net.minecraft.client.gui.screens.Screen.hasControlDown(); }
	static void basculer(InteractionHand main) { PacketDistributor.sendToServer(new MarteauPilon.Mode(main == InteractionHand.MAIN_HAND)); }
}
