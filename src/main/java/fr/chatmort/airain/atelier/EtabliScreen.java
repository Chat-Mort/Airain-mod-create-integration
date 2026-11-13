package fr.chatmort.airain.atelier;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

/** Écran de l'établi : le fond de la table de craft. */
public class EtabliScreen extends AbstractContainerScreen<EtabliMenu> {
	private static final ResourceLocation FOND = ResourceLocation.withDefaultNamespace("textures/gui/container/crafting_table.png");
	public EtabliScreen(EtabliMenu m, Inventory inv, Component t) { super(m, inv, t); titleLabelX = 29; }
	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
	}
	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		g.blit(FOND, leftPos, topPos, 0, 0, imageWidth, imageHeight);
	}
}
