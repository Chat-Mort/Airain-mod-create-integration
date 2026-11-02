package fr.chatmort.airain.ingenieur;

/** Seule porte vers l'écran (chargée côté client uniquement). */
final class Ouvrir {
	private Ouvrir() {}
	static void livre() { net.minecraft.client.Minecraft.getInstance().setScreen(new LivreIngenieurScreen()); }
}
