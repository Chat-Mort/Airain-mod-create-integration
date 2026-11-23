package fr.chatmort.airain.gui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
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
	/** Marge la plus courte : le texte peut mordre sur la couronne dentée, jamais sur le trou du pignon (qui finit à 14 px). */
	public static final int MARGE_PIGNONS_MIN = 14;
	private static boolean actif;
	/** Écrans de Create redessinés en carter (lot 5b) : on en ajoute un ici quand sa texture HD est livrée. */
	private static final java.util.Set<String> ECRANS_CREATE_HD = java.util.Set.of("DisplayLinkScreen", "ThresholdSwitchScreen", "ElevatorContactScreen", "SequencedGearshiftScreen", "FactoryPanelScreen");

	private InterfaceHD() {}

	public static boolean actif() { return actif; }

	/** Relu à chaque rechargement des ressources (changement de pack, F3+T). */
	public static void recharger(ResourceManager rm) { actif = rm.getResource(REPERE).isPresent(); }

	/** Couleur d'un texte du mod : l'ancienne (brune, pour le laiton) sans le pack, l'airain sur l'ardoise avec. */
	public static int texte(int ancienne) { return actif ? AIRAIN : ancienne; }

	/**
	 * Titres sombres d'un écran de conteneur, illisibles sur l'ardoise : ils passent en airain.
	 * Gris vanilla (0x404040), gris et brun-rouge de Create (0x505050, 0x592424), brun du gardien de stock (0x714A40).
	 */
	public static boolean texteSurArdoise(int couleur) {
		int c = couleur & 0xFFFFFF;
		// écrans de Create passés au carter HD (lot 5b) : leur titre se pose sur une plaque sombre, il passe en airain,
		// quelle que soit sa teinte d'origine (brun-rouge, gris, ardoise, violet)
		var e = Minecraft.getInstance().screen;
		if (actif && e != null && ECRANS_CREATE_HD.contains(e.getClass().getSimpleName())
			&& (c == 0x592424 || c == 0x505050 || c == 0x3D3C48 || c == 0x2F3738 || c == 0x54214F)) return true;
		if (!actif || (c != 0x404040 && c != 0x505050 && c != 0x592424 && c != 0x714A40)) return false;
		var ecran = Minecraft.getInstance().screen;
		// l'inventaire créatif a désormais son fond d'ardoise : son titre passe aussi en airain
		return ecran instanceof AbstractContainerScreen<?>;
	}
}
