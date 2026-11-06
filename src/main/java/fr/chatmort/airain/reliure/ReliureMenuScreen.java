package fr.chatmort.airain.reliure;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

/** Ranger les livres : un panneau de cuir, 9 cases de livres, puis l'inventaire. */
public class ReliureMenuScreen extends AbstractContainerScreen<ReliureMenu> {
	public ReliureMenuScreen(ReliureMenu m, Inventory inv, Component titre) {
		super(m, inv, titre);
		imageWidth = 176; imageHeight = 134;
		inventoryLabelY = 41;
	}

	private void creux(GuiGraphics g, int x, int y) {
		g.fill(x - 1, y - 1, x + 17, y + 17, 0xFF2A180C);
		g.fill(x, y, x + 17, y + 17, 0xFFB08A5A);
		g.fill(x, y, x + 16, y + 16, 0xFF5A3A1E);
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		int x = leftPos, y = topPos;
		g.fill(x, y, x + imageWidth, y + imageHeight, 0xFF1E120A);
		g.fill(x + 1, y + 1, x + imageWidth - 1, y + imageHeight - 1, 0xFF6E3E1E);
		g.fill(x + 3, y + 3, x + imageWidth - 3, y + 38, 0xFF8A5428);
		for (int[] c : new int[][] {{2, 2}, {imageWidth - 6, 2}, {2, imageHeight - 6}, {imageWidth - 6, imageHeight - 6}})
			g.fill(x + c[0], y + c[1], x + c[0] + 4, y + c[1] + 4, 0xFFD6A030);
		for (int i = 0; i < Reliure.CASES; i++) creux(g, x + 8 + i * 18, y + 20);
		for (int r = 0; r < 3; r++) for (int c = 0; c < 9; c++) creux(g, x + 8 + c * 18, y + 52 + r * 18);
		for (int c = 0; c < 9; c++) creux(g, x + 8 + c * 18, y + 110);
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		g.drawString(font, title, 8, 7, 0xFFE9B0, false);
		g.drawString(font, playerInventoryTitle, 8, inventoryLabelY, 0xFFE9B0, false);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
	}
}
