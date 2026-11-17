package fr.chatmort.airain.trophee;

import com.mojang.blaze3d.platform.Lighting;
import com.mojang.math.Axis;
import fr.chatmort.airain.gui.InterfaceHD;
import fr.chatmort.airain.gui.PanneauHD;
import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Réglages du piédestal, au style de l'Empire : page « Socle » (matériau, velours, capitonnage, garnitures, colonne)
 * et page « Trophée » (présentation, éclairage, particules, plaque gravée). Aperçu 3D tournant dans la vitrine.
 */
public class SocleScreen extends Screen {
	private static final String[] CLES = {"materiau", "velours", "capitonnage", "garniture", "presentation", "hauteur", "lumiere", "particules", "plaque"};
	private static final int[][] PAGES = {{0, 1, 2, 3, 5}, {4, 6, 7, 8}};
	private static final String[] NOMS_PAGES = {"socle", "trophee"};
	private final BlockPos pos;
	private final int[] choix;
	private String plaque;
	private int page;
	private EditBox champ;

	public SocleScreen(BlockPos pos, SocleApparence a, String plaque) {
		super(Component.translatable("block.airain.trophy_pedestal"));
		this.pos = pos; this.choix = a.valeurs(); this.plaque = plaque;
	}

	private int haut() { return height / 2 - 108; }

	@Override
	protected void init() {
		if (InterfaceHD.actif()) { initHD(); return; }
		int x = width / 2 - 150, y = haut();
		int[] l = PAGES[page];
		for (int n = 0; n < l.length; n++) {
			final int i = l[n];
			int ly = y + 14 + n * 21;
			addRenderableWidget(new WidgetsEmpire.Fleche(x + 78, ly + 2, false, b -> choix[i] = Math.floorMod(choix[i] - 1, SocleApparence.TAILLES[i])));
			addRenderableWidget(new WidgetsEmpire.Fleche(x + 186, ly + 2, true, b -> choix[i] = Math.floorMod(choix[i] + 1, SocleApparence.TAILLES[i])));
		}
		champ = null;
		if (page == 1) {
			champ = new EditBox(font, x + 5, y + 14 + l.length * 21 + 20, 182, 10, Component.translatable("airain.socle.plaque_texte"));
			champ.setBordered(false); champ.setTextColor(WidgetsEmpire.CREME);
			champ.setMaxLength(32); champ.setValue(plaque); champ.setResponder(v -> plaque = v);
			addRenderableWidget(champ);
		}
		for (int k = 0; k < PAGES.length; k++) {
			final int cible = k;
			addRenderableWidget(new WidgetsEmpire.Onglet(x + 4 + k * 74, y - 23, Component.translatable("airain.socle.onglet." + NOMS_PAGES[k]),
				k == page, b -> { page = cible; rebuildWidgets(); }));
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 186, 94, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 96, y + 186, 94, 20).build());
	}

	/** Interface HD : onglets raccordés au bac, rangées au pas de 21 dans le bac, flèches à 5 px de son bord. */
	private void initHD() {
		int x = width / 2 - 150, y = haut();
		int[] l = PAGES[page];
		for (int n = 0; n < l.length; n++) {
			final int i = l[n];
			int ly = y + PanneauHD.Y_LIGNES + n * PanneauHD.PAS;
			addRenderableWidget(new WidgetsEmpire.Fleche(x + 79, ly, false, b -> choix[i] = Math.floorMod(choix[i] - 1, SocleApparence.TAILLES[i])));
			addRenderableWidget(new WidgetsEmpire.Fleche(x + 179, ly, true, b -> choix[i] = Math.floorMod(choix[i] + 1, SocleApparence.TAILLES[i])));
		}
		champ = null;
		if (page == 1) {
			// plaque gravée : une rangée de libellé, puis le champ sur toute la largeur du bac
			champ = new EditBox(font, x + 8, y + 142, 184, 10, Component.translatable("airain.socle.plaque_texte"));
			champ.setBordered(false); champ.setTextColor(WidgetsEmpire.CREME);
			champ.setMaxLength(32); champ.setValue(plaque); champ.setResponder(v -> plaque = v);
			addRenderableWidget(champ);
		}
		// onglets : l'actif est ajouté en dernier pour passer devant les autres
		for (int k = PAGES.length - 1; k >= -1; k--) {
			int c = k < 0 ? page : k;
			if (k >= 0 && k == page) continue;
			final int cible = c;
			addRenderableWidget(new WidgetsEmpire.Onglet(x + 2 + c * 74, y + PanneauHD.Y_ONGLETS, 72, 16,
				Component.translatable("airain.socle.onglet." + NOMS_PAGES[c]), c == page, b -> { page = cible; rebuildWidgets(); }));
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 186, PanneauHD.BOUTON, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + PanneauHD.ECART_BOUTONS, y + 186, PanneauHD.BOUTON, 20).build());
	}

	private void valider() {
		PacketDistributor.sendToServer(new ConfigurerSocle(pos, SocleApparence.depuis(choix).pack(), plaque.trim()));
		onClose();
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if ((key == 257 || key == 335) && champ != null && champ.isFocused()) { valider(); return true; }
		return super.keyPressed(key, scan, mods);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		int x = width / 2 - 150, y = haut();
		if (InterfaceHD.actif()) {
			PanneauHD.fond(g, x, y);
			if (page == 1) PanneauHD.champ(g, x + 4, y + 138, 192, champ != null && champ.isFocused());
			return;
		}
		g.blit(WidgetsEmpire.PANNEAU, x - 10, y - 10, 0, 0, 310, 226, 512, 256);
		if (page == 1) WidgetsEmpire.creux(g, x, y + 14 + PAGES[1].length * 21 + 14, 190, 20);
	}

	/** Libellé d'une valeur : le velours reprend les couleurs des bannières, les garnitures leurs ornements. */
	private static String valeur(int k, int v) {
		if (k == 1) return "airain.etendard.fond." + v;
		if (k == 3) return "airain.etendard.ornement." + v;
		return "airain.socle." + CLES[k] + "." + v;
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = width / 2 - 150, y = haut();
		if (InterfaceHD.actif()) {
			// interface HD : titre sur l'ardoise, libellés à points de conduite, valeurs en cartouches émaillés
			g.drawString(font, title, x + 2, y - 4, InterfaceHD.AIRAIN, true);
			int[] l = PAGES[page];
			for (int n = 0; n < l.length; n++) {
				int k = l[n], ly = y + PanneauHD.Y_LIGNES + n * PanneauHD.PAS;
				PanneauHD.libelle(g, font, x + 4, ly, x + 79, Component.translatable("airain.socle." + CLES[k]));
				PanneauHD.cartouche(g, font, x + 97, ly, 80, Component.translatable(valeur(k, choix[k])), false);
			}
			if (page == 1) PanneauHD.libelle(g, font, x + 4, y + PanneauHD.Y_LIGNES + l.length * PanneauHD.PAS, x + 196, Component.translatable("airain.socle.plaque_texte"));
			apercu(g, x, y, pt);
			PanneauHD.reflets(g, x, y);
			return;
		}
		g.drawString(font, title, x + 2, y - 4, WidgetsEmpire.BRUN, false);
		int[] l = PAGES[page];
		for (int n = 0; n < l.length; n++) {
			int k = l[n], ly = y + 14 + n * 21;
			WidgetsEmpire.creux(g, x + 96, ly + 2, 88, 16);
			g.drawString(font, Component.translatable("airain.socle." + CLES[k]), x, ly + 6, WidgetsEmpire.BRUN, false);
			g.drawCenteredString(font, Component.translatable(valeur(k, choix[k])), x + 140, ly + 6, WidgetsEmpire.CREME);
		}
		if (page == 1) g.drawString(font, Component.translatable("airain.socle.plaque_texte"), x, y + 14 + l.length * 21 + 4, WidgetsEmpire.BRUN, false);
		apercu(g, x, y, pt);
	}

	/** Le piédestal en 3D, qui tourne lentement dans la vitrine. */
	private void apercu(GuiGraphics g, int x, int y, float pt) {
		if (minecraft == null || minecraft.level == null) return;
		SocleApparence a = SocleApparence.depuis(choix);
		ItemStack t = ItemStack.EMPTY; int jour = 1;
		if (minecraft.level.getBlockEntity(pos) instanceof SocleBlockEntity s) { t = s.trophee(); jour = s.jour(); }
		if (t.isEmpty()) t = new ItemStack(Items.NETHER_STAR);       // pour voir la présentation
		float temps = minecraft.level.getGameTime() + pt;
		float S = a.haute() ? 38 : 52;
		g.pose().pushPose();
		g.pose().translate(x + 252, y + 140, 120);
		g.pose().scale(S, S, -S);
		g.pose().mulPose(Axis.ZP.rotationDegrees(180));
		g.pose().mulPose(Axis.XP.rotationDegrees(-22));
		g.pose().mulPose(Axis.YP.rotationDegrees(temps * 0.8f));
		g.pose().translate(-0.5, 0, -0.5);
		Lighting.setupForEntityInInventory();
		SocleRenderer.dessiner(g.pose(), g.bufferSource(), a, t, plaque, jour, temps, LightTexture.FULL_BRIGHT, Direction.NORTH, minecraft.level);
		g.flush();
		Lighting.setupFor3DItems();
		g.pose().popPose();
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
