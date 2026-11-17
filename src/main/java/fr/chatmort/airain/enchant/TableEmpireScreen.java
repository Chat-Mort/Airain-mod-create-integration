package fr.chatmort.airain.enchant;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.ChatFormatting;
import fr.chatmort.airain.gui.InterfaceHD;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

/** Écran de la table de l'Empire : une ligne par enchantement du répertoire, un bouton par niveau disponible. */
public class TableEmpireScreen extends AbstractContainerScreen<TableEmpireMenu> {
	private static final int LISTE_X = 50, LISTE_Y = 18, LIGNE = 18, VISIBLES = 6, LARGEUR = 176, BOUTON = 15;
	private static final int LIGNE_FOND = 0xFF3E2A16, LIGNE_SURVOL = 0xFF523A1E, SEPARATION = 0xFF281A0C, BRUN = 0x3A220E;
	private static final net.minecraft.resources.ResourceLocation FOND = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/imperial_table.png");
	private static final net.minecraft.resources.ResourceLocation ELEMENTS = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/widgets.png");
	private int defilement;
	// interface HD, mode sélection : une ligne choisie, un niveau choisi par ligne (flèches), puis « Graver »
	private static final int HD_LX = 50, HD_LY = 18, HD_LW = 162, HD_LIGNE = 17, HD_VIS = 5;
	private int choisie = -1;
	private final java.util.Map<Integer, Integer> niveaux = new java.util.HashMap<>();
	private Button graver;

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
						|| (minecraft.player.experienceLevel >= Bibliotheque.coutXp(ligne.enchantement(), n, Bibliotheque.actuel(objet, ligne.enchantement())) && menu.lapis() >= Bibliotheque.coutLapis(ligne.enchantement(), n, Bibliotheque.actuel(objet, ligne.enchantement()))
							&& (!ligne.parTome(n) || menu.encre() > 0)));
				b.add(new Bouton(i + defilement, n, x, y + 2, possible, ligne));
			}
		}
		return b;
	}

	/** Panneau de laiton : cases (avec leurs silhouettes), registre riveté, tuyau et engrenages, plaque de titre. */
	/** « 14 3 » avec 14 barré quand le prix est réduit, sinon le prix seul. */
	private static Component prix(int plein, int reduit) {
		if (reduit >= plein) return Component.literal(String.valueOf(reduit));
		return Component.literal(String.valueOf(plein)).withStyle(ChatFormatting.STRIKETHROUGH, ChatFormatting.DARK_GRAY)
			.append(Component.literal(" " + reduit).withStyle(s -> s.withStrikethrough(false).withColor(ChatFormatting.GREEN)));
	}

	@Override
	protected void init() {
		super.init();
		graver = null;
		if (InterfaceHD.actif()) {
			int by = topPos + HD_LY + HD_LIGNE * HD_VIS + 3;
			graver = addRenderableWidget(Button.builder(Component.translatable("airain.table.graver"), b -> graverChoix())
				.bounds(leftPos + HD_LX + HD_LW + 10 - 74, by, 74, 20).build());
		}
	}

	@Override
	protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
		if (InterfaceHD.actif()) { g.blit(FOND, leftPos, topPos, 0, 0, imageWidth, imageHeight, 512, 256); return; }
		g.blit(FOND, leftPos, topPos, 0, 0, imageWidth, imageHeight, 256, 256);
	}

	// ---------------------------------------------------------------- interface HD : mode sélection

	private int niveau(int index, TableEmpireMenu.Ligne l) { return Math.max(1, Math.min(l.niveauMax(), niveaux.getOrDefault(index, l.niveauMax()))); }

	/** Ce niveau peut-il être gravé tout de suite (objet compatible, niveaux, lapis, encre pour le tome) ? */
	private boolean possible(TableEmpireMenu.Ligne ligne, int n) {
		ItemStack objet = menu.objet();
		int deja = Bibliotheque.actuel(objet, ligne.enchantement());
		return Bibliotheque.applicable(objet, ligne.enchantement(), n)
			&& (minecraft.player.getAbilities().instabuild
				|| (minecraft.player.experienceLevel >= Bibliotheque.coutXp(ligne.enchantement(), n, deja) && menu.lapis() >= Bibliotheque.coutLapis(ligne.enchantement(), n, deja)
					&& (!ligne.parTome(n) || menu.encre() > 0)));
	}

	private void graverChoix() {
		if (minecraft == null || minecraft.level == null || minecraft.gameMode == null) return;
		List<TableEmpireMenu.Ligne> l = menu.lignes(minecraft.level);
		if (choisie < 0 || choisie >= l.size()) return;
		TableEmpireMenu.Ligne ligne = l.get(choisie);
		int n = niveau(choisie, ligne);
		if (possible(ligne, n)) minecraft.gameMode.handleInventoryButtonClick(menu.containerId, choisie * 16 + n);
	}

	private void blitHD(GuiGraphics g, int x, int y, int u, int v, int w, int h) { g.blit(FOND, x, y, u, v, w, h, 512, 256); }

	private void renderHD(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
		super.render(g, mouseX, mouseY, partialTick);
		if (minecraft == null || minecraft.level == null) return;
		List<TableEmpireMenu.Ligne> l = menu.lignes(minecraft.level);
		int x0 = leftPos + HD_LX, y0 = topPos + HD_LY;
		if (choisie >= l.size()) choisie = -1;
		if (choisie < 0 && !l.isEmpty()) choisie = 0;
		if (l.isEmpty()) g.drawWordWrap(font, Component.translatable("airain.table.vide"), x0 + 5, y0 + 5, HD_LW - 10, InterfaceHD.ARDOISE_TEXTE);
		defilement = Math.max(0, Math.min(defilement, l.size() - HD_VIS));
		TableEmpireMenu.Ligne info = null; int infoN = 0;
		for (int i = 0; i < HD_VIS && i + defilement < l.size(); i++) {
			int idx = i + defilement;
			TableEmpireMenu.Ligne ligne = l.get(idx);
			int y = y0 + i * HD_LIGNE, n = niveau(idx, ligne);
			boolean choix = idx == choisie;
			g.fill(x0, y, x0 + HD_LW, y + HD_LIGNE - 1, choix ? 0xFF30343D : 0xFF272A32);
			g.fill(x0, y + HD_LIGNE - 1, x0 + HD_LW, y + HD_LIGNE, 0xFF1B1E24);
			if (choix) {   // filet cramoisi tout autour de la ligne choisie
				g.fill(x0, y, x0 + HD_LW, y + 1, 0xFFAF1D25); g.fill(x0, y + HD_LIGNE - 2, x0 + HD_LW, y + HD_LIGNE - 1, 0xFFAF1D25);
				g.fill(x0, y, x0 + 1, y + HD_LIGNE - 1, 0xFFAF1D25); g.fill(x0 + HD_LW - 1, y, x0 + HD_LW, y + HD_LIGNE - 1, 0xFFAF1D25);
			}
			boolean applicable = Bibliotheque.applicable(menu.objet(), ligne.enchantement(), n) || menu.objet().isEmpty();
			int place = HD_LW - 50;
			String nom = ligne.enchantement().value().description().getString();
			if (font.width(nom) > place) nom = font.plainSubstrByWidth(nom, place - font.width("...")) + "...";
			g.drawString(font, nom, x0 + 5, y + 5, applicable ? InterfaceHD.AIRAIN : InterfaceHD.ARDOISE_TEXTE, true);
			// ◀ touche ▶ (de droite à gauche depuis le bord du registre)
			int xd = x0 + HD_LW - 4 - 7, xt = xd - 2 - 15, xg = xt - 2 - 7;
			boolean surG = mouseX >= xg && mouseX < xg + 7 && mouseY >= y + 3 && mouseY < y + 14;
			boolean surD = mouseX >= xd && mouseX < xd + 7 && mouseY >= y + 3 && mouseY < y + 14;
			boolean surT = mouseX >= xt && mouseX < xt + 15 && mouseY >= y + 1 && mouseY < y + 15;
			blitHD(g, xg, y + 3, 240 + 7 * (n <= 1 ? 4 : surG ? 2 : 0), 60, 7, 11);
			blitHD(g, xd, y + 3, 240 + 7 * (n >= ligne.niveauMax() ? 5 : surD ? 3 : 1), 60, 7, 11);
			int etat = !possible(ligne, n) ? 2 : ligne.parTome(n) ? 3 : surT ? 1 : 0;
			blitHD(g, xt, y + 1, 240 + 15 * (Math.min(n, 10) - 1), 14 * etat, 15, 14);
			if (surT) { info = ligne; infoN = n; }
		}
		// chariot du rail de défilement
		if (l.size() > HD_VIS) {
			int h = HD_LIGNE * HD_VIS - 1, bh = Math.max(10, h * HD_VIS / l.size()), yb = y0 + (h - bh) * defilement / (l.size() - HD_VIS);
			g.fill(x0 + HD_LW + 5, yb, x0 + HD_LW + 9, yb + bh, 0xFFE1BA6E);
		}
		// coût de la ligne choisie, et « Graver »
		int by = y0 + HD_LIGNE * HD_VIS + 3;
		boolean ok = false;
		if (choisie >= 0 && choisie < l.size()) {
			TableEmpireMenu.Ligne ligne = l.get(choisie);
			int n = niveau(choisie, ligne), deja = Bibliotheque.actuel(menu.objet(), ligne.enchantement());
			g.drawString(font, Component.translatable("airain.table.cout_court"), x0 + 5, by + 6, 0xC9B48A, true);
			String xp = String.valueOf(Bibliotheque.coutXp(ligne.enchantement(), n, deja));
			g.drawString(font, xp, x0 + 31, by + 6, 0x80FF20, true);
			g.drawString(font, Component.translatable("airain.table.niv"), x0 + 33 + font.width(xp), by + 6, InterfaceHD.ARDOISE_TEXTE, true);
			g.renderItem(new ItemStack(net.minecraft.world.item.Items.LAPIS_LAZULI), x0 + 66, by + 2);
			g.drawString(font, String.valueOf(Bibliotheque.coutLapis(ligne.enchantement(), n, deja)), x0 + 83, by + 6, 0xE8E2D4, true);
			ok = possible(ligne, n);
		}
		if (graver != null) graver.active = ok;
		if (info != null) {
			List<Component> t = new ArrayList<>();
			t.add(net.minecraft.world.item.enchantment.Enchantment.getFullname(info.enchantement(), infoN));
			int deja = Bibliotheque.actuel(menu.objet(), info.enchantement());
			t.add(Component.translatable("airain.table.cout", prix(Bibliotheque.coutXp(info.enchantement(), infoN), Bibliotheque.coutXp(info.enchantement(), infoN, deja)),
				prix(Bibliotheque.coutLapis(info.enchantement(), infoN), Bibliotheque.coutLapis(info.enchantement(), infoN, deja))).withStyle(ChatFormatting.GRAY));
			if (info.parTome(infoN)) t.add(Component.translatable("airain.table.tome").withStyle(ChatFormatting.GOLD));
			if (Bibliotheque.depasse(info.enchantement(), infoN)) t.add(Component.translatable("airain.table.depasse").withStyle(ChatFormatting.GOLD));
			if (!Bibliotheque.applicable(menu.objet(), info.enchantement(), infoN))
				t.add(Component.translatable(menu.objet().isEmpty() ? "airain.table.sans_objet" : "airain.table.incompatible").withStyle(ChatFormatting.RED));
			g.renderComponentTooltip(font, t, mouseX, mouseY);
		} else renderTooltip(g, mouseX, mouseY);
	}

	private boolean clicHD(double mx, double my) {
		if (minecraft == null || minecraft.level == null) return false;
		List<TableEmpireMenu.Ligne> l = menu.lignes(minecraft.level);
		int x0 = leftPos + HD_LX, y0 = topPos + HD_LY;
		for (int i = 0; i < HD_VIS && i + defilement < l.size(); i++) {
			int idx = i + defilement, y = y0 + i * HD_LIGNE;
			if (my < y || my >= y + HD_LIGNE || mx < x0 || mx >= x0 + HD_LW) continue;
			TableEmpireMenu.Ligne ligne = l.get(idx);
			int n = niveau(idx, ligne), xd = x0 + HD_LW - 4 - 7, xg = xd - 2 - 15 - 2 - 7;
			choisie = idx;
			if (mx >= xg && mx < xg + 7 && n > 1) niveaux.put(idx, n - 1);
			else if (mx >= xd && mx < xd + 7 && n < ligne.niveauMax()) niveaux.put(idx, n + 1);
			minecraft.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK, 1f));
			return true;
		}
		return false;
	}

	@Override
	public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
		if (InterfaceHD.actif()) { renderHD(g, mouseX, mouseY, partialTick); return; }
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
			var hs = survole.ligne.enchantement();
			int deja = Bibliotheque.actuel(menu.objet(), hs);
			int xp = Bibliotheque.coutXp(hs, survole.niveau, deja), plein = Bibliotheque.coutXp(hs, survole.niveau);
			int lapis = Bibliotheque.coutLapis(hs, survole.niveau, deja), lapisPlein = Bibliotheque.coutLapis(hs, survole.niveau);
			// prix réduit affiché comme chez les villageois : l'ancien prix barré, puis le nouveau
			info.add(Component.translatable("airain.table.cout", prix(plein, xp), prix(lapisPlein, lapis)).withStyle(ChatFormatting.GRAY));
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
		if (InterfaceHD.actif()) {
			g.drawString(font, title, 10, 6, InterfaceHD.AIRAIN, true);
			g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, InterfaceHD.AIRAIN_SOMBRE, true);
			return;
		}
		g.drawString(font, title, 10, 6, BRUN, false);
		g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, BRUN, false);
	}

	@Override
	public boolean mouseClicked(double mouseX, double mouseY, int button) {
		if (InterfaceHD.actif()) {
			if (button == 0 && clicHD(mouseX, mouseY)) return true;
			return super.mouseClicked(mouseX, mouseY, button);
		}
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
