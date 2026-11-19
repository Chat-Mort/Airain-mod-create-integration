package fr.chatmort.airain.affichage;

import fr.chatmort.airain.gui.InterfaceHD;
import fr.chatmort.airain.gui.PanneauHD;
import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.client.gui.components.Button;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.world.item.DyeColor;
import net.neoforged.neoforge.network.PacketDistributor;

import java.util.ArrayList;
import java.util.List;

/**
 * 1.60 : le menu du tableau émaillé, en cinq onglets (Contenu, Style, Police, Lumière, Pose), avec l'aperçu à droite.
 * Chaque changement part au serveur (le tableau change sous vos yeux) ; tout est dessiné ici, les clics sont des zones.
 */
public class EmailScreen extends Screen {
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, VERT = 0x286428, CLAIR = 0xFAECC8;
	private static final int L_CLAIR = 0xFFFAE2A0, L_MOY = 0xFFD6AA5A, L_FONCE = 0xFF966830, L_OMBRE = 0xFF603E1E;
	private static final String[] ONGLETS = {"contenu", "style", "police", "lumiere", "pose", "liaisons"};
	private static final int VISIBLES = 7;
	private final BlockPos pos;
	private final Reglages r;
	private int onglet, choisie, defile;
	private boolean arriere, sale;
	private int attente;
	private EditBox champ;
	private record Zone(int x0, int y0, int x1, int y1, Runnable action) {}
	private final List<Zone> zones = new ArrayList<>();

	public EmailScreen(BlockPos pos, Reglages r) {
		super(Component.translatable("block.airain.enamel_board"));
		this.pos = pos; this.r = r;
	}
	private int ox() { return width / 2 - 160; }
	private int oy() { return height / 2 - 118; }
	private List<Reglages.Ligne> lignes() { return r.face(arriere && !r.memeFace); }
	private Reglages.Ligne ligne() { List<Reglages.Ligne> l = lignes(); return choisie < l.size() ? l.get(choisie) : null; }
	private void change() { sale = true; }

	@Override
	protected void init() {
		champ = null;
		if (InterfaceHD.actif()) { initHD(); return; }
		if (onglet == 0) {
			champ = new EditBox(font, ox() + 55, oy() + 177, 158, 10, Component.empty());
			champ.setBordered(false); champ.setTextColor(CLAIR); champ.setMaxLength(Reglages.MAX_TEXTE);
			Reglages.Ligne l = ligne();
			champ.setValue(l == null ? "" : l.texte);
			champ.setResponder(v -> { Reglages.Ligne x = ligne(); if (x != null && !x.texte.equals(v)) { x.texte = v; change(); } });
			addRenderableWidget(champ);
		}
	}
	/** Interface HD : champ « Texte » dans son creux, bouton à chaîne « Terminé » sous le bac. */
	private void initHD() {
		if (onglet == 0) {
			champ = new EditBox(font, ox() + 60, oy() + 140, 142, 10, Component.empty());
			champ.setBordered(false); champ.setTextColor(0xE8E2D4); champ.setMaxLength(Reglages.MAX_TEXTE);
			Reglages.Ligne l = ligne();
			champ.setValue(l == null ? "" : l.texte);
			champ.setResponder(v -> { Reglages.Ligne x = ligne(); if (x != null && !x.texte.equals(v)) { x.texte = v; change(); } });
			addRenderableWidget(champ);
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> onClose()).bounds(ox() + 10, oy() + 196, PanneauHD.BOUTON, 20).build());
	}
	private int visibles() { return InterfaceHD.actif() ? 5 : VISIBLES; }
	private void choisir(int i) { choisie = i; rebuildWidgets(); }

	@Override
	public void tick() {
		if (sale && ++attente >= 4) envoyer();
	}
	private void envoyer() { sale = false; attente = 0; PacketDistributor.sendToServer(new PaquetEmail(pos, r.ecrire())); }
	@Override public void onClose() { if (sale) envoyer(); super.onClose(); }
	@Override public boolean isPauseScreen() { return false; }

	// ---------------------------------------------------------------- petits outils de dessin
	private Component tr(String k, Object... a) { return Component.translatable("airain.email." + k, a); }
	private void zone(int x, int y, int w, int h, Runnable a) { zones.add(new Zone(x, y, x + w, y + h, a)); }
	private void texte(GuiGraphics g, Component c, int x, int y, int col) { g.drawString(font, c, x, y, col, false); }
	private void bouton(GuiGraphics g, int x, int y, int w, int h, Component t, boolean actif, Runnable a) {
		g.fill(x, y, x + w, y + h, L_OMBRE);
		g.fill(x, y, x + w - 1, y + h - 1, actif ? L_FONCE : L_CLAIR);
		g.fill(x + 1, y + 1, x + w - 1, y + h - 1, actif ? L_FONCE : L_MOY);
		if (actif) g.fill(x + 1, y + 1, x + w - 1, y + 2, L_OMBRE);
		if (t != null) g.drawString(font, t, x + (w - font.width(t)) / 2, y + (h - 8) / 2 + (actif ? 1 : 0), actif ? CLAIR : ENCRE, false);
		zone(x, y, w, h, a);
	}
	private void bouton(GuiGraphics g, int x, int y, int w, int h, String t, boolean actif, Runnable a) { bouton(g, x, y, w, h, Component.literal(t), actif, a); }
	private void radio(GuiGraphics g, int x, int y, boolean on, Component t, Runnable a) {
		g.fill(x + 1, y, x + 8, y + 9, L_OMBRE); g.fill(x, y + 1, x + 9, y + 8, L_OMBRE);
		g.fill(x + 1, y + 1, x + 8, y + 8, L_CLAIR);
		if (on) g.fill(x + 2, y + 2, x + 7, y + 7, 0xFF000000 | ROUGE);
		texte(g, t, x + 12, y + 1, ENCRE);
		zone(x, y - 1, 12 + font.width(t), 11, a);
	}
	private void caseC(GuiGraphics g, int x, int y, boolean on, Component t, Runnable a) {
		g.fill(x, y, x + 9, y + 9, L_OMBRE); g.fill(x + 1, y + 1, x + 8, y + 8, L_CLAIR);
		if (on) { g.fill(x + 2, y + 4, x + 4, y + 7, 0xFF000000 | ROUGE); g.fill(x + 4, y + 5, x + 6, y + 7, 0xFF000000 | ROUGE); g.fill(x + 6, y + 2, x + 8, y + 5, 0xFF000000 | ROUGE); }
		texte(g, t, x + 12, y + 1, ENCRE);
		zone(x, y - 1, 12 + font.width(t), 11, a);
	}
	private void pastille(GuiGraphics g, int x, int y, int col, boolean sel, Runnable a) {
		if (sel) g.fill(x - 2, y - 2, x + 12, y + 12, 0xFF000000 | ROUGE);
		g.fill(x, y, x + 10, y + 10, L_OMBRE); g.fill(x + 1, y + 1, x + 9, y + 9, 0xFF000000 | col);
		zone(x - 1, y - 1, 12, 12, a);
	}
	private void section(GuiGraphics g, Component t, int x, int y) {
		g.drawString(font, t.copy().withStyle(s -> s.withBold(true)), x, y, ROUGE, false);
		g.fill(x, y + 10, x + 202, y + 11, L_FONCE);
	}
	private void champCreux(GuiGraphics g, int x, int y, int w) { WidgetsEmpire.creux(g, x, y, w, 12); }

	// ---------------------------------------------------------------- dessin
	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		g.blit(WidgetsEmpire.PANNEAU, ox(), oy(), 0, 0, 310, 226, 512, 256);
	}
	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		zones.clear();
		if (InterfaceHD.actif()) { renderHD(g, mx, my, pt); return; }
		renderBackground(g, mx, my, pt);
		int x = ox(), y = oy();
		g.drawString(font, title.copy().withStyle(s -> s.withBold(true)), x + 14, y + 6, ENCRE, false);
		int tx = x + 10;
		for (int k = 0; k < ONGLETS.length; k++) {
			Component n = tr("onglet." + ONGLETS[k]); int w = font.width(n) + 8; final int kk = k;
			bouton(g, tx, y + 22, w, 14, n, k == onglet, () -> { onglet = kk; rebuildWidgets(); });
			tx += w + 2;
		}
		switch (onglet) { case 0 -> contenu(g, x, y); case 1 -> style(g, x, y); case 2 -> police(g, x, y); case 3 -> lumiere(g, x, y); case 5 -> liaisonsHD(g); default -> pose(g, x, y); }
		apercu(g, x, y);
		bouton(g, x + 226, y + 196, 74, 16, Component.translatable("gui.done"), false, this::onClose);
		for (var w : renderables) w.render(g, mx, my, pt);
	}

	// ---- 1. contenu
	private void contenu(GuiGraphics g, int x, int y) {
		List<Reglages.Ligne> L = lignes();
		section(g, tr(r.memeFace ? "lignes" : arriere ? "lignes_arriere" : "lignes_avant"), x + 12, y + 42);
		defile = Math.max(0, Math.min(defile, Math.max(0, L.size() - visibles())));
		int base = arriere && !r.memeFace ? r.avant.size() : 0;
		for (int n = 0; n < visibles() && n + defile < L.size(); n++) {
			int i = n + defile, ly = y + 55 + n * 11;
			Reglages.Ligne l = L.get(i);
			boolean sel = i == choisie;
			if (sel) g.fill(x + 11, ly - 2, x + 215, ly + 9, 0xFFE8C478);
			texte(g, tr("type." + l.type), x + 14, ly, sel ? ENCRE : SEPIA);
			String t = l.texte.isEmpty() && l.type != Reglages.FILET && l.type != Reglages.COLONNE && l.type != Reglages.VIDE ? "…" : l.texte;
			g.drawString(font, font.plainSubstrByWidth(t, 120), x + 72, ly, ENCRE, false);
			if (!EmailClientEtat.valeur(pos, base + i).isEmpty()) g.fill(x + 206, ly + 2, x + 210, ly + 6, 0xFF000000 | VERT);
			final int ii = i;
			zone(x + 11, ly - 2, 204, 11, () -> choisir(ii));
		}
		int by = y + 55 + VISIBLES * 11 + 1;
		bouton(g, x + 12, by, 14, 12, "+", false, () -> {
			if (L.size() >= Reglages.MAX_LIGNES) return;
			L.add(Math.min(L.size(), choisie + 1), new Reglages.Ligne(Reglages.TEXTE, "", 0, 1, 0)); choisie = Math.min(L.size() - 1, choisie + 1); change(); rebuildWidgets();
		});
		bouton(g, x + 28, by, 14, 12, "−", false, () -> { if (L.size() > 1 && choisie < L.size()) { L.remove(choisie); choisie = Math.max(0, choisie - 1); change(); rebuildWidgets(); } });
		bouton(g, x + 44, by, 14, 12, "↑", false, () -> { if (choisie > 0) { L.add(choisie - 1, L.remove(choisie)); choisie--; change(); } });
		bouton(g, x + 60, by, 14, 12, "↓", false, () -> { if (choisie < L.size() - 1) { L.add(choisie + 1, L.remove(choisie)); choisie++; change(); } });
		if (L.size() > VISIBLES) {
			bouton(g, x + 186, by, 14, 12, "▲", false, () -> defile = Math.max(0, defile - 1));
			bouton(g, x + 202, by, 14, 12, "▼", false, () -> defile++);
		}
		Reglages.Ligne l = ligne();
		if (l == null) return;
		int sy = by + 15;
		section(g, tr("ligne", choisie + 1), x + 12, sy);
		int ry = sy + 13;
		texte(g, tr("type"), x + 14, ry + 2, ENCRE);
		bouton(g, x + 52, ry, 12, 12, "◀", false, () -> { l.type = Math.floorMod(l.type - 1, Reglages.NB_TYPES); defauts(l); change(); });
		Component nt = tr("type." + l.type);
		g.drawString(font, nt.copy().withStyle(s -> s.withBold(true)), x + 66 + (52 - font.width(nt)) / 2, ry + 2, ENCRE, false);
		bouton(g, x + 120, ry, 12, 12, "▶", false, () -> { l.type = Math.floorMod(l.type + 1, Reglages.NB_TYPES); defauts(l); change(); });
		texte(g, tr("taille"), x + 140, ry + 2, ENCRE);
		for (int k = 0; k < 3; k++) { final int kk = k; bouton(g, x + 170 + k * 15, ry, 14, 12, tr("taille." + k), l.taille == k, () -> { l.taille = kk; change(); }); }
		ry += 14;
		texte(g, tr("texte"), x + 14, ry + 2, ENCRE); champCreux(g, x + 52, ry, 162);
		ry += 14;
		texte(g, tr("aligner"), x + 14, ry + 2, ENCRE);
		for (int k = 0; k < 3; k++) { final int kk = k; bouton(g, x + 52 + k * 15, ry, 14, 12, tr("align." + k), l.align == k, () -> { l.align = kk; change(); }); }
		for (int k = 0; k < Reglages.PALETTE.length; k++) { final int kk = k; pastille(g, x + 104 + k * 14, ry + 1, Reglages.PALETTE[k], l.couleur == k, () -> { l.couleur = kk; change(); }); }
		ry += 14;
		String v = EmailClientEtat.valeur(pos, base + choisie);
		if (l.liee()) {
			texte(g, tr("liaison"), x + 14, ry + 1, ENCRE);
			g.drawString(font, v.isEmpty() ? tr("liaison.aucune") : Component.literal(font.plainSubstrByWidth(v, 150)), x + 52, ry + 1, v.isEmpty() ? SEPIA : VERT, false);
		}
	}
	/** Réglages qui vont bien quand on change le type d'une ligne. */
	private static void defauts(Reglages.Ligne l) {
		switch (l.type) {
			case Reglages.TITRE -> { l.align = 1; l.taille = 2; }
			case Reglages.SECTION -> { l.align = 0; l.taille = 1; l.couleur = 1; }
			default -> {}
		}
	}

	// ---- 2. style
	private void style(GuiGraphics g, int x, int y) {
		section(g, tr("email"), x + 12, y + 42);
		for (int i = 0; i < 16; i++) { final int ii = i; pastille(g, x + 14 + (i % 8) * 14, y + 56 + (i / 8) * 14, DyeColor.byId(i).getTextureDiffuseColor() & 0xFFFFFF, r.email == i, () -> { r.email = ii; change(); }); }
		texte(g, Component.translatable("color.minecraft." + DyeColor.byId(r.email).getName()), x + 134, y + 62, ENCRE);
		section(g, tr("cadre"), x + 12, y + 88);
		for (int i = 0; i < 4; i++) { final int ii = i; bouton(g, x + 12 + i * 51, y + 101, 49, 14, tr("cadre." + i), r.cadre == i, () -> { r.cadre = ii; change(); }); }
		section(g, tr("airain"), x + 12, y + 121);
		int[] teintes = {0xD6AA5A, 0xC2703E, 0xA83424, 0x900A1C};
		for (int i = 0; i < 4; i++) { final int ii = i; pastille(g, x + 14 + i * 51, y + 135, teintes[i], r.airain == i, () -> { r.airain = ii; change(); }); texte(g, tr("airain." + i), x + 27 + i * 51, y + 136, ENCRE); }
		section(g, tr("finition"), x + 12, y + 154);
		radio(g, x + 14, y + 168, !r.mat, tr("brillant"), () -> { r.mat = false; change(); });
		radio(g, x + 84, y + 168, r.mat, tr("mat"), () -> { r.mat = true; change(); });
		caseC(g, x + 14, y + 184, r.ecusson, tr("ecusson"), () -> { r.ecusson = !r.ecusson; change(); });
		caseC(g, x + 84, y + 184, r.rosaces, tr("rosaces"), () -> { r.rosaces = !r.rosaces; change(); });
		caseC(g, x + 150, y + 184, r.baguettes, tr("baguettes"), () -> { r.baguettes = !r.baguettes; change(); });
	}

	// ---- 3. police
	private void police(GuiGraphics g, int x, int y) {
		section(g, tr("police"), x + 12, y + 42);
		for (int i = 0; i < 3; i++) {
			final int ii = i; int ly = y + 58 + i * 26;
			radio(g, x + 14, ly, r.police == i, tr("police." + i), () -> { r.police = ii; change(); });
			g.fill(x + 96, ly - 5, x + 214, ly + 13, 0xFF000000 | EmailRendu.couleurEmail(r));
			MutableComponent ex = Component.literal("Lingots 1 284").withStyle(i == 1 ? net.minecraft.network.chat.Style.EMPTY.withFont(MiseEnPage.IMPERIALE) : net.minecraft.network.chat.Style.EMPTY);
			if (i == 2) {
				g.drawString(font, ex, x + 102, ly + 1, 0xFF000000 | EmailRendu.melange(EmailRendu.couleurEmail(r), 0xFFFFFF, 0.35f), false);
				g.drawString(font, ex, x + 102, ly, 0xFF000000 | EmailRendu.melange(EmailRendu.couleurEmail(r), 0, 0.6f), false);
			} else g.drawString(font, ex, x + 102, ly, 0xFF000000 | Reglages.PALETTE[0], false);
		}
		section(g, tr("couleurs"), x + 12, y + 138);
		texte(g, tr("couleur_lignes"), x + 14, y + 155, ENCRE);
		for (int k = 0; k < Reglages.PALETTE.length; k++) { final int kk = k; pastille(g, x + 98 + k * 14, y + 154, Reglages.PALETTE[k], false, () -> { for (Reglages.Ligne l : lignes()) l.couleur = kk; change(); }); }
		texte(g, tr("couleur_valeurs"), x + 14, y + 173, ENCRE);
		for (int k = 0; k < Reglages.PALETTE.length; k++) { final int kk = k; pastille(g, x + 98 + k * 14, y + 172, Reglages.PALETTE[k], r.coulValeur == k, () -> { r.coulValeur = kk; change(); }); }
	}

	// ---- 4. lumière
	private void lumiere(GuiGraphics g, int x, int y) {
		section(g, tr("eclairage"), x + 12, y + 42);
		int rx = x + 14;
		for (int i = 0; i < 3; i++) { final int ii = i; radio(g, rx, y + 56, r.eclairage == i, tr("eclairage." + i), () -> { r.eclairage = ii; change(); }); rx += font.width(tr("eclairage." + i)) + 22; }
		texte(g, tr("intensite"), x + 14, y + 74, ENCRE);
		int sx = x + 70, sw = 120;
		g.fill(sx, y + 77, sx + sw, y + 79, L_OMBRE); g.fill(sx, y + 77, sx + sw * r.intensite / 15, y + 79, L_CLAIR);
		int k = sx + sw * r.intensite / 15;
		g.fill(k - 3, y + 72, k + 3, y + 84, L_FONCE); g.fill(k - 2, y + 73, k + 2, y + 83, L_CLAIR);
		g.drawString(font, Component.literal("" + r.intensite).withStyle(s -> s.withBold(true)), x + 198, y + 74, ENCRE, false);
		zone(sx - 4, y + 70, sw + 8, 16, () -> {});
		section(g, tr("allumage"), x + 12, y + 92);
		radio(g, x + 14, y + 106, r.allumage == 0, tr("allumage.0"), () -> { r.allumage = 0; change(); });
		radio(g, x + 14 + font.width(tr("allumage.0")) + 22, y + 106, r.allumage == 1, tr("allumage.1"), () -> { r.allumage = 1; change(); });
		radio(g, x + 14, y + 120, r.allumage == 2, tr("allumage.2"), () -> { r.allumage = 2; change(); });
		section(g, tr("alerte"), x + 12, y + 138);
		texte(g, tr("alerte.si"), x + 14, y + 154, ENCRE);
		int ax = x + 14 + font.width(tr("alerte.si")) + 4;
		bouton(g, ax, y + 152, 12, 12, "◀", false, () -> { r.alerteLigne = Math.max(0, r.alerteLigne - 1); change(); });
		champCreux(g, ax + 14, y + 152, 22);
		g.drawString(font, r.alerteLigne == 0 ? Component.literal("—") : Component.literal("" + r.alerteLigne), ax + 18, y + 154, CLAIR, false);
		bouton(g, ax + 38, y + 152, 12, 12, "▶", false, () -> { r.alerteLigne = Math.min(Reglages.MAX_LIGNES, r.alerteLigne + 1); change(); });
		int bx = ax + 54;
		texte(g, tr("alerte.depasse"), bx, y + 154, ENCRE); bx += font.width(tr("alerte.depasse")) + 4;
		bouton(g, bx, y + 152, 12, 12, "◀", false, () -> { r.seuil -= hasShiftDown() ? 10 : 1; change(); });
		champCreux(g, bx + 14, y + 152, 30);
		g.drawString(font, "" + r.seuil, bx + 17, y + 154, CLAIR, false);
		bouton(g, bx + 46, y + 152, 12, 12, "▶", false, () -> { r.seuil += hasShiftDown() ? 10 : 1; change(); });
		texte(g, tr("alerte.alors"), x + 14, y + 173, ENCRE);
		int cx = x + 14 + font.width(tr("alerte.alors")) + 4;
		for (int i = 0; i < 2; i++) { final int ii = i; Component n = tr("alerte.action." + i); int w = font.width(n) + 10; bouton(g, cx, y + 170, w, 14, n, r.alerteAction == i, () -> { r.alerteAction = ii; change(); }); cx += w + 3; }
		for (int i = 0; i < Reglages.PALETTE.length && cx + i * 13 < x + 214; i++) { final int ii = i; pastille(g, cx + 4 + i * 13, y + 172, Reglages.PALETTE[i], r.alerteCouleur == i, () -> { r.alerteCouleur = ii; change(); }); }
	}
	@Override
	public boolean mouseDragged(double mx, double my, int b, double dx, double dy) {
		if (onglet == 3 && surCurseur(mx, my)) { curseur(mx); return true; }
		return super.mouseDragged(mx, my, b, dx, dy);
	}
	/** Zone du curseur d'intensité (interface HD : curseur du kit de 140 px en (64, 68)). */
	private boolean surCurseur(double mx, double my) {
		if (InterfaceHD.actif()) return my >= oy() + 68 && my <= oy() + 88 && mx >= ox() + 64 && mx <= ox() + 204;
		return my >= oy() + 70 && my <= oy() + 86 && mx >= ox() + 66 && mx <= ox() + 194;
	}
	private void curseur(double mx) {
		int v = InterfaceHD.actif() ? (int) Math.round((mx - (ox() + 68)) * 15 / 132.0) : (int) Math.round((mx - (ox() + 70)) * 15 / 120.0);
		v = Math.max(0, Math.min(15, v));
		if (v != r.intensite) { r.intensite = v; change(); }
	}

	// ---- 5. pose
	private void pose(GuiGraphics g, int x, int y) {
		section(g, tr("accrochage"), x + 12, y + 42);
		for (int i = 0; i < 4; i++) { final int ii = i; radio(g, x + 14 + (i % 2) * 100, y + 56 + (i / 2) * 14, r.accrochage == i, tr("accrochage." + i), () -> { r.accrochage = ii; change(); }); }
		var mc = net.minecraft.client.Minecraft.getInstance();
		if (mc.level != null && mc.level.getBlockState(pos).getBlock() instanceof EmailBlock)
			texte(g, tr("ici", tr("montage." + mc.level.getBlockState(pos).getValue(EmailBlock.MONTAGE).ordinal())), x + 14, y + 88, VERT);
		section(g, tr("double"), x + 12, y + 104);
		radio(g, x + 14, y + 118, r.memeFace, tr("double.meme"), () -> { r.memeFace = true; arriere = false; change(); });
		radio(g, x + 114, y + 118, !r.memeFace, tr("double.different"), () -> {
			if (r.memeFace && r.arriere.isEmpty()) for (Reglages.Ligne l : r.avant) r.arriere.add(l.copie());
			r.memeFace = false; change();
		});
		if (!r.memeFace) {
			texte(g, tr("editer"), x + 14, y + 136, ENCRE);
			int ex = x + 14 + font.width(tr("editer")) + 6;
			Component a = tr("face.avant"), b = tr("face.arriere");
			bouton(g, ex, y + 133, font.width(a) + 10, 14, a, !arriere, () -> { arriere = false; choisie = 0; });
			bouton(g, ex + font.width(a) + 13, y + 133, font.width(b) + 10, 14, b, arriere, () -> { arriere = true; choisie = 0; });
		}
		section(g, tr("copier"), x + 12, y + 156);
		int ly = y + 170;
		for (String s : tr("copier.aide").getString().split("\n")) { g.drawString(font, s, x + 14, ly, SEPIA, false); ly += 10; }
	}

	// ================================================================ interface HD
	// Panneau de réglages commun : bac, onglets de classeur, libellés à points de conduite, touches et pastilles serties.
	// Coordonnées des maquettes validées, relatives au coin du panneau (ox, oy).
	private static final ResourceLocation SPR_PISTE = ResourceLocation.withDefaultNamespace("widget/slider"),
		SPR_POIGNEE = ResourceLocation.withDefaultNamespace("widget/slider_handle"),
		SPR_RAIL = ResourceLocation.withDefaultNamespace("widget/scroller_background"),
		SPR_CHARIOT = ResourceLocation.withDefaultNamespace("widget/scroller");
	private static final int HD_TEXTE = 0xC8C2B4, HD_CREME = 0xFFE9B0, HD_VERT = 0x78C878;
	private int sx, sy;      // souris, pour les survols

	private boolean sous(int x, int y, int w, int h) { return sx >= x && sx < x + w && sy >= y && sy < y + h; }
	private void hdTexte(GuiGraphics g, Component c, int px, int py, int col) { g.drawString(font, c, ox() + px, oy() + py, col, true); }
	private void hdSection(GuiGraphics g, Component c, int py) { PanneauHD.libelle(g, font, ox() + 14, oy() + py, ox() + 207, c); }
	private void hdPuce(GuiGraphics g, Component c, int py) { PanneauHD.libelle(g, font, ox() + 14, oy() + py, ox() + 14, c); }
	private void hdTouche(GuiGraphics g, int px, int py, int w, boolean actif, Component t, Runnable a) {
		int x = ox() + px, y = oy() + py;
		PanneauHD.toucheTexte(g, font, x, y, w, actif, sous(x, y, w, 16), t);
		zone(x, y, w, 16, a);
	}
	private void hdRadio(GuiGraphics g, int px, int py, boolean on, Component t, Runnable a) {
		int x = ox() + px, y = oy() + py, w = 14 + font.width(t);
		PanneauHD.radio(g, x, y, on, sous(x, y - 1, w, 13));
		g.drawString(font, t, x + 14, y + 2, on ? InterfaceHD.AIRAIN : HD_TEXTE, true);
		zone(x, y - 1, w, 13, a);
	}
	private void hdCase(GuiGraphics g, int px, int py, boolean on, Component t, Runnable a) {
		int x = ox() + px, y = oy() + py;
		PanneauHD.caseACocher(g, x, y, on);
		g.drawString(font, t, x + 14, y + 2, on ? InterfaceHD.AIRAIN : HD_TEXTE, true);
		zone(x, y - 1, 14 + font.width(t), 13, a);
	}
	private void hdEmail(GuiGraphics g, int px, int py, int col, boolean sel, Runnable a) {
		PanneauHD.email(g, ox() + px, oy() + py, col, sel);
		zone(ox() + px - 1, oy() + py - 1, 12, 12, a);
	}
	private void hdFleche(GuiGraphics g, int px, int py, boolean droite, Runnable a) {
		int x = ox() + px, y = oy() + py;
		PanneauHD.fleche(g, x, y, droite, sous(x, y, 16, 16));
		zone(x, y, 16, 16, a);
	}
	private void hdValeur(GuiGraphics g, int px, int py, int w, Component t) {
		PanneauHD.champ(g, ox() + px, oy() + py, w, false);
		g.drawString(font, t, ox() + px + w / 2 - font.width(t) / 2 + 1, oy() + py + 4, HD_CREME, true);
	}

	private void renderHD(GuiGraphics g, int mx, int my, float pt) {
		sx = mx; sy = my;
		super.renderBackground(g, mx, my, pt);
		int x = ox(), y = oy();
		PanneauHD.fond(g, x + 10, y + 10);
		g.drawString(font, title, x + 12, y + 6, InterfaceHD.AIRAIN, true);
		// onglets de classeur : de droite à gauche, l'actif en dernier (devant)
		Component[] noms = new Component[ONGLETS.length];
		for (int k = 0; k < ONGLETS.length; k++) noms[k] = tr("onglet." + ONGLETS[k]);
		int[] xs = PanneauHD.placeOnglets(font, noms, x + 10);
		for (int k = ONGLETS.length - 1; k >= -1; k--) {
			int c = k < 0 ? onglet : k;
			if (k >= 0 && k == onglet) continue;
			final int cc = c;
			PanneauHD.onglet(g, font, xs[c], y + 18, xs[ONGLETS.length + c], noms[c], c == onglet, c != onglet && sous(xs[c], y + 18, xs[ONGLETS.length + c], 16));
			zone(xs[c], y + 18, xs[ONGLETS.length + c], 16, () -> { onglet = cc; rebuildWidgets(); });
		}
		if (onglet == 0) PanneauHD.champ(g, x + 56, y + 136, 150, champ != null && champ.isFocused());
		switch (onglet) { case 0 -> contenuHD(g); case 1 -> styleHD(g); case 2 -> policeHD(g); case 3 -> lumiereHD(g); case 5 -> liaisonsHD(g); default -> poseHD(g); }
		apercu(g, x, y);
		PanneauHD.reflets(g, x + 10, y + 10);
		for (var w : renderables) w.render(g, mx, my, pt);
	}

	// ---- 1. contenu : liste de 5 lignes, boutons ronds sur la ligne du titre, réglages de la ligne choisie sous une rainure
	private void contenuHD(GuiGraphics g) {
		int x = ox(), y = oy();
		List<Reglages.Ligne> L = lignes();
		PanneauHD.libelle(g, font, x + 14, y + 38, x + 136, tr(r.memeFace ? "lignes" : arriere ? "lignes_arriere" : "lignes_avant"));
		Runnable[] actions = {
			() -> { if (L.size() >= Reglages.MAX_LIGNES) return;
				L.add(Math.min(L.size(), choisie + 1), new Reglages.Ligne(Reglages.TEXTE, "", 0, 1, 0)); choisie = Math.min(L.size() - 1, choisie + 1); change(); rebuildWidgets(); },
			() -> { if (L.size() > 1 && choisie < L.size()) { L.remove(choisie); choisie = Math.max(0, choisie - 1); change(); rebuildWidgets(); } },
			() -> { if (choisie > 0) { L.add(choisie - 1, L.remove(choisie)); choisie--; change(); } },
			() -> { if (choisie < L.size() - 1) { L.add(choisie + 1, L.remove(choisie)); choisie++; change(); } }};
		for (int k = 0; k < 4; k++) {
			int bx = x + 138 + k * 17, by = y + 38;
			PanneauHD.rond(g, bx, by, k, sous(bx, by, 16, 16));
			zone(bx, by, 16, 16, actions[k]);
		}
		// liste : creux sombre, ligne choisie en bande cramoisie, une ligne sur deux plus sombre
		int lx0 = x + 13, ly0 = y + 57, lx1 = x + 199, ly1 = y + 112;
		g.fill(lx0 - 1, ly0 - 1, lx1 + 1, ly1 + 1, 0xFF704425);
		g.fill(lx0, ly0, lx1, ly1, 0xFF15171B);
		defile = Math.max(0, Math.min(defile, Math.max(0, L.size() - visibles())));
		int base = arriere && !r.memeFace ? r.avant.size() : 0;
		for (int n = 0; n < visibles() && n + defile < L.size(); n++) {
			int i = n + defile, ly = ly0 + n * 11;
			Reglages.Ligne l = L.get(i);
			boolean sel = i == choisie;
			if (sel) { g.fill(lx0, ly, lx1, ly + 11, 0xFF820019); g.fill(lx0, ly, lx1, ly + 1, 0xFFAF1D25); g.fill(lx0, ly + 10, lx1, ly + 11, 0xFF520019); }
			else if (n % 2 == 1) g.fill(lx0, ly, lx1, ly + 11, 0xFF1A1C21);
			g.drawString(font, tr("type." + l.type), lx0 + 4, ly + 2, sel ? InterfaceHD.AIRAIN : 0xB48242, true);
			String t = l.texte.isEmpty() && l.type != Reglages.FILET && l.type != Reglages.COLONNE && l.type != Reglages.VIDE ? "-" : l.texte;
			g.drawString(font, font.plainSubstrByWidth(t, 120), lx0 + 44, ly + 2, sel ? HD_CREME : 0xD8D2C4, true);
			if (!EmailClientEtat.valeur(pos, base + i).isEmpty()) PanneauHD.lampe(g, lx1 - 9, ly + 2);
			final int ii = i;
			zone(lx0, ly, lx1 - lx0, 11, () -> choisir(ii));
		}
		// rail de défilement à droite de la liste
		g.blitSprite(SPR_RAIL, x + 201, ly0, 6, ly1 - ly0);
		int total = Math.max(1, L.size()), h = Math.max(8, (ly1 - ly0) * Math.min(visibles(), total) / total);
		int course = ly1 - ly0 - h, pos0 = total > visibles() ? course * defile / (total - visibles()) : 0;
		g.blitSprite(SPR_CHARIOT, x + 201, ly0 + pos0, 6, h);
		PanneauHD.rainure(g, x + 13, x + 207, y + 114);
		Reglages.Ligne l = ligne();
		if (l == null) return;
		// type : flèches et cartouche, comme le panneau commun
		PanneauHD.libelle(g, font, x + 14, y + 118, x + 89, tr("type"));
		hdFleche(g, 89, 118, false, () -> { l.type = Math.floorMod(l.type - 1, Reglages.NB_TYPES); defauts(l); change(); });
		PanneauHD.cartouche(g, font, x + 107, y + 118, 80, tr("type." + l.type), false);
		hdFleche(g, 189, 118, true, () -> { l.type = Math.floorMod(l.type + 1, Reglages.NB_TYPES); defauts(l); change(); });
		hdPuce(g, tr("texte"), 136);
		// alignement (traits dessinés) et taille
		hdPuce(g, tr("aligner"), 154);
		for (int k = 0; k < 3; k++) {
			final int kk = k; int bx = x + 66 + k * 17, by = y + 154;
			hdTouche(g, 66 + k * 17, 154, 16, l.align == k, null, () -> { l.align = kk; change(); });
			int c = l.align == k ? 0xFFFFE9B0 : 0xFFE1BA6E;
			for (int t = 0; t < 4; t++) {
				int L_ = t % 2 == 0 ? 10 : 6, x0 = k == 0 ? 3 : k == 1 ? 3 + (10 - L_) / 2 : 13 - L_;
				g.fill(bx + x0, by + 4 + t * 2, bx + x0 + L_, by + 5 + t * 2, c);
			}
		}
		hdTexte(g, tr("taille"), 126, 158, InterfaceHD.AIRAIN_SOMBRE);
		for (int k = 0; k < 3; k++) { final int kk = k; hdTouche(g, 155 + k * 17, 154, 16, l.taille == k, tr("taille." + k), () -> { l.taille = kk; change(); }); }
		// couleur, puis la liaison (lampe verte et valeur lue)
		hdPuce(g, Component.translatable("airain.email.couleur"), 171);
		for (int k = 0; k < Reglages.PALETTE.length; k++) { final int kk = k; hdEmail(g, 66 + k * 11, 173, Reglages.PALETTE[k], l.couleur == k, () -> { l.couleur = kk; change(); }); }
		if (l.liee()) {
			String v = EmailClientEtat.valeur(pos, base + choisie);
			if (!v.isEmpty()) PanneauHD.lampe(g, x + 160, y + 175);
			g.drawString(font, v.isEmpty() ? Component.literal("-") : Component.literal(font.plainSubstrByWidth(v, 36)), x + 167, y + 175, v.isEmpty() ? HD_TEXTE : HD_VERT, true);
		}
	}

	// ---- 2. style : émail, cadre (et teinte de l'airain dessous), finition
	private void styleHD(GuiGraphics g) {
		hdSection(g, tr("email"), 38);
		for (int i = 0; i < 16; i++) { final int ii = i; hdEmail(g, 16 + (i % 8) * 12, 53 + (i / 8) * 12, DyeColor.byId(i).getTextureDiffuseColor() & 0xFFFFFF, r.email == i, () -> { r.email = ii; change(); }); }
		hdTexte(g, Component.translatable("color.minecraft." + DyeColor.byId(r.email).getName()), 118, 59, 0xD8D2C4);
		hdSection(g, tr("cadre"), 83);
		for (int i = 0; i < 4; i++) { final int ii = i; hdTouche(g, 15 + i * 48, 98, 46, r.cadre == i, tr("cadre." + i), () -> { r.cadre = ii; change(); }); }
		int[] teintes = {0xD6AA5A, 0xC2703E, 0xA83424, 0x900A1C};
		// teintes de l'airain : pastille + nom, réparties sur la largeur du bac selon la longueur des noms (rien ne se chevauche)
		int somme = 0;
		for (int i = 0; i < 4; i++) somme += 13 + font.width(tr("airain." + i));
		float ecart = Math.max(4, (187 - somme) / 3f), tx = 16;
		for (int i = 0; i < 4; i++) {
			final int ii = i; int xi = Math.round(tx);
			hdEmail(g, xi, 120, teintes[i], r.airain == i, () -> { r.airain = ii; change(); });
			hdTexte(g, tr("airain." + i), xi + 13, 121, r.airain == i ? InterfaceHD.AIRAIN : HD_TEXTE);
			tx += 13 + font.width(tr("airain." + i)) + ecart;
		}
		hdSection(g, tr("finition"), 138);
		hdRadio(g, 16, 153, !r.mat, tr("brillant"), () -> { r.mat = false; change(); });
		hdRadio(g, 80, 153, r.mat, tr("mat"), () -> { r.mat = true; change(); });
		hdCase(g, 16, 168, r.ecusson, tr("ecusson"), () -> { r.ecusson = !r.ecusson; change(); });
		hdCase(g, 80, 168, r.rosaces, tr("rosaces"), () -> { r.rosaces = !r.rosaces; change(); });
		hdCase(g, 144, 168, r.baguettes, tr("baguettes"), () -> { r.baguettes = !r.baguettes; change(); });
	}

	// ---- 3. police : trois exemples sur l'émail choisi, couleurs
	private void policeHD(GuiGraphics g) {
		int x = ox(), y = oy();
		hdSection(g, tr("police"), 38);
		int em = EmailRendu.couleurEmail(r);
		for (int i = 0; i < 3; i++) {
			final int ii = i; int ly = 57 + i * 24;
			hdRadio(g, 16, ly + 3, r.police == i, tr("police." + i), () -> { r.police = ii; change(); });
			int bx0 = x + 100, by0 = y + ly - 2;
			g.fill(bx0 - 1, by0 - 1, bx0 + 107, by0 + 19, 0xFFB48242);
			g.fill(bx0, by0, bx0 + 106, by0 + 18, 0xFF000000 | em);
			g.fill(bx0, by0, bx0 + 106, by0 + 1, 0xFF000000 | EmailRendu.melange(em, 0xFFFFFF, 0.25f));
			MutableComponent ex = Component.literal("Lingots 1 284").withStyle(i == 1 ? net.minecraft.network.chat.Style.EMPTY.withFont(MiseEnPage.IMPERIALE) : net.minecraft.network.chat.Style.EMPTY);
			if (i == 2) {
				g.drawString(font, ex, bx0 + 6, by0 + 6, 0xFF000000 | EmailRendu.melange(em, 0xFFFFFF, 0.35f), false);
				g.drawString(font, ex, bx0 + 6, by0 + 5, 0xFF000000 | EmailRendu.melange(em, 0, 0.6f), false);
			} else g.drawString(font, ex, bx0 + 6, by0 + 5, 0xFF000000 | Reglages.PALETTE[i == 1 ? 1 : 0], true);
		}
		hdSection(g, tr("couleurs"), 133);
		hdTexte(g, tr("couleur_lignes"), 16, 149, InterfaceHD.AIRAIN_SOMBRE);
		for (int k = 0; k < Reglages.PALETTE.length; k++) { final int kk = k; hdEmail(g, 110 + k * 12, 148, Reglages.PALETTE[k], false, () -> { for (Reglages.Ligne l : lignes()) l.couleur = kk; change(); }); }
		hdTexte(g, tr("couleur_valeurs"), 16, 167, InterfaceHD.AIRAIN_SOMBRE);
		for (int k = 0; k < Reglages.PALETTE.length; k++) { final int kk = k; hdEmail(g, 110 + k * 12, 166, Reglages.PALETTE[k], r.coulValeur == k, () -> { r.coulValeur = kk; change(); }); }
	}

	// ---- 4. lumière : éclairage, intensité (curseur du kit), allumage en 3 touches, alerte sur deux lignes
	private void lumiereHD(GuiGraphics g) {
		int x = ox(), y = oy();
		hdSection(g, tr("eclairage"), 38);
		int rx = 16;
		for (int i = 0; i < 3; i++) { final int ii = i; hdRadio(g, rx, 53, r.eclairage == i, tr("eclairage." + i), () -> { r.eclairage = ii; change(); }); rx += 24 + font.width(tr("eclairage." + i)); }
		hdTexte(g, tr("intensite"), 16, 74, InterfaceHD.AIRAIN_SOMBRE);
		boolean dessus = sous(x + 64, y + 68, 140, 20);
		g.blitSprite(dessus ? ResourceLocation.withDefaultNamespace("widget/slider_highlighted") : SPR_PISTE, x + 64, y + 68, 140, 20);
		g.blitSprite(dessus ? ResourceLocation.withDefaultNamespace("widget/slider_handle_highlighted") : SPR_POIGNEE, x + 64 + 132 * r.intensite / 15, y + 68, 8, 20);
		Component v = Component.literal("" + r.intensite);
		g.drawString(font, v, x + 134 - font.width(v) / 2, y + 74, 0xFFFFFF, true);
		zone(x + 64, y + 68, 140, 20, () -> {});
		hdSection(g, tr("allumage"), 95);
		// trois touches à la largeur de leur texte, réparties sur le bac
		int[] la = new int[3]; int sa = 0;
		for (int i = 0; i < 3; i++) { la[i] = Math.max(46, font.width(tr("allumage." + i)) + 12); sa += la[i]; }
		int ea = Math.max(2, (188 - sa) / 2), ax = 15;
		for (int i = 0; i < 3; i++) { final int ii = i; hdTouche(g, ax, 109, la[i], r.allumage == i, tr("allumage." + i), () -> { r.allumage = ii; change(); }); ax += la[i] + ea; }
		hdSection(g, tr("alerte"), 132);
		// ligne puis seuil : chaque réglage suit son libellé (4 px), le seuil est calé à droite du bac
		int xl = 16 + font.width(tr("alerte.ligne")) + 4;
		hdTexte(g, tr("alerte.ligne"), 16, 151, InterfaceHD.AIRAIN_SOMBRE);
		hdFleche(g, xl, 147, false, () -> { r.alerteLigne = Math.max(0, r.alerteLigne - 1); change(); });
		hdValeur(g, xl + 18, 147, 14, Component.literal(r.alerteLigne == 0 ? "-" : "" + r.alerteLigne));
		hdFleche(g, xl + 34, 147, true, () -> { r.alerteLigne = Math.min(Reglages.MAX_LIGNES, r.alerteLigne + 1); change(); });
		int xs = 203 - 56;
		hdTexte(g, tr("alerte.seuil"), xs - 4 - font.width(tr("alerte.seuil")), 151, InterfaceHD.AIRAIN_SOMBRE);
		hdFleche(g, xs, 147, false, () -> { r.seuil -= hasShiftDown() ? 10 : 1; change(); });
		hdValeur(g, xs + 18, 147, 20, Component.literal("" + r.seuil));
		hdFleche(g, xs + 40, 147, true, () -> { r.seuil += hasShiftDown() ? 10 : 1; change(); });
		hdTexte(g, tr("alerte.alors_hd"), 16, 171, InterfaceHD.AIRAIN_SOMBRE);
		for (int i = 0; i < 2; i++) { final int ii = i; hdTouche(g, 46 + i * 52, 167, 50, r.alerteAction == i, tr("alerte.action." + i), () -> { r.alerteAction = ii; change(); }); }
		for (int i = 0; i < 4; i++) { final int ii = i; hdEmail(g, 154 + i * 12, 170, Reglages.PALETTE[i], r.alerteCouleur == i, () -> { r.alerteCouleur = ii; change(); }); }
	}

	// ---- 5. pose : accrochage (avec l'accrochage réel au bout de la ligne du titre), double face, aide Copier
	private void poseHD(GuiGraphics g) {
		int x = ox(), y = oy();
		Component ici = null;
		var mc = net.minecraft.client.Minecraft.getInstance();
		if (mc.level != null && mc.level.getBlockState(pos).getBlock() instanceof EmailBlock)
			ici = tr("ici", tr("montage." + mc.level.getBlockState(pos).getValue(EmailBlock.MONTAGE).ordinal()));
		int xi = ici == null ? 207 : 205 - font.width(ici);
		PanneauHD.libelle(g, font, x + 14, y + 38, x + xi - 10, tr("accrochage"));
		if (ici != null) { PanneauHD.lampe(g, x + xi - 8, y + 41); hdTexte(g, ici, xi, 42, HD_VERT); }
		for (int i = 0; i < 4; i++) { final int ii = i; hdRadio(g, 16 + (i % 2) * 96, 53 + (i / 2) * 14, r.accrochage == i, tr("accrochage." + i), () -> { r.accrochage = ii; change(); }); }
		hdSection(g, tr("double"), 86);
		hdRadio(g, 16, 101, r.memeFace, tr("double.meme"), () -> { r.memeFace = true; arriere = false; change(); });
		hdRadio(g, 112, 101, !r.memeFace, tr("double.different"), () -> {
			if (r.memeFace && r.arriere.isEmpty()) for (Reglages.Ligne l : r.avant) r.arriere.add(l.copie());
			r.memeFace = false; change();
		});
		if (!r.memeFace) {
			hdTexte(g, tr("editer"), 16, 121, InterfaceHD.AIRAIN_SOMBRE);
			Component a = tr("face.avant"), b = tr("face.arriere");
			int wa = Math.max(66, font.width(a) + 10), wb = Math.max(78, font.width(b) + 10);
			hdTouche(g, 50, 117, wa, !arriere, a, () -> { arriere = false; choisie = 0; });
			hdTouche(g, 52 + wa, 117, wb, arriere, b, () -> { arriere = true; choisie = 0; });
		}
		hdSection(g, tr("copier"), 141);
		int ly = 156;
		for (String l : tr("copier.aide").getString().split("\n")) { hdTexte(g, Component.literal(l), 16, ly, HD_TEXTE); ly += 12; }
	}

	// ---- 6. liaisons : pour chaque ligne qui peut recevoir une valeur, la liaison d'affichage qui y écrit, et combien de
	// lignes une source en liste (stock du rayonnage…) remplit à partir d'elle
	private int defileLiaisons;
	private void liaisonsHD(GuiGraphics g) {
		var mc = net.minecraft.client.Minecraft.getInstance();
		hdSection(g, tr("liaisons"), 38);
		List<com.simibubi.create.content.redstone.displayLink.DisplayLinkBlockEntity> liens = mc.level == null ? List.of() : Liaisons.vers(mc.level, pos);
		int n = 0; for (int i = 0; r.liable(i) != null; i++) n++;
		final int VIS = 6;
		defileLiaisons = Math.max(0, Math.min(defileLiaisons, Math.max(0, n - VIS)));
		for (int k = 0; k < VIS && k + defileLiaisons < n; k++) {
			final int i = k + defileLiaisons; Reglages.Ligne l = r.liable(i); int py = 54 + k * 17;
			// la ligne : numéro et début de son texte (ou son type), grisée si elle ne reçoit pas de valeur
			String nom = (i + 1) + " " + (l.texte.isEmpty() ? tr("type." + l.type).getString() : l.texte);
			hdTexte(g, Component.literal(font.plainSubstrByWidth(nom, 50)), 16, py + 4, l.liee() ? InterfaceHD.AIRAIN_SOMBRE : 0x6A6E78);
			if (!l.liee()) continue;
			// liaison actuelle : celle que le tableau a attribuée à la ligne, sinon une liaison jamais réglée qui vise cette ligne
			int actuel = -1;
			EmailBlockEntity tb = mc.level.getBlockEntity(pos) instanceof EmailBlockEntity x ? x : null;
			BlockPos attribuee = tb == null ? null : tb.lienDe(i);
			for (int q = 0; q < liens.size(); q++) {
				BlockPos lp = liens.get(q).getBlockPos();
				if (attribuee != null ? lp.equals(attribuee) : liens.get(q).targetLine == i && (tb == null || tb.ligneDe(lp) == null)) { actuel = q; break; }
			}
			final int act = actuel;
			Component nomLien = act < 0 ? tr("liaisons.aucune") : nomLiaison(mc, liens.get(act));
			hdFleche(g, 68, py, false, () -> { if (!liens.isEmpty()) choisirLiaison(liens, act, -1, i); });
			PanneauHD.cartouche(g, font, ox() + 86, oy() + py, 82, Component.literal(font.plainSubstrByWidth(nomLien.getString(), 76)), act < 0);
			hdFleche(g, 170, py, true, () -> { if (!liens.isEmpty()) choisirLiaison(liens, act, 1, i); });
			// nombre de lignes de la liste : A (toutes), 1 à 9
			Component nb = l.nb == 0 ? tr("liaisons.lignes") : Component.literal("" + l.nb);
			int bx = ox() + 188, by = oy() + py;
			PanneauHD.toucheTexte(g, font, bx, by, 16, false, sous(bx, by, 16, 16), nb);
			zone(bx, by, 16, 16, () -> { l.nb = (l.nb + 1) % 10; change(); });
		}
		int ly = 158;
		if (liens.isEmpty()) hdTexte(g, tr("liaisons.vide"), 16, ly, 0xE06A6A);
		else for (String s : tr("liaisons.aide").getString().split("\n")) { hdTexte(g, Component.literal(s), 16, ly, HD_TEXTE); ly += 11; }
	}
	/** Nom d'une liaison : la source qu'elle lit (« Stock du rayonnage »), à défaut le bloc qu'elle vise. */
	private static Component nomLiaison(net.minecraft.client.Minecraft mc, com.simibubi.create.content.redstone.displayLink.DisplayLinkBlockEntity d) {
		return d.activeSource != null ? d.activeSource.getName() : mc.level.getBlockState(d.getSourcePosition()).getBlock().getName();
	}
	/** Liaison suivante (ou précédente) pour la ligne : « aucune », puis chaque liaison qui vise le tableau. */
	private void choisirLiaison(List<com.simibubi.create.content.redstone.displayLink.DisplayLinkBlockEntity> liens, int actuel, int sens, int ligne) {
		int suivant = Math.floorMod(actuel + 1 + sens, liens.size() + 1) - 1;
		if (suivant < 0) { if (actuel >= 0) PacketDistributor.sendToServer(new PaquetLiaison(pos, liens.get(actuel).getBlockPos(), -1)); }
		else PacketDistributor.sendToServer(new PaquetLiaison(pos, liens.get(suivant).getBlockPos(), ligne));
	}

	// ---- aperçu, dans le panneau sombre
	private void apercu(GuiGraphics g, int x, int y) {
		// interface HD : toute la vitrine (titre en haut, taille au-dessus de l'estrade)
		boolean hd = InterfaceHD.actif();
		int px0 = hd ? x + 222 : x + 225, py0 = hd ? y + 17 : y + 19, pw = hd ? 78 : 74, ph = hd ? 163 : 140;
		if (hd) g.drawString(font, tr("apercu"), px0 + pw / 2 - font.width(tr("apercu")) / 2, py0 + 3, InterfaceHD.AIRAIN_SOMBRE, true);
		else g.drawCenteredString(font, tr("apercu"), px0 + pw / 2, py0 + 3, CLAIR);
		var mc = net.minecraft.client.Minecraft.getInstance();
		int w = 1, h = 1;
		if (mc.level != null && mc.level.getBlockEntity(pos) instanceof EmailBlockEntity e) { w = e.largeur; h = e.hauteur; }
		float W = w * 16, H = h * 16;
		float sc = Math.min((pw - 8) / W, (ph - 34) / H);
		float bx = px0 + (pw - W * sc) / 2, by = py0 + 16 + (ph - 34 - H * sc) / 2;
		float ep = r.cadre == 3 ? 0.5f : h == 1 ? 2 : 3;
		int cadre = r.cadre == 2 ? 0xFFE8E4DC : new int[] {0xFFD6AA5A, 0xFFC2703E, 0xFFA83424, 0xFF900A1C}[r.airain];
		rectF(g, bx, by, bx + W * sc, by + H * sc, r.cadre == 3 ? 0xFF000000 | EmailRendu.couleurEmail(r) : cadre);
		rectF(g, bx + ep * sc, by + ep * sc, bx + (W - ep) * sc, by + (H - ep) * sc, 0xFF000000 | EmailRendu.couleurEmail(r));
		final float ox = bx + ep * sc, oy = by + ep * sc;
		int base = arriere && !r.memeFace ? r.avant.size() : 0;
		MiseEnPage.dessiner(new MiseEnPage.Peintre() {
			@Override
			public void texte(Component c, float tx, float ty, float s, int col, boolean grave) {
				var ps = g.pose(); ps.pushPose(); ps.translate(ox + tx * sc, oy + ty * sc, 0); ps.scale(s * sc, s * sc, 1);
				if (grave) {
					g.drawString(font, c, 0, 1, 0xFF000000 | EmailRendu.melange(EmailRendu.couleurEmail(r), 0xFFFFFF, 0.35f), false);
					g.drawString(font, c, 0, 0, 0xFF000000 | EmailRendu.melange(EmailRendu.couleurEmail(r), 0, 0.6f), false);
				} else g.drawString(font, c, 0, 0, 0xFF000000 | col, false);
				ps.popPose();
			}
			@Override public void rect(float a, float b, float c, float d, int col) { rectF(g, ox + a * sc, oy + b * sc, ox + c * sc, oy + d * sc, 0xFF000000 | col); }
			@Override public void baguette(float a, float b, float c, float d) { rectF(g, ox + a * sc, oy + b * sc, ox + c * sc, oy + d * sc, cadre); }
		}, font, r, lignes(), i -> EmailClientEtat.valeur(pos, base + i), W - 2 * ep, H - 2 * ep);
		if (hd) g.drawString(font, tr("taille_tableau", w, h), px0 + pw / 2 - font.width(tr("taille_tableau", w, h)) / 2, py0 + ph - 14, InterfaceHD.AIRAIN_SOMBRE, true);
		else g.drawCenteredString(font, tr("taille_tableau", w, h), px0 + pw / 2, py0 + ph - 14, CLAIR);
	}
	private static void rectF(GuiGraphics g, float x0, float y0, float x1, float y1, int col) {
		var ps = g.pose(); ps.pushPose(); ps.translate(x0, y0, 0); ps.scale(x1 - x0, y1 - y0, 1); g.fill(0, 0, 1, 1, col); ps.popPose();
	}

	// ---------------------------------------------------------------- clics
	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (b == 0) {
			if (onglet == 3 && surCurseur(mx, my)) { curseur(mx); return true; }
			for (int i = zones.size() - 1; i >= 0; i--) {
				Zone z = zones.get(i);
				if (mx >= z.x0 && mx < z.x1 && my >= z.y0 && my < z.y1) {
					minecraft.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK, 1f));
					z.action.run(); return true;
				}
			}
		}
		return super.mouseClicked(mx, my, b);
	}
	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		if (onglet == 0) { defile = Math.max(0, defile - (int) Math.signum(sy)); return true; }
		if (onglet == 5) { defileLiaisons = Math.max(0, defileLiaisons - (int) Math.signum(sy)); return true; }
		return super.mouseScrolled(mx, my, sx, sy);
	}
}
