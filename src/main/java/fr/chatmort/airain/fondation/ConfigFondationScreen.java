package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.systems.RenderSystem;
import fr.chatmort.airain.gui.InterfaceHD;
import fr.chatmort.airain.gui.PanneauHD;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Écran des étendards et de la bannière murale, en pages :
 * « Général » (nom, devise, style ; hauteur et titre pour le grand), « Toile » (couleurs, partition, motif, forme, usure),
 * puis « Mât » pour le grand étendard ou « Taille » pour la bannière murale. Aperçu de la toile à droite.
 */
public class ConfigFondationScreen extends Screen {
	private static final String[] CLES = {"style", "fond", "ornement", "motif", "forme",
		"longueur", "largeur", "vent", "franges", "fleuron", "double", "lanternes", "titre",
		"partition", "fond2", "couleur_motif", "etat", "broderie", "synchro", "presence", "cote", "hauteur"};
	private static final int HAUTEUR = 21;
	private static final int BRUN = 0x3A220E, CREME = 0xFFE9B0;
	private static final net.minecraft.resources.ResourceLocation FOND = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/standard.png");
	static final net.minecraft.resources.ResourceLocation ELEMENTS = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/widgets.png");
	private record Page(String cle, boolean champs, int[] lignes) {}
	private static final Page GENERAL = new Page("general", true, new int[] {0, 18});
	private static final Page GENERAL_GRAND = new Page("general", true, new int[] {0, HAUTEUR, 12});
	private static final Page TOILE = new Page("toile", false, new int[] {1, 13, 14, 2, 3, 15, 4, 16, 17});
	private static final Page MAT = new Page("mat", false, new int[] {5, 6, 7, 18, 19, 8, 9, 10, 11});
	private static final Page TAILLE = new Page("taille", false, new int[] {5, 6, 7, 18, 19, 8, 9, 11});
	// interface HD : 5 rangées au plus par onglet (Général, Toile, Motif, Mât ou Taille, Garnitures)
	private static final Page HD_GENERAL = new Page("general", true, new int[] {0, 18});
	private static final Page HD_GENERAL_GRAND = new Page("general", true, new int[] {0, HAUTEUR, 12});
	private static final Page HD_TOILE = new Page("toile", false, new int[] {1, 13, 14, 4, 16});
	private static final Page HD_MOTIF = new Page("motif", false, new int[] {3, 15, 2, 17});
	private static final Page HD_MAT = new Page("mat", false, new int[] {5, 6, 7, 18, 19});
	private static final Page HD_TAILLE = new Page("taille", false, new int[] {5, 6, 7, 18, 19});
	private static final Page HD_GARNITURES = new Page("garnitures", false, new int[] {8, 9, 10, 11});
	private static final Page HD_GARNITURES_MUR = new Page("garnitures", false, new int[] {8, 9, 11});
	/** Interface HD : flèche gauche, cartouche (x, largeur), flèche droite (par rapport à x). */
	private static final int HD_FG = 72, HD_CX = 90, HD_CW = 87, HD_FD = 179;
	private final BlockPos pos;
	private String nom, dev;
	private final int[] choix;
	private EditBox champ, devise;
	private boolean grand, murale;
	private Page[] pages = {GENERAL, TOILE};
	private int page;

	public ConfigFondationScreen(BlockPos pos, String nom, String dev, Apparence a) {
		super(Component.translatable("airain.fondation.ecran"));
		this.pos = pos; this.nom = nom; this.dev = dev;
		this.choix = java.util.Arrays.copyOf(a.valeurs(), HAUTEUR + 1);
		var mc = net.minecraft.client.Minecraft.getInstance();
		if (mc.level != null && mc.level.getBlockEntity(pos) instanceof FondationBlockEntity f)
			choix[HAUTEUR] = f.hauteur() - GrandEtendardBlock.MAT_MIN;
	}

	private Apparence apparence() {
		return Apparence.depuis(choix);
	}

	private Page courante() { return pages[page]; }
	private int pas() { return InterfaceHD.actif() ? PanneauHD.PAS : courante().champs() ? 21 : courante().lignes().length > 8 ? 18 : 19; }
	private int debutLignes() {
		if (InterfaceHD.actif()) return courante().champs() ? 82 : PanneauHD.Y_LIGNES;   // sous les deux champs et la rainure
		return courante().champs() ? 76 : 14;
	}
	private static int taille(int i) { return i == HAUTEUR ? GrandEtendardBlock.MAT_MAX - GrandEtendardBlock.MAT_MIN + 1 : Apparence.TAILLES[i]; }

	private int haut() {
		return height / 2 - 108;
	}

	@Override
	protected void init() {
		if (minecraft != null && minecraft.level != null) {
			var b = minecraft.level.getBlockState(pos).getBlock();
			grand = b instanceof GrandEtendardBlock;
			murale = b instanceof BanniereMuraleBlock;
		}
		if (InterfaceHD.actif())
			pages = murale ? new Page[] {HD_TOILE, HD_MOTIF, HD_TAILLE, HD_GARNITURES_MUR}
				: grand ? new Page[] {HD_GENERAL_GRAND, HD_TOILE, HD_MOTIF, HD_MAT, HD_GARNITURES} : new Page[] {HD_GENERAL, HD_TOILE, HD_MOTIF};
		else pages = murale ? new Page[] {TOILE, TAILLE} : grand ? new Page[] {GENERAL_GRAND, TOILE, MAT} : new Page[] {GENERAL, TOILE};
		page = Math.min(page, pages.length - 1);
		if (InterfaceHD.actif()) { initHD(); return; }
		int x = width / 2 - 150, y = haut();
		champ = null; devise = null;
		if (courante().champs()) {
			champ = new EditBox(font, x + 5, y + 20, 182, 10, Component.translatable("airain.fondation.ecran"));
			champ.setBordered(false); champ.setTextColor(CREME);
			champ.setMaxLength(32); champ.setValue(nom); champ.setResponder(v -> nom = v);
			addRenderableWidget(champ); setInitialFocus(champ);
			devise = new EditBox(font, x + 5, y + 54, 182, 10, Component.translatable("airain.fondation.devise"));
			devise.setBordered(false); devise.setTextColor(CREME);
			devise.setMaxLength(48); devise.setValue(dev); devise.setResponder(v -> dev = v);
			devise.setHint(Component.translatable("airain.fondation.sous_titre"));
			addRenderableWidget(devise);
		}
		int[] lignes = courante().lignes();
		for (int n = 0; n < lignes.length; n++) {
			final int i = lignes[n];
			int ly = y + debutLignes() + n * pas();
			addRenderableWidget(new fr.chatmort.airain.gui.WidgetsEmpire.Fleche(x + 78, ly + 2, false, b -> changer(i, -1)));
			addRenderableWidget(new fr.chatmort.airain.gui.WidgetsEmpire.Fleche(x + 186, ly + 2, true, b -> changer(i, 1)));
		}
		for (int k = 0; k < pages.length; k++) {                            // onglets de laiton au-dessus du panneau
			final int cible = k;
			addRenderableWidget(new fr.chatmort.airain.gui.WidgetsEmpire.Onglet(x + 4 + k * 74, y - 23, Component.translatable("airain.etendard.onglet." + pages[k].cle()),
				k == page, b -> { page = cible; rebuildWidgets(); }));
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 186, 94, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 96, y + 186, 94, 20).build());
	}

	/** Interface HD : champs creux Nom et Devise, onglets raccordés au bac, rangées au pas de 21. */
	private void initHD() {
		int x = width / 2 - 150, y = haut();
		champ = null; devise = null;
		if (courante().champs()) {
			champ = new EditBox(font, x + 56, y + 32, 136, 10, Component.translatable("airain.fondation.ecran"));
			champ.setBordered(false); champ.setTextColor(0xE8E2D4);
			champ.setMaxLength(32); champ.setValue(nom); champ.setResponder(v -> nom = v);
			addRenderableWidget(champ); setInitialFocus(champ);
			devise = new EditBox(font, x + 56, y + 53, 136, 10, Component.translatable("airain.fondation.devise"));
			devise.setBordered(false); devise.setTextColor(0xE8E2D4);
			devise.setMaxLength(48); devise.setValue(dev); devise.setResponder(v -> dev = v);
			devise.setHint(Component.translatable("airain.fondation.sous_titre"));
			addRenderableWidget(devise);
		}
		int[] lignes = courante().lignes();
		for (int n = 0; n < lignes.length; n++) {
			final int i = lignes[n];
			int ly = y + debutLignes() + n * pas();
			addRenderableWidget(new fr.chatmort.airain.gui.WidgetsEmpire.Fleche(x + HD_FG, ly, false, b -> changer(i, -1)));
			addRenderableWidget(new fr.chatmort.airain.gui.WidgetsEmpire.Fleche(x + HD_FD, ly, true, b -> changer(i, 1)));
		}
		Component[] noms = new Component[pages.length];
		for (int k = 0; k < pages.length; k++) noms[k] = Component.translatable("airain.etendard.onglet." + pages[k].cle());
		int[] xs = PanneauHD.placeOnglets(font, noms, x);
		// onglets de droite à gauche (comme un classeur), l'actif en dernier pour passer devant
		for (int k = pages.length - 1; k >= -1; k--) {
			int c = k < 0 ? page : k;
			if (k >= 0 && k == page) continue;
			final int cible = c;
			addRenderableWidget(new fr.chatmort.airain.gui.WidgetsEmpire.Onglet(xs[c], y + PanneauHD.Y_ONGLETS, xs[pages.length + c], 16, noms[c],
				c == page, b -> { page = cible; rebuildWidgets(); }));
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 186, PanneauHD.BOUTON, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + PanneauHD.ECART_BOUTONS, y + 186, PanneauHD.BOUTON, 20).build());
	}

	/** La ligne « bannière » réunit simple à gauche, simple à droite et double. */
	private int banniere() { return choix[10] == 1 ? 2 : choix[20]; }
	private void changer(int i, int d) {
		if (i == 10) {
			int b = Math.floorMod(banniere() + d, 3);
			choix[10] = b == 2 ? 1 : 0;
			choix[20] = b == 1 ? 1 : 0;
		} else choix[i] = Math.floorMod(choix[i] + d, taille(i));
	}

	/** Panneau de laiton, champs de saisie encastrés. */
	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		int x = width / 2 - 150, y = haut();
		if (InterfaceHD.actif()) {
			PanneauHD.fond(g, x, y);
			if (courante().champs()) {
				PanneauHD.champ(g, x + 52, y + 28, 144, champ != null && champ.isFocused());
				PanneauHD.champ(g, x + 52, y + 49, 144, devise != null && devise.isFocused());
				PanneauHD.rainure(g, x + 3, x + 197, y + 73);
			}
			return;
		}
		g.blit(FOND, x - 10, y - 10, 0, 0, 310, 226, 512, 256);
		if (courante().champs()) {
			creux(g, x, y + 14, 190, 20);
			creux(g, x, y + 48, 190, 20);
		}
	}

	private static void creux(GuiGraphics g, int x, int y, int w, int h) {
		g.fill(x, y, x + w, y + h, 0xFF603E16);
		g.fill(x + 1, y + 1, x + w, y + h, 0xFFE6C068);
		g.fill(x + 1, y + 1, x + w - 1, y + h - 1, 0xFF281A0C);
	}

	private void valider() {
		Apparence a = apparence();
		PacketDistributor.sendToServer(new ConfigurerFondation(pos, nom.trim(), dev.trim(), a.pack(), choix[HAUTEUR] + GrandEtendardBlock.MAT_MIN, a.packExt()));
		onClose();
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if ((key == 257 || key == 335) && champ != null && (champ.isFocused() || devise.isFocused())) { valider(); return true; }
		return super.keyPressed(key, scan, mods);
	}

	/** Libellé d'une valeur : certaines lignes reprennent les listes de couleurs, la bannière murale a ses propres tailles. */
	private String valeur(int k, int v) {
		if (k == 14) return "airain.etendard.fond." + v;
		if (k == 15) return v == 0 ? "airain.etendard.couleur_motif.0" : v <= 4 ? "airain.etendard.ornement." + (v - 1) : "airain.etendard.fond." + (v - 5);
		if (murale && (k == 5 || k == 6)) return "airain.etendard." + CLES[k] + "_mur." + v;
		return "airain.etendard." + CLES[k] + "." + v;
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = width / 2 - 150, y = haut();
		Component titre = minecraft != null && minecraft.level != null ? minecraft.level.getBlockState(pos).getBlock().getName() : title;
		if (InterfaceHD.actif()) { renderHD(g, x, y, titre); apercu(g, x, y); PanneauHD.reflets(g, x, y); return; }
		g.drawString(font, titre, x + 2, y - 4, BRUN, false);
		if (courante().champs()) g.drawString(font, Component.translatable("airain.fondation.devise"), x, y + 38, BRUN, false);
		int[] lignes = courante().lignes();
		for (int n = 0; n < lignes.length; n++) {
			int k = lignes[n];
			int ly = y + debutLignes() + n * pas();
			creux(g, x + 96, ly + 2, 88, 16);                                 // cartouche encastré pour la valeur
			String libelle = murale && k == 9 ? "airain.etendard.embouts" : "airain.etendard." + CLES[k];
			g.drawString(font, Component.translatable(libelle), x, ly + 6, BRUN, false);
			boolean inutile = (k == 10 && choix[0] == 1) || (k == 14 && choix[13] == 0);   // vexillum : une seule bannière ; uni : pas de 2e couleur
			g.drawCenteredString(font, Component.translatable(k == 10 ? "airain.etendard.banniere." + banniere() : valeur(k, choix[k])), x + 140, ly + 6, inutile ? 0x8A8070 : CREME);
		}
		apercu(g, x, y);
	}

	/** Interface HD : titre sur l'ardoise, libellés à points de conduite, valeurs en cartouches (grises si sans effet). */
	private void renderHD(GuiGraphics g, int x, int y, Component titre) {
		g.drawString(font, titre, x + 2, y - 4, InterfaceHD.AIRAIN, true);
		if (courante().champs()) {
			PanneauHD.libelle(g, font, x + 4, y + 28, x + 4, Component.translatable("airain.fondation.nom"));
			PanneauHD.libelle(g, font, x + 4, y + 49, x + 4, Component.translatable("airain.fondation.devise_courte"));
		}
		int[] lignes = courante().lignes();
		// gravure du bas du bac, sous la dernière rangée (cartouche de 16 px de haut) quand l'onglet laisse la place
		PanneauHD.garniture(g, x, y, y + debutLignes() + (lignes.length - 1) * pas() + 16);
		for (int n = 0; n < lignes.length; n++) {
			int k = lignes[n];
			int ly = y + debutLignes() + n * pas();
			String libelle = murale && k == 9 ? "airain.etendard.embouts" : "airain.etendard." + CLES[k];
			PanneauHD.libelle(g, font, x + 4, ly, x + HD_FG, Component.translatable(libelle));
			boolean inutile = (k == 10 && choix[0] == 1) || (k == 14 && choix[13] == 0);
			PanneauHD.cartouche(g, font, x + HD_CX, ly, HD_CW, Component.translatable(k == 10 ? "airain.etendard.banniere." + banniere() : valeur(k, choix[k])), inutile);
		}
	}

	/** Aperçu de la toile dans la vitrine. */
	private void apercu(GuiGraphics g, int x, int y) {
		Apparence a = apparence();
		int bh = 128, bw = 64;
		if (grand) bw = Math.round(128f * Apparence.LARGEURS[a.largeur()] / Apparence.LONGUEURS[a.longueur()]);
		if (murale) bw = Math.round(128f * BanniereMuraleBlock.LARGEURS[a.largeur()] / BanniereMuraleBlock.LONGUEURS[a.longueur()]);
		bw = Math.min(bw, 74);
		int px = x + 252 - bw / 2, py = y + 14;
		RenderSystem.enableBlend();
		g.blit(TexturesBanniere.de(a), px, py, bw, bh, 0f, 0f, 16, 32, 16, 32);
		if ((grand || murale) && a.avecFranges()) {                          // franges sous la bannière
			int c = 0xFF000000 | Apparence.ORNEMENTS[a.ornement()];
			for (int i = 0; i < bw; i += 2) g.fill(px + i, py + bh, px + i + 1, py + bh + 6, c);
		}
	}

	@Override
	public boolean isPauseScreen() { return false; }

}
