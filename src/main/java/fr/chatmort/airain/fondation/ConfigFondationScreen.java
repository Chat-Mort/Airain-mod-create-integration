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
		"partition", "fond2", "couleur_motif", "etat", "broderie", "synchro", "hauteur"};
	private static final int HAUTEUR = 19;
	private record Page(String cle, boolean champs, int[] lignes) {}
	private static final Page GENERAL = new Page("general", true, new int[] {0, 18});
	private static final Page GENERAL_GRAND = new Page("general", true, new int[] {0, HAUTEUR, 12});
	private static final Page TOILE = new Page("toile", false, new int[] {1, 13, 14, 2, 3, 15, 4, 16, 17});
	private static final Page MAT = new Page("mat", false, new int[] {5, 6, 7, 18, 8, 9, 10, 11});
	private static final Page TAILLE = new Page("taille", false, new int[] {5, 6, 7, 18, 8, 9, 11});
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
			champ = new EditBox(font, x, y + 14, 190, 20, Component.translatable("airain.fondation.ecran"));
			champ.setMaxLength(32); champ.setValue(nom); champ.setResponder(v -> nom = v);
			addRenderableWidget(champ); setInitialFocus(champ);
			devise = new EditBox(font, x, y + 48, 190, 20, Component.translatable("airain.fondation.devise"));
			devise.setMaxLength(48); devise.setValue(dev); devise.setResponder(v -> dev = v);
			devise.setHint(Component.translatable("airain.fondation.sous_titre"));
			addRenderableWidget(devise);
		}
		int[] lignes = courante().lignes();
		for (int n = 0; n < lignes.length; n++) {
			final int i = lignes[n];
			int ly = y + debutLignes() + n * pas();
			addRenderableWidget(new Fleche(x + 66, ly + 2, false, b -> choix[i] = Math.floorMod(choix[i] - 1, taille(i))));
			addRenderableWidget(new Fleche(x + 174, ly + 2, true, b -> choix[i] = Math.floorMod(choix[i] + 1, taille(i))));
		}
		Page suivante = pages[(page + 1) % pages.length];
		addRenderableWidget(Button.builder(Component.translatable("airain.etendard.page." + suivante.cle()), b -> changerPage())
			.bounds(x + 214, y + 168, 76, 16).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 186, 94, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 96, y + 186, 94, 20).build());
	}

	private void changerPage() {
		page = (page + 1) % pages.length;
		rebuildWidgets();
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
		Component titre = !grand && !murale && courante().champs() ? title
			: Component.translatable("airain.etendard.titre_page." + (murale ? "murale_" : grand ? "grand_" : "") + courante().cle());
		g.drawString(font, titre, x, y, 0xE8C878);
		if (courante().champs()) g.drawString(font, Component.translatable("airain.fondation.devise"), x, y + 38, 0xD0C8B0);
		int[] lignes = courante().lignes();
		for (int n = 0; n < lignes.length; n++) {
			int k = lignes[n];
			int ly = y + debutLignes() + n * pas();
			g.fill(x + 84, ly + 2, x + 172, ly + 18, 0xA0100C08);           // cartouche sombre derrière chaque valeur
			g.fill(x + 84, ly + 2, x + 172, ly + 3, 0xFF6E5020);
			g.fill(x + 84, ly + 17, x + 172, ly + 18, 0xFF6E5020);
			String libelle = murale && k == 9 ? "airain.etendard.embouts" : "airain.etendard." + CLES[k];
			g.drawString(font, Component.translatable(libelle), x, ly + 6, 0xD0C8B0);
			boolean inutile = (k == 10 && choix[0] == 1) || (k == 14 && choix[13] == 0);   // vexillum : une seule bannière ; uni : pas de 2e couleur
			g.drawCenteredString(font, Component.translatable(valeur(k, choix[k])), x + 128, ly + 6, inutile ? 0x8A8070 : 0xFFE9B0);
		}
		// aperçu de la toile
		Apparence a = apparence();
		int bh = 128, bw = 64;
		if (grand) bw = Math.round(128f * Apparence.LARGEURS[a.largeur()] / Apparence.LONGUEURS[a.longueur()]);
		if (murale) bw = Math.round(128f * BanniereMuraleBlock.LARGEURS[a.largeur()] / BanniereMuraleBlock.LONGUEURS[a.longueur()]);
		bw = Math.min(bw, 74);
		int px = x + 252 - bw / 2, py = y + 14;
		g.fill(x + 214, py - 6, x + 290, py + bh + 10, 0x80101010);
		RenderSystem.enableBlend();
		g.blit(TexturesBanniere.de(a), px, py, bw, bh, 0f, 0f, 16, 32, 16, 32);
		if ((grand || murale) && a.avecFranges()) {                          // franges sous la bannière
			int c = 0xFF000000 | Apparence.ORNEMENTS[a.ornement()];
			for (int i = 0; i < bw; i += 2) g.fill(px + i, py + bh, px + i + 1, py + bh + 6, c);
		}
	}

	@Override
	public boolean isPauseScreen() { return false; }

	/** Petite flèche dessinée à la main : lisible quel que soit le pack de ressources. */
	private static final class Fleche extends Button {
		private final boolean droite;

		Fleche(int x, int y, boolean droite, OnPress action) {
			super(x, y, 16, 16, Component.literal(droite ? ">" : "<"), action, DEFAULT_NARRATION);
			this.droite = droite;
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			int x = getX(), y = getY(), w = width, h = height;
			boolean survol = isHoveredOrFocused();
			g.fill(x, y, x + w, y + h, survol ? 0xFFE8BE5A : 0xFF8A6526);         // cadre laiton
			g.fill(x + 1, y + 1, x + w - 1, y + h - 1, survol ? 0xFF3A2A12 : 0xFF1C140A);
			int c = survol ? 0xFFFFF0C0 : 0xFFE8BE5A;
			for (int i = 0; i < 4; i++) {                                        // triangle de 4 colonnes
				int col = droite ? x + 6 + i : x + 9 - i;
				g.fill(col, y + 4 + i, col + 1, y + h - 4 - i, c);
			}
		}
	}
}
