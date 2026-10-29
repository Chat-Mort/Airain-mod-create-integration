package fr.chatmort.airain.banc;

import java.util.List;

import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

/** Écran du banc d'entretien, au style de l'Empire : réservoir d'huile en verre, conduite de progression, modules. */
public class BancScreen extends AbstractContainerScreen<BancMenu> {
	private static final ResourceLocation FOND = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/banc.png");

	public BancScreen(BancMenu menu, Inventory inv, Component titre) {
		super(menu, inv, titre);
		imageWidth = 176;
		imageHeight = 186;
		inventoryLabelY = 93;
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		int x = leftPos, y = topPos;
		g.blit(FOND, x, y, 0, 0, imageWidth, imageHeight, 256, 256);
		// huile : de l'ambre foncé au miel, avec un reflet
		int h = Math.round(60f * Math.min(1f, menu.huile() / (float) BancEntretienBlockEntity.CAPACITE));
		if (h > 0) {
			g.fillGradient(x + 11, y + 80 - h, x + 25, y + 80, 0xFFC08A2A, 0xFF7A4A12);
			g.fill(x + 13, y + 80 - h, x + 14, y + 80, 0x60FFF0C0);
			g.fill(x + 11, y + 80 - h, x + 25, y + 81 - h, 0xFFE8B850);
		}
		// conduite de progression : le laiton avance vers la case du résultat
		int p = Math.round(44 * menu.avancement());
		if (p > 0) {
			g.fillGradient(x + 59, y + 41, x + 59 + p, y + 47, 0xFFF0C868, 0xFF9A6A24);
			if (menu.travaille()) g.fill(x + 58 + p, y + 41, x + 59 + p, y + 47, 0xFFFFF4C0);
		}
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		g.drawString(font, title, 10, 6, WidgetsEmpire.BRUN, false);
		g.drawString(font, playerInventoryTitle, 8, inventoryLabelY, WidgetsEmpire.BRUN, false);
		Component etat = menu.vitesse() < 16 ? Component.translatable("airain.banc.arret")
			: menu.secondes() >= 0 && menu.travaille() ? Component.translatable("airain.banc.rythme", menu.vitesse(), menu.secondes())
			: Component.translatable("airain.banc.vitesse", menu.vitesse());
		g.drawString(font, etat, 36, 82, WidgetsEmpire.BRUN, false);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int rx = mx - leftPos, ry = my - topPos;
		if (rx >= 10 && rx < 26 && ry >= 19 && ry < 81)
			g.renderComponentTooltip(font, List.of(Component.translatable("airain.banc.huile", menu.huile(), BancEntretienBlockEntity.CAPACITE)
				.withStyle(ChatFormatting.GOLD)), mx, my);
		else if (rx >= 149 && rx < 167 && ry >= 17 && ry < 77 && hoveredSlot != null && !hoveredSlot.hasItem())
			g.renderComponentTooltip(font, List.of(Component.translatable("airain.banc.emplacement_module").withStyle(ChatFormatting.GRAY)), mx, my);
		else renderTooltip(g, mx, my);
	}
}
