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
	private static final int LIGNE_FOND = 0xFF3E2A16, LIGNE_SURVOL = 0xFF523A1E, SEPARATION = 0xFF281A0C, BRUN = 0x3A220E;
	private static final net.minecraft.resources.ResourceLocation FOND = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/table_empire.png");
	private static final net.minecraft.resources.ResourceLocation ELEMENTS = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/elements.png");
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
						|| (minecraft.player.experienceLevel >= Bibliotheque.coutXp(ligne.enchantement(), n) && menu.lapis() >= Bibliotheque.coutLapis(ligne.enchantement(), n)
							&& (!ligne.parTome(n) || menu.encre() > 0)));
				b.add(new Bouton(i + defilement, n, x, y + 2, possible, ligne));
			}
		}
		return b;
	}

	/** Panneau de laiton : cases (avec leurs silhouettes), registre riveté, tuyau et engrenages, plaque de titre. */
	@Override
	protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
		g.blit(FOND, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
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
			g.fill(leftPos + LISTE_X + 1, y + LIGNE - 1, leftPos + LISTE_X + LARGEUR - 1, y + LIGNE, SEPARATION);
			// le nom s'arrête avant les touches (le nom complet reste dans l'infobulle)
			int place = LARGEUR - 10 - ligne.niveauMax() * (BOUTON + 1);
			String nom = ligne.enchantement().value().description().getString();
			if (font.width(nom) > place) nom = font.plainSubstrByWidth(nom, place - font.width("…")) + "…";
			g.drawString(font, nom, leftPos + LISTE_X + 4, y + 5, 0xF0DCAA, false);
		}
		Bouton survole = null;
		for (Bouton b : boutons()) {
			boolean dessus = mouseX >= b.x && mouseX < b.x + BOUTON && mouseY >= b.y && mouseY < b.y + 14;
			boolean tome = b.ligne.parTome(b.niveau);
			// touche de machine à écrire : ivoire (disponible), grise (hors de portée), dorée cerclée d'améthyste (tome + encre)
			int touche = (tome ? 3 : 0) + (!b.actif ? 2 : dessus ? 1 : 0);
			g.blit(ELEMENTS, b.x, b.y, touche * 16, 0, 15, 14, 128, 64);
			Component chiffre = Component.translatable("enchantment.level." + b.niveau);
			g.drawString(font, chiffre, b.x + 8 - font.width(chiffre) / 2, b.y + 3, b.actif ? BRUN : 0x968C78, false);
			if (dessus)
				survole = b;
		}
		if (l.size() > VISIBLES)
			g.drawString(font, (defilement + 1) + "-" + Math.min(l.size(), defilement + VISIBLES) + " / " + l.size(),
				leftPos + LISTE_X + LARGEUR - 50, topPos + LISTE_Y + VISIBLES * LIGNE + 3, BRUN, false);
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
		g.drawString(font, title, 10, 6, BRUN, false);
		g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, BRUN, false);
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
