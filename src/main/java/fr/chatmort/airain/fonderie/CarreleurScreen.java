package fr.chatmort.airain.fonderie;

import java.util.List;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Checkbox;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * 1.70 : écran de la table du carreleur. Quatre onglets (Création, Sols, Murs, Plafonds), fond et onglets dessinés
 * dans le style des écrans du mod ; boutons, case à cocher et curseur sont ceux du jeu (habillés par le pack HD).
 */
public class CarreleurScreen extends AbstractContainerScreen<CarreleurMenu> {
	private static final ResourceLocation FOND = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/tilers_table.png");
	private static final ResourceLocation FOND_RANGEMENT = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/tilers_table_storage.png");
	private static final ResourceLocation ONGLETS = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/tilers_table_tabs.png");
	private static final int OR = 0xFFE1BA6E, BLANC = 0xFFEBE6DC, GRIS = 0xFFBEBEBE;
	private static final String[] TITRES = {"airain.carreleur.sols", "airain.carreleur.murs", "airain.carreleur.plafonds"};

	// réglages de l'onglet Création (gardés tant que le jeu tourne)
	private static int type, choix, reglage = -1, bordL = 1;
	private static boolean bord;
	private static int defil;            // 1.70.2 : défilement de la liste des motifs (8 lignes visibles)
	private static final int LIGNES = 8;
	private static String nom = "";

	private Button btType, moins, plus, bMoins, bPlus, imprimer;
	private Checkbox caseBord;
	private Curseur curseur;
	private boolean glisse;              // 1.70.3 : curseur saisi (l'écran de conteneur ne transmet pas le glisser aux widgets)
	private EditBox champNom;

	public CarreleurScreen(CarreleurMenu m, Inventory inv, Component t) {
		super(m, inv, t);
		imageWidth = 264; imageHeight = 276;
	}

	private Generateur.Dessin dessin() {
		List<Generateur.Dessin> l = Generateur.PAR_TYPE.get(type);
		if (choix >= l.size()) choix = 0;
		return l.get(choix);
	}

	@Override
	protected void init() {
		super.init();
		Generateur.Dessin d = dessin();
		if (reglage < d.min || reglage > d.max) reglage = d.defaut;
		int x = leftPos, y = topPos;
		btType = addRenderableWidget(Button.builder(Component.empty(), b -> { type = (type + 1) % 3; choix = 0; defil = 0; reglage = dessin().defaut; maj(); }).bounds(x + 8, y + 30, 78, 20).build());
		moins = addRenderableWidget(Button.builder(Component.literal("−"), b -> { reglage = Math.max(dessin().min, reglage - 1); maj(); }).bounds(x + 132, y + 136, 20, 20).build());
		plus = addRenderableWidget(Button.builder(Component.literal("+"), b -> { reglage = Math.min(dessin().max, reglage + 1); maj(); }).bounds(x + 166, y + 136, 20, 20).build());
		curseur = addRenderableWidget(new Curseur(x + 90, y + 146, 100));
		caseBord = addRenderableWidget(Checkbox.builder(Component.translatable("airain.carreleur.bordure"), font).pos(x + 90, y + 169).selected(bord)
			.onValueChange((c, v) -> { bord = v; maj(); }).build());
		bMoins = addRenderableWidget(Button.builder(Component.literal("−"), b -> { bordL = Math.max(1, bordL - 1); maj(); }).bounds(x + 152, y + 168, 20, 20).build());
		bPlus = addRenderableWidget(Button.builder(Component.literal("+"), b -> { bordL = Math.min(3, bordL + 1); maj(); }).bounds(x + 184, y + 168, 20, 20).build());
		imprimer = addRenderableWidget(Button.builder(Component.translatable("airain.carreleur.imprimer"), b -> {
			PacketDistributor.sendToServer(new Carreleur.Imprimer(type, choix, reglage, bord ? bordL : 0, champNom.getValue()));
		}).bounds(x + 196, y + 150, 62, 20).build());
		champNom = new EditBox(font, x + 11, y + 169, 72, 10, Component.translatable("airain.carreleur.nom"));
		champNom.setBordered(false); champNom.setMaxLength(40); champNom.setValue(nom); champNom.setTextColor(BLANC);
		champNom.setResponder(s -> nom = s);
		addRenderableWidget(champNom);
		maj();
	}

	/** Remet les commandes d'accord avec l'onglet et le motif choisi. */
	private void maj() {
		boolean creation = menu.onglet() == 0;
		Generateur.Dessin d = dessin();
		boolean cases = d.reglage == Generateur.Reglage.CASE;
		btType.setMessage(Component.translatable("airain.carreleur.type." + Generateur.TYPES[type]).append("  ›"));
		btType.visible = creation;
		moins.visible = plus.visible = creation && cases;
		curseur.visible = creation && !cases;
		curseur.caler();
		caseBord.visible = creation;
		bMoins.visible = bPlus.visible = creation && bord;
		imprimer.visible = creation;
		champNom.visible = creation;
		menu.accentVisible = d.accent;
		menu.bordVisible = bord;
	}

	@Override
	public void containerTick() {
		super.containerTick();
		// l'impression n'est possible qu'avec un carton vierge en entrée, la sortie libre et les rôles remplis
		var t = menu.table;
		Generateur.Dessin d = dessin();
		boolean ok = t.getItem(Carreleur.ENTREE).is(Motif.CARTON.get()) && t.getItem(Carreleur.SORTIE).isEmpty()
			&& !t.getItem(Carreleur.ROLES).isEmpty() && !t.getItem(Carreleur.ROLES + 1).isEmpty()
			&& (!d.accent || !t.getItem(Carreleur.ROLES + 2).isEmpty()) && (!bord || !t.getItem(Carreleur.ROLES + 3).isEmpty());
		imprimer.active = ok;
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		int o = menu.onglet();
		g.blit(o == 0 ? FOND : FOND_RANGEMENT, leftPos, topPos, 0, 0, imageWidth, imageHeight, 512, 512);
		// onglets : l'actif est plus haut et relié au panneau
		for (int i = 0; i < 4; i++) {
			boolean actif = i == o;
			g.blit(ONGLETS, leftPos + 6 + i * 28, topPos + (actif ? 2 : 5), i * 26, actif ? 0 : 24, 26, actif ? 24 : 21, 128, 64);
		}
		if (o == 0) {
			// liste des motifs du type choisi
			List<Generateur.Dessin> l = Generateur.PAR_TYPE.get(type);
			defil = Math.max(0, Math.min(defil, l.size() - LIGNES));
			for (int i = defil; i < Math.min(l.size(), defil + LIGNES); i++) {
				int y = topPos + 53 + (i - defil) * 12;
				if (i == choix) g.fill(leftPos + 9, y, leftPos + 85, y + 12, 0xFF5A3C28);
				else if (mx >= leftPos + 9 && mx < leftPos + 85 && my >= y && my < y + 12) g.fill(leftPos + 9, y, leftPos + 85, y + 12, 0xFF2E3240);
				g.drawString(font, Component.translatable(l.get(i).cle()), leftPos + 11, y + 2, i == choix ? OR : BLANC, false);
			}
			// barre de défilement fine, à droite de la liste, quand il y a plus de 8 motifs
			if (l.size() > LIGNES) {
				int h = 96 * LIGNES / l.size(), y = topPos + 53 + (96 - h) * defil / (l.size() - LIGNES);
				g.fill(leftPos + 83, topPos + 53, leftPos + 85, topPos + 149, 0xFF2A2E37);
				g.fill(leftPos + 83, y, leftPos + 85, y + h, OR);
			}
			apercu(g, leftPos + 92, topPos + 32);
			// cases des rôles visibles
			int k = 0;
			for (Role role : roles()) { if (role != null) g.blit(FOND, leftPos + 240, topPos + 31 + k * 22, 300, 0, 18, 18, 512, 512); k++; }
		}
	}
	private record Role(int i) {}
	private Role[] roles() {
		Generateur.Dessin d = dessin();
		return new Role[] {new Role(0), new Role(1), d.accent ? new Role(2) : (bord ? new Role(3) : null), d.accent && bord ? new Role(3) : null};
	}

	/** Aperçu vu de dessus (ou de face pour un mur) d'une zone 16 x 16, avec les blocs des rôles. */
	private void apercu(GuiGraphics g, int x, int y) {
		Generateur.Dessin d = dessin();
		int[][] t = Generateur.tuile(d, reglage);
		int h = t.length, w = t[0].length, n = 16, c = 6, bl = bord ? bordL : 0;
		boolean mur = type == Generateur.MUR;
		var br = Minecraft.getInstance().getBlockRenderer();
		int[] teintes = {0xFFD8D4CC, 0xFF3A3840, 0xFFC99B52, 0xFFE1BA6E};
		for (int r = 0; r < n; r++)
			for (int col = 0; col < n; col++) {
				int v = mur ? n - 1 - r : r, role;
				boolean auBord = bl > 0 && (col < bl || col >= n - bl || v < bl || v >= n - bl);
				if (auBord) role = 3;
				else if (d.uniqueV()) role = (v - bl) < h ? t[v - bl][Math.floorMod(col - bl, w)] : 0;   // soubassement, frise : une seule fois en bas
				else role = t[Math.floorMod(v - bl, h)][Math.floorMod(col - bl, w)];
				if (role == 2 && !d.accent) role = 0;
				ItemStack s = menu.table.getItem(Carreleur.ROLES + role);
				BlockState st = Carreleur.etatDe(s);
				int px = x + col * c, py = y + r * c;
				if (st == null) { g.fill(px, py, px + c, py + c, teintes[role]); continue; }
				TextureAtlasSprite sp = br.getBlockModel(st).getParticleIcon();
				g.blit(px, py, 0, c, c, sp);
			}
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		g.drawString(font, title, 186, 9, OR, true);
		int o = menu.onglet();
		if (o > 0) { g.drawString(font, Component.translatable(TITRES[o - 1]), 8, 31, OR, true); return; }
		Generateur.Dessin d = dessin();
		String[] noms = {"airain.carreleur.role_a", "airain.carreleur.role_b", "airain.carreleur.role_accent", "airain.carreleur.role_bord"};
		int k = 0;
		for (Role r : roles()) { if (r != null) g.drawString(font, Component.translatable(noms[r.i()]), 196, 36 + k * 22, BLANC, false); k++; }
		g.drawString(font, Component.translatable("airain.carreleur.nom"), 8, 157, GRIS, false);
		if (d.reglage == Generateur.Reglage.CASE) {
			g.drawString(font, Component.translatable(d == Generateur.Dessin.GRID ? "airain.carreleur.ecart" : "airain.carreleur.case"), 90, 142, BLANC, false);
			// chiffre centré entre « − » (132-152) et « + » (166-186)
			String v = String.valueOf(reglage);
			g.drawString(font, v, 159 - font.width(v) / 2, 142, OR, true);
		} else {
			g.drawString(font, Component.translatable("airain.carreleur.taille"), 90, 136, BLANC, false);
			// valeur calée à droite sur le bord du curseur, pour ne jamais toucher l'intitulé
			String v = reglage + " × " + reglage;
			g.drawString(font, v, 190 - font.width(v), 136, OR, true);
		}
		if (bord) g.drawString(font, String.valueOf(bordL), 175, 174, OR, true);
		g.drawString(font, "→", 228, 127, OR, true);
	}

	@Override
	public boolean mouseClicked(double mx, double my, int bt) {
		for (int i = 0; i < 4; i++) {
			int x = leftPos + 6 + i * 28, y = topPos + 2;
			if (mx >= x && mx < x + 26 && my >= y && my < y + 24 && menu.onglet() != i) {
				menu.clickMenuButton(Minecraft.getInstance().player, i);
				Minecraft.getInstance().gameMode.handleInventoryButtonClick(menu.containerId, i);
				maj();
				return true;
			}
		}
		// curseur saisi : on suit la souris jusqu'au relâchement
		if (curseur.visible && curseur.isMouseOver(mx, my)) glisse = true;
		if (menu.onglet() == 0) {
			List<Generateur.Dessin> l = Generateur.PAR_TYPE.get(type);
			for (int i = defil; i < Math.min(l.size(), defil + LIGNES); i++) {
				int y = topPos + 53 + (i - defil) * 12;
				if (mx >= leftPos + 9 && mx < leftPos + 83 && my >= y && my < y + 12) { choix = i; reglage = dessin().defaut; maj(); return true; }
			}
		}
		return super.mouseClicked(mx, my, bt);
	}

	@Override
	public boolean mouseDragged(double mx, double my, int bt, double dx, double dy) {
		// AbstractContainerScreen garde le glisser pour les cases : on le passe au curseur
		if (glisse && curseur.visible) return curseur.mouseDragged(mx, my, bt, dx, dy);
		return super.mouseDragged(mx, my, bt, dx, dy);
	}

	@Override
	public boolean mouseReleased(double mx, double my, int bt) {
		if (glisse) { glisse = false; curseur.onRelease(mx, my); return true; }
		return super.mouseReleased(mx, my, bt);
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		// molette sur la liste : défilement des motifs
		if (menu.onglet() == 0 && mx >= leftPos + 8 && mx < leftPos + 86 && my >= topPos + 52 && my < topPos + 152) {
			int n = Generateur.PAR_TYPE.get(type).size();
			defil = Math.max(0, Math.min(n - LIGNES, defil - (int) Math.signum(sy)));
			return true;
		}
		return super.mouseScrolled(mx, my, sx, sy);
	}

	@Override
	public boolean keyPressed(int k, int sc, int mod) {
		// le champ du nom garde les touches (sinon « E » fermerait l'écran)
		if (champNom.isFocused() && champNom.visible && k != 256) { champNom.keyPressed(k, sc, mod); return true; }
		return super.keyPressed(k, sc, mod);
	}

	/** Curseur de la taille du motif (motifs complexes). */
	private class Curseur extends AbstractSliderButton {
		Curseur(int x, int y, int w) { super(x, y, w, 20, Component.empty(), 0); }
		void caler() { Generateur.Dessin d = dessin(); value = (reglage - d.min) / (double) Math.max(1, d.max - d.min); updateMessage(); }
		@Override protected void updateMessage() { setMessage(Component.empty()); }
		@Override protected void applyValue() { Generateur.Dessin d = dessin(); reglage = d.min + (int) Math.round(value * (d.max - d.min)); }
	}
}
