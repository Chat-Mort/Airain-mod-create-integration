package fr.chatmort.airain.affichage;

import fr.chatmort.airain.gui.WidgetsEmpire;
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
	private static final String[] ONGLETS = {"contenu", "style", "police", "lumiere", "pose"};
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
		if (onglet == 0) {
			champ = new EditBox(font, ox() + 55, oy() + 177, 158, 10, Component.empty());
			champ.setBordered(false); champ.setTextColor(CLAIR); champ.setMaxLength(Reglages.MAX_TEXTE);
			Reglages.Ligne l = ligne();
			champ.setValue(l == null ? "" : l.texte);
			champ.setResponder(v -> { Reglages.Ligne x = ligne(); if (x != null && !x.texte.equals(v)) { x.texte = v; change(); } });
			addRenderableWidget(champ);
		}
	}
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
		renderBackground(g, mx, my, pt);
		int x = ox(), y = oy();
		g.drawString(font, title.copy().withStyle(s -> s.withBold(true)), x + 14, y + 6, ENCRE, false);
		int tx = x + 10;
		for (int k = 0; k < ONGLETS.length; k++) {
			Component n = tr("onglet." + ONGLETS[k]); int w = font.width(n) + 8; final int kk = k;
			bouton(g, tx, y + 22, w, 14, n, k == onglet, () -> { onglet = kk; rebuildWidgets(); });
			tx += w + 2;
		}
		switch (onglet) { case 0 -> contenu(g, x, y); case 1 -> style(g, x, y); case 2 -> police(g, x, y); case 3 -> lumiere(g, x, y); default -> pose(g, x, y); }
		apercu(g, x, y);
		bouton(g, x + 226, y + 196, 74, 16, Component.translatable("gui.done"), false, this::onClose);
		for (var w : renderables) w.render(g, mx, my, pt);
	}

	// ---- 1. contenu
	private void contenu(GuiGraphics g, int x, int y) {
		List<Reglages.Ligne> L = lignes();
		section(g, tr(r.memeFace ? "lignes" : arriere ? "lignes_arriere" : "lignes_avant"), x + 12, y + 42);
		defile = Math.max(0, Math.min(defile, Math.max(0, L.size() - VISIBLES)));
		int base = arriere && !r.memeFace ? r.avant.size() : 0;
		for (int n = 0; n < VISIBLES && n + defile < L.size(); n++) {
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
		int[] teintes = {0xD6AA5A, 0xBE8250, 0xA8583C, 0x961E1A};
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
		if (onglet == 3 && my >= oy() + 70 && my <= oy() + 86 && mx >= ox() + 66 && mx <= ox() + 194) { curseur(mx); return true; }
		return super.mouseDragged(mx, my, b, dx, dy);
	}
	private void curseur(double mx) {
		int v = (int) Math.round((mx - (ox() + 70)) * 15 / 120.0); v = Math.max(0, Math.min(15, v));
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

	// ---- aperçu, dans le panneau sombre
	private void apercu(GuiGraphics g, int x, int y) {
		int px0 = x + 225, py0 = y + 19, pw = 74, ph = 140;
		g.drawCenteredString(font, tr("apercu"), px0 + pw / 2, py0 + 3, CLAIR);
		var mc = net.minecraft.client.Minecraft.getInstance();
		int w = 1, h = 1;
		if (mc.level != null && mc.level.getBlockEntity(pos) instanceof EmailBlockEntity e) { w = e.largeur; h = e.hauteur; }
		float W = w * 16, H = h * 16;
		float sc = Math.min((pw - 8) / W, (ph - 34) / H);
		float bx = px0 + (pw - W * sc) / 2, by = py0 + 16 + (ph - 34 - H * sc) / 2;
		float ep = r.cadre == 3 ? 0.5f : h == 1 ? 2 : 3;
		int cadre = r.cadre == 2 ? 0xFFE8E4DC : new int[] {0xFFD6AA5A, 0xFFBE8250, 0xFFA8583C, 0xFF961E1A}[r.airain];
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
		g.drawCenteredString(font, tr("taille_tableau", w, h), px0 + pw / 2, py0 + ph - 14, CLAIR);
	}
	private static void rectF(GuiGraphics g, float x0, float y0, float x1, float y1, int col) {
		var ps = g.pose(); ps.pushPose(); ps.translate(x0, y0, 0); ps.scale(x1 - x0, y1 - y0, 1); g.fill(0, 0, 1, 1, col); ps.popPose();
	}

	// ---------------------------------------------------------------- clics
	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (b == 0) {
			if (onglet == 3 && my >= oy() + 70 && my <= oy() + 86 && mx >= ox() + 66 && mx <= ox() + 194) { curseur(mx); return true; }
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
		return super.mouseScrolled(mx, my, sx, sy);
	}
}
