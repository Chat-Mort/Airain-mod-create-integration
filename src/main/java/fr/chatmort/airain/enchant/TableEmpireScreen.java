package fr.chatmort.airain.enchant;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

/** Écran de la table de l'Empire : une ligne par enchantement du répertoire, un bouton par niveau disponible. */
public class TableEmpireScreen extends AbstractContainerScreen<TableEmpireMenu> {
	private static final int LISTE_X = 50, LISTE_Y = 18, LIGNE = 18, VISIBLES = 6, LARGEUR = 176, BOUTON = 15;
	private static final int FOND = 0xFF2A211B, CADRE = 0xFFB0853A, CASE = 0xFF1A1512, LIGNE_FOND = 0xFF3A2E24, LIGNE_SURVOL = 0xFF4E3D2E;
	private int defilement;

	public TableEmpireScreen(TableEmpireMenu menu, Inventory inv, Component titre) {
		super(menu, inv, titre);
		imageWidth = 232;
		imageHeight = 222;
		inventoryLabelX = 35;
		inventoryLabelY = 129;
	}

	private record Bouton(int index, int niveau, int x, int y, boolean actif, TableEmpireMenu.Ligne ligne) {}

	private List<Bouton> boutons() {
		List<Bouton> b = new ArrayList<>();
		if (minecraft == null || minecraft.level == null)
			return b;
		List<TableEmpireMenu.Ligne> l = menu.lignes(minecraft.level);
		ItemStack objet = menu.objet();
		for (int i = 0; i < VISIBLES && i + defilement < l.size(); i++) {
			TableEmpireMenu.Ligne ligne = l.get(i + defilement);
			int y = topPos + LISTE_Y + i * LIGNE;
			for (int n = 1; n <= ligne.niveauMax(); n++) {
				int x = leftPos + LISTE_X + LARGEUR - (ligne.niveauMax() - n + 1) * (BOUTON + 1) - 2;
				boolean possible = Bibliotheque.applicable(objet, ligne.enchantement(), n)
					&& (minecraft.player.getAbilities().instabuild
						|| (minecraft.player.experienceLevel >= Bibliotheque.coutXp(ligne.enchantement(), n) && menu.lapis() >= Bibliotheque.coutLapis(ligne.enchantement(), n)));
				b.add(new Bouton(i + defilement, n, x, y + 2, possible, ligne));
			}
		}
		return b;
	}

	@Override
	protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
		int x = leftPos, y = topPos;
		g.fill(x, y, x + imageWidth, y + imageHeight, CADRE);
		g.fill(x + 2, y + 2, x + imageWidth - 2, y + imageHeight - 2, FOND);
		for (int[] c : new int[][] {{22, 35}, {22, 60}})
			caseVide(g, x + c[0], y + c[1]);
		for (int l = 0; l < 3; l++)
			for (int c = 0; c < 9; c++)
				caseVide(g, x + 35 + c * 18, y + 140 + l * 18);
		for (int c = 0; c < 9; c++)
			caseVide(g, x + 35 + c * 18, y + 198);
		// liste
		g.fill(x + LISTE_X - 1, y + LISTE_Y - 1, x + LISTE_X + LARGEUR + 1, y + LISTE_Y + VISIBLES * LIGNE + 1, CADRE);
		g.fill(x + LISTE_X, y + LISTE_Y, x + LISTE_X + LARGEUR, y + LISTE_Y + VISIBLES * LIGNE, CASE);
	}

	private void caseVide(GuiGraphics g, int x, int y) {
		g.fill(x - 1, y - 1, x + 17, y + 17, 0xFF8B8B8B);
		g.fill(x, y, x + 16, y + 16, 0xFF373737);
	}

	@Override
	public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
		super.render(g, mouseX, mouseY, partialTick);
		if (minecraft == null || minecraft.level == null)
			return;
		List<TableEmpireMenu.Ligne> l = menu.lignes(minecraft.level);
		if (l.isEmpty()) {
			g.drawWordWrap(font, Component.translatable("airain.table.vide"), leftPos + LISTE_X + 6, topPos + LISTE_Y + 6, LARGEUR - 12, 0xA08060);
		}
		defilement = Math.max(0, Math.min(defilement, l.size() - VISIBLES));
		for (int i = 0; i < VISIBLES && i + defilement < l.size(); i++) {
			TableEmpireMenu.Ligne ligne = l.get(i + defilement);
			int y = topPos + LISTE_Y + i * LIGNE;
			boolean survol = mouseX >= leftPos + LISTE_X && mouseX < leftPos + LISTE_X + LARGEUR && mouseY >= y && mouseY < y + LIGNE;
			g.fill(leftPos + LISTE_X + 1, y + 1, leftPos + LISTE_X + LARGEUR - 1, y + LIGNE - 1, survol ? LIGNE_SURVOL : LIGNE_FOND);
			g.drawString(font, ligne.enchantement().value().description(), leftPos + LISTE_X + 4, y + 5, 0xE8D8B0, false);
		}
		Bouton survole = null;
		for (Bouton b : boutons()) {
			boolean dessus = mouseX >= b.x && mouseX < b.x + BOUTON && mouseY >= b.y && mouseY < b.y + 14;
			boolean tome = b.ligne.parTome(b.niveau);
			int fond = !b.actif ? (tome ? 0xFF3A3018 : 0xFF2B2B2B) : tome ? (dessus ? 0xFFFFE070 : 0xFFE0B020) : dessus ? 0xFFD9A54E : 0xFF8A6A2E;
			g.fill(b.x, b.y, b.x + BOUTON, b.y + 14, fond);
			if (tome)
				g.renderOutline(b.x, b.y, BOUTON, 14, b.actif ? 0xFFFFF4C0 : 0xFF806020);
			Component chiffre = Component.translatable("enchantment.level." + b.niveau);
			g.drawCenteredString(font, chiffre, b.x + BOUTON / 2 + 1, b.y + 3, b.actif ? (tome ? 0x3A2400 : 0xFFFFFF) : (tome ? 0xA08040 : 0x707070));
			if (dessus)
				survole = b;
		}
		if (l.size() > VISIBLES)
			g.drawString(font, (defilement + 1) + "-" + Math.min(l.size(), defilement + VISIBLES) + " / " + l.size(),
				leftPos + LISTE_X + LARGEUR - 50, topPos + LISTE_Y + VISIBLES * LIGNE + 3, 0xA08060, false);
		if (survole != null) {
			List<Component> info = new ArrayList<>();
			info.add(net.minecraft.world.item.enchantment.Enchantment.getFullname(survole.ligne.enchantement(), survole.niveau));
			info.add(Component.translatable("airain.table.cout", Bibliotheque.coutXp(survole.ligne.enchantement(), survole.niveau),
				Bibliotheque.coutLapis(survole.ligne.enchantement(), survole.niveau)).withStyle(ChatFormatting.GRAY));
			if (survole.ligne.parTome(survole.niveau))
				info.add(Component.translatable("airain.table.tome").withStyle(ChatFormatting.GOLD));
			if (Bibliotheque.depasse(survole.ligne.enchantement(), survole.niveau))
				info.add(Component.translatable("airain.table.depasse").withStyle(ChatFormatting.GOLD));
			if (!Bibliotheque.applicable(menu.objet(), survole.ligne.enchantement(), survole.niveau))
				info.add(Component.translatable(menu.objet().isEmpty() ? "airain.table.sans_objet" : "airain.table.incompatible").withStyle(ChatFormatting.RED));
			g.renderComponentTooltip(font, info, mouseX, mouseY);
		} else {
			renderTooltip(g, mouseX, mouseY);
		}
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
		g.drawString(font, title, 8, 6, 0xE8D8B0, false);
		g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, 0xB0A080, false);
	}

	@Override
	public boolean mouseClicked(double mouseX, double mouseY, int button) {
		for (Bouton b : boutons()) {
			if (b.actif && mouseX >= b.x && mouseX < b.x + BOUTON && mouseY >= b.y && mouseY < b.y + 14) {
				if (minecraft != null && minecraft.gameMode != null)
					minecraft.gameMode.handleInventoryButtonClick(menu.containerId, b.index * 16 + b.niveau);
				return true;
			}
		}
		return super.mouseClicked(mouseX, mouseY, button);
	}

	@Override
	public boolean mouseScrolled(double mouseX, double mouseY, double dx, double dy) {
		defilement = Math.max(0, defilement - (int) Math.signum(dy));
		return true;
	}
}
