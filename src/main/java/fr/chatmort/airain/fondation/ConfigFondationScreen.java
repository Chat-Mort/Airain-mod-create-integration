package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Écran de l'étendard : nom de la base, devise, puis style, couleurs, motif et forme de la bannière, avec un aperçu.
 * Le grand étendard a une seconde page (taille, vent, franges, fleuron, bannière double, lanternes, titre).
 */
public class ConfigFondationScreen extends Screen {
	private static final String[] CLES = {"style", "fond", "ornement", "motif", "forme",
		"longueur", "largeur", "vent", "franges", "fleuron", "double", "lanternes", "titre", "hauteur"};
	/** Ordre des lignes : page bannière, page étendard (la hauteur du mât n'est pas dans l'apparence, d'où l'indice 13). */
	private static final int[][] ORDRE = {{0, 1, 2, 3, 4}, {13, 5, 6, 7, 8, 9, 10, 11, 12}};
	private static final int PAGE1 = 5;
	private final BlockPos pos;
	private String nom, dev;
	private final int[] choix;
	private EditBox champ, devise;
	private boolean grand;
	private int page;

	public ConfigFondationScreen(BlockPos pos, String nom, String dev, Apparence a) {
		super(Component.translatable("airain.fondation.ecran"));
		this.pos = pos; this.nom = nom; this.dev = dev;
		this.choix = java.util.Arrays.copyOf(a.valeurs(), 14);
		var mc = net.minecraft.client.Minecraft.getInstance();
		if (mc.level != null && mc.level.getBlockEntity(pos) instanceof FondationBlockEntity f)
			choix[13] = f.hauteur() - GrandEtendardBlock.MAT_MIN;
	}

	private Apparence apparence() {
		return Apparence.depuis(choix);
	}

	/** Réglages affichés sur la page courante (indices dans CLES) et leur première ligne. */
	private int[] ordre() { return ORDRE[page]; }
	private int pas() { return page == 0 ? 21 : 19; }
	private static int taille(int i) { return i == 13 ? GrandEtendardBlock.MAT_MAX - GrandEtendardBlock.MAT_MIN + 1 : Apparence.TAILLES[i]; }
	private int debutLignes() { return page == 0 ? 76 : 14; }

	private int haut() {
		return height / 2 - 108;
	}

	@Override
	protected void init() {
		grand = minecraft != null && minecraft.level != null && minecraft.level.getBlockState(pos).getBlock() instanceof GrandEtendardBlock;
		int x = width / 2 - 150, y = haut();
		if (page == 0) {
			champ = new EditBox(font, x, y + 14, 190, 20, Component.translatable("airain.fondation.ecran"));
			champ.setMaxLength(32); champ.setValue(nom); champ.setResponder(v -> nom = v);
			addRenderableWidget(champ); setInitialFocus(champ);
			devise = new EditBox(font, x, y + 48, 190, 20, Component.translatable("airain.fondation.devise"));
			devise.setMaxLength(48); devise.setValue(dev); devise.setResponder(v -> dev = v);
			devise.setHint(Component.translatable("airain.fondation.sous_titre"));
			addRenderableWidget(devise);
		} else {
			champ = null; devise = null;
		}
		for (int n = 0; n < ordre().length; n++) {
			final int i = ordre()[n];
			int ly = y + debutLignes() + n * pas();
			addRenderableWidget(new Fleche(x + 66, ly + 2, false, b -> choix[i] = Math.floorMod(choix[i] - 1, taille(i))));
			addRenderableWidget(new Fleche(x + 174, ly + 2, true, b -> choix[i] = Math.floorMod(choix[i] + 1, taille(i))));
		}
		int yb = y + 186;
		if (grand) {   // onglets : bannière / étendard
			addRenderableWidget(Button.builder(Component.translatable("airain.etendard.page." + (page == 0 ? 1 : 0)), b -> changerPage())
				.bounds(x + 214, y + 168, 76, 16).build());
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, yb, 94, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 96, yb, 94, 20).build());
	}

	private void changerPage() {
		page = 1 - page;
		rebuildWidgets();
	}

	private void valider() {
		PacketDistributor.sendToServer(new ConfigurerFondation(pos, nom.trim(), dev.trim(), apparence().pack(), choix[13] + GrandEtendardBlock.MAT_MIN));
		onClose();
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if ((key == 257 || key == 335) && champ != null && (champ.isFocused() || devise.isFocused())) { valider(); return true; }
		return super.keyPressed(key, scan, mods);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = width / 2 - 150, y = haut();
		Component titre = grand ? Component.translatable("airain.etendard.titre_page." + page) : title;
		g.drawString(font, titre, x, y, 0xE8C878);
		if (page == 0) g.drawString(font, Component.translatable("airain.fondation.devise"), x, y + 38, 0xD0C8B0);
		for (int n = 0; n < ordre().length; n++) {
			int k = ordre()[n];
			int ly = y + debutLignes() + n * pas();
			g.fill(x + 84, ly + 2, x + 172, ly + 18, 0xA0100C08);           // cartouche sombre derrière chaque valeur
			g.fill(x + 84, ly + 2, x + 172, ly + 3, 0xFF6E5020);
			g.fill(x + 84, ly + 17, x + 172, ly + 18, 0xFF6E5020);
			g.drawString(font, Component.translatable("airain.etendard." + CLES[k]), x, ly + 6, 0xD0C8B0);
			boolean inutile = k == 10 && choix[0] == 1;                       // le vexillum n'a qu'une bannière
			g.drawCenteredString(font, Component.translatable("airain.etendard." + CLES[k] + "." + choix[k]), x + 128, ly + 6, inutile ? 0x8A8070 : 0xFFE9B0);
		}
		// aperçu de la bannière (calques teintés)
		Apparence a = apparence();
		int bh = 128, bw = grand ? Math.round(128f * Apparence.LARGEURS[a.largeur()] / Apparence.LONGUEURS[a.longueur()]) : 64;
		int px = x + 220 + (64 - bw) / 2, py = y + 14;
		g.fill(x + 214, py - 6, x + 290, py + bh + 10, 0x80101010);
		RenderSystem.enableBlend();
		dessiner(g, a.texFond(), Apparence.FONDS[a.fond()], px, py, bw, bh);
		if (a.texMotif() != null) dessiner(g, a.texMotif(), Apparence.ORNEMENTS[a.ornement()], px, py, bw, bh);
		dessiner(g, a.texOrnement(), Apparence.ORNEMENTS[a.ornement()], px, py, bw, bh);
		RenderSystem.setShaderColor(1, 1, 1, 1);
		if (grand && a.avecFranges()) {                                       // franges sous la bannière
			int c = 0xFF000000 | Apparence.ORNEMENTS[a.ornement()];
			for (int i = 0; i < bw; i += 2) g.fill(px + i, py + bh, px + i + 1, py + bh + 6, c);
		}
	}

	private static void dessiner(GuiGraphics g, ResourceLocation tex, int c, int x, int y, int w, int h) {
		RenderSystem.setShaderColor((c >> 16 & 255) / 255f, (c >> 8 & 255) / 255f, (c & 255) / 255f, 1f);
		g.blit(tex, x, y, w, h, 0f, 0f, 16, 32, 16, 32);
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
