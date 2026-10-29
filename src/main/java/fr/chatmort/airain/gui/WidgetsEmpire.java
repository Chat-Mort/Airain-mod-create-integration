package fr.chatmort.airain.gui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

/** Éléments d'interface au style de l'Empire (planche textures/gui/elements.png), partagés par tous les écrans du mod. */
public final class WidgetsEmpire {
	public static final ResourceLocation ELEMENTS = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/elements.png");
	/** Panneau de laiton 310 x 226 (avec vitrine d'aperçu à droite). */
	public static final ResourceLocation PANNEAU = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/etendard.png");
	public static final int BRUN = 0x3A220E, CREME = 0xFFE9B0, GRISE = 0x8A8070;

	private WidgetsEmpire() {}

	/** Creux encastré (champ de saisie, cartouche de valeur). */
	public static void creux(GuiGraphics g, int x, int y, int w, int h) {
		g.fill(x, y, x + w, y + h, 0xFF603E16);
		g.fill(x + 1, y + 1, x + w, y + h, 0xFFE6C068);
		g.fill(x + 1, y + 1, x + w - 1, y + h - 1, 0xFF281A0C);
	}

	/** Bouton rond de laiton avec une flèche. */
	public static final class Fleche extends Button {
		private final boolean droite;

		public Fleche(int x, int y, boolean droite, OnPress action) {
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
	public static final class Onglet extends Button {
		private final boolean actif;

		public Onglet(int x, int y, Component nom, boolean actif, OnPress action) {
			super(x, y, 72, 14, nom, action, DEFAULT_NARRATION);
			this.actif = actif;
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			var font = Minecraft.getInstance().font;
			g.blit(ELEMENTS, getX(), getY(), 0, actif ? 32 : 48, 72, 14, 128, 64);
			int c = actif ? BRUN : isHoveredOrFocused() ? 0x5A3A1A : 0x46301A;
			g.drawString(font, getMessage(), getX() + 36 - font.width(getMessage()) / 2, getY() + 4, c, false);
		}
	}
}
