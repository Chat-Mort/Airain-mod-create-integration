package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.systems.RenderSystem;
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
		"partition", "fond2", "couleur_motif", "etat", "broderie", "synchro", "presence", "hauteur"};
	private static final int HAUTEUR = 20;
	private static final int BRUN = 0x3A220E, CREME = 0xFFE9B0;
	private static final net.minecraft.resources.ResourceLocation FOND = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/etendard.png");
	static final net.minecraft.resources.ResourceLocation ELEMENTS = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/elements.png");
	private record Page(String cle, boolean champs, int[] lignes) {}
	private static final Page GENERAL = new Page("general", true, new int[] {0, 18});
	private static final Page GENERAL_GRAND = new Page("general", true, new int[] {0, HAUTEUR, 12});
	private static final Page TOILE = new Page("toile", false, new int[] {1, 13, 14, 2, 3, 15, 4, 16, 17});
	private static final Page MAT = new Page("mat", false, new int[] {5, 6, 7, 18, 19, 8, 9, 10, 11});
	private static final Page TAILLE = new Page("taille", false, new int[] {5, 6, 7, 18, 19, 8, 9, 11});
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
	private int pas() { return courante().champs() ? 21 : courante().lignes().length > 8 ? 18 : 19; }
	private int debutLignes() { return courante().champs() ? 76 : 14; }
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
		pages = murale ? new Page[] {TOILE, TAILLE} : grand ? new Page[] {GENERAL_GRAND, TOILE, MAT} : new Page[] {GENERAL, TOILE};
		page = Math.min(page, pages.length - 1);
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
			addRenderableWidget(new Fleche(x + 78, ly + 2, false, b -> choix[i] = Math.floorMod(choix[i] - 1, taille(i))));
			addRenderableWidget(new Fleche(x + 186, ly + 2, true, b -> choix[i] = Math.floorMod(choix[i] + 1, taille(i))));
		}
		for (int k = 0; k < pages.length; k++) {                            // onglets de laiton au-dessus du panneau
			final int cible = k;
			addRenderableWidget(new Onglet(x + 4 + k * 74, y - 23, Component.translatable("airain.etendard.onglet." + pages[k].cle()),
				k == page, b -> { page = cible; rebuildWidgets(); }));
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 186, 94, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 96, y + 186, 94, 20).build());
	}

	/** Panneau de laiton, champs de saisie encastrés. */
	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		int x = width / 2 - 150, y = haut();
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
			g.drawCenteredString(font, Component.translatable(valeur(k, choix[k])), x + 140, ly + 6, inutile ? 0x8A8070 : CREME);
		}
		// aperçu de la toile
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

	/** Bouton rond de laiton avec une flèche (planche elements.png). */
	private static final class Fleche extends Button {
		private final boolean droite;

		Fleche(int x, int y, boolean droite, OnPress action) {
			super(x, y, 16, 16, Component.literal(droite ? ">" : "<"), action, DEFAULT_NARRATION);
			this.droite = droite;
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			int u = (droite ? 16 : 0) + (isHoveredOrFocused() ? 32 : 0);
			g.blit(ELEMENTS, getX(), getY(), u, 16, 16, 16, 128, 64);
		}
	}

	/** Onglet de laiton au-dessus du panneau ; l'onglet actif est plus clair. */
	private final class Onglet extends Button {
		private final boolean actif;

		Onglet(int x, int y, Component nom, boolean actif, OnPress action) {
			super(x, y, 72, 14, nom, action, DEFAULT_NARRATION);
			this.actif = actif;
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			g.blit(ELEMENTS, getX(), getY(), 0, actif ? 32 : 48, 72, 14, 128, 64);
			int c = actif ? BRUN : isHoveredOrFocused() ? 0x5A3A1A : 0x46301A;
			g.drawString(font, getMessage(), getX() + 36 - font.width(getMessage()) / 2, getY() + 4, c, false);
		}
	}
}
