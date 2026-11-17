package fr.chatmort.airain.gui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.inventory.CreativeModeInventoryScreen;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;

/**
 * Nouvelle interface « Airain-Interface-HD » (resource pack séparé, ardoise et airain en 3x).
 * Le pack porte un repère (assets/airain/interface_hd.json) : s'il est actif, les textes sombres des écrans passent en airain
 * et les boutons à chaîne gardent leur texte entre les deux pignons. Sans le pack, rien ne change.
 */
public final class InterfaceHD {
	private static final ResourceLocation REPERE = ResourceLocation.fromNamespaceAndPath("airain", "interface_hd.json");
	/** Airain neuf (titres) et airain un ton plus sombre (libellés secondaires). */
	public static final int AIRAIN = 0xF3D694, AIRAIN_SOMBRE = 0xE1BA6E, ARDOISE_TEXTE = 0x9AA0AA;
	/** Marge du texte des boutons larges : le pignon occupe les 17 premiers et derniers pixels. */
	public static final int MARGE_PIGNONS = 17;
	private static boolean actif;

	private InterfaceHD() {}

	public static boolean actif() { return actif; }

	/** Relu à chaque rechargement des ressources (changement de pack, F3+T). */
	public static void recharger(ResourceManager rm) { actif = rm.getResource(REPERE).isPresent(); }

	/** Couleur d'un texte du mod : l'ancienne (brune, pour le laiton) sans le pack, l'airain sur l'ardoise avec. */
	public static int texte(int ancienne) { return actif ? AIRAIN : ancienne; }

	/** Texte gris foncé vanilla (0x404040) d'un écran de conteneur : illisible sur l'ardoise, il passe en airain. */
	public static boolean texteSurArdoise(int couleur) {
		if (!actif || (couleur & 0xFFFFFF) != 0x404040) return false;
		var ecran = Minecraft.getInstance().screen;
		// l'inventaire créatif garde ses onglets vanilla (gris clair) : on n'y touche pas
		return ecran instanceof AbstractContainerScreen<?> && !(ecran instanceof CreativeModeInventoryScreen);
	}
}
