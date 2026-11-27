package fr.chatmort.airain.fonderie;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.player.Inventory;

/** 1.71.1 : écran de l'armoire impériale (style des écrans du mod), boutons d'échange sous les colonnes. */
public class ArmoireScreen extends AbstractContainerScreen<ArmoireMenu> {
	private static final ResourceLocation FOND = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/imperial_wardrobe.png");
	private static final int OR = 0xFFE1BA6E, BLANC = 0xFFEBE6DC;

	public ArmoireScreen(ArmoireMenu m, Inventory inv, Component t) {
		super(m, inv, t);
		imageWidth = 176; imageHeight = 206;
		titleLabelX = 8; titleLabelY = 6;
		inventoryLabelX = 8; inventoryLabelY = 111;
	}

	/** Colonne du bouton survolé, ou -1. */
	private int bouton(double mx, double my) {
		for (int c = 0; c < 9; c++) {
			int x = leftPos + 8 + c * 18, y = topPos + 91;
			if (mx >= x && mx < x + 16 && my >= y && my < y + 10) return c;
		}
		return -1;
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		g.blit(FOND, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
		int b = bouton(mx, my);
		for (int c = 0; c < 9; c++) g.blit(FOND, leftPos + 8 + c * 18, topPos + 91, 180, c == b ? 12 : 0, 16, 10, 256, 256);
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		g.drawString(font, title, titleLabelX, titleLabelY, OR, false);
		g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, BLANC, false);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
		if (bouton(mx, my) >= 0) g.renderTooltip(font, Component.translatable("airain.armoire.echanger"), mx, my);
	}

	@Override
	public boolean mouseClicked(double mx, double my, int bt) {
		int c = bouton(mx, my);
		if (c >= 0 && bt == 0) {
			Minecraft mc = Minecraft.getInstance();
			if (mc.gameMode != null) mc.gameMode.handleInventoryButtonClick(menu.containerId, c);
			mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1f));
			return true;
		}
		return super.mouseClicked(mx, my, bt);
	}
}
