package fr.chatmort.airain.borne;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/** Le catalogue de la borne : rayons, recherche, lots ×1 / ×32 / ×64, bon de commande et paiement en pièces. */
public class BorneScreen extends Screen {
	private static final int W = 320, H = 222, COLS = 9, RANGS = 6, LIGNES = 6;
	private final PaquetsBorne.Ouvrir d;
	private final int fond, cadre, accent, texte, doux, case_, survol;
	private Catalogue.Rayon rayon = Catalogue.Rayon.PIERRES;
	private List<Item> liste = new ArrayList<>();
	private final List<PaquetsBorne.Ligne> bon = new ArrayList<>();
	private Item choix;
	private int defil, defilBon, restant, alerte;
	private EditBox recherche;
	private final Button[] lots = new Button[3];
	private Button commander;

	public BorneScreen(PaquetsBorne.Ouvrir d) {
		super(Component.translatable(d.empire() ? "block.airain.borne_imperiale" : "block.airain.borne_arcanique"));
		this.d = d;
		this.restant = d.restant();
		if (d.empire()) { fond = 0xF0EDE6D4; cadre = 0xFFC9A13C; accent = 0xFF962024; texte = 0xFF3A2A1A; doux = 0xFF7A6A55; case_ = 0xFFDCD3BC; survol = 0xFFF3E3A8; }
		else { fond = 0xF0181220; cadre = 0xFF6A3FB0; accent = 0xFFBAA0FF; texte = 0xFFE6DCFF; doux = 0xFF9A8AB8; case_ = 0xFF2A2238; survol = 0xFF4A3470; }
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - H) / 2; }

	@Override
	protected void init() {
		int x = bx(), y = by();
		String avant = recherche == null ? "" : recherche.getValue();
		recherche = new EditBox(font, x + 124, y + 22, 52, 14, Component.translatable("airain.borne.chercher"));
		recherche.setValue(avant);
		recherche.setHint(Component.translatable("airain.borne.chercher"));
		recherche.setResponder(s -> { defil = 0; filtrer(); });
		addRenderableWidget(recherche);
		for (int i = 0; i < 3; i++) {
			int k = i;
			lots[i] = addRenderableWidget(Button.builder(Component.literal("×" + Catalogue.LOTS[i]), b -> ajouter(k)).bounds(x + 8 + i * 56, y + 172, 50, 14).build());
		}
		commander = addRenderableWidget(Button.builder(Component.translatable("airain.borne.commander"), b -> envoyer()).bounds(x + 184, y + 198, 128, 18).build());
		filtrer();
		majBoutons();
	}

	private void filtrer() {
		String q = recherche == null ? "" : recherche.getValue().trim().toLowerCase(Locale.ROOT);
		liste = new ArrayList<>();
		if (q.isEmpty()) liste.addAll(Catalogue.rayon(rayon));
		else for (Catalogue.Rayon r : Catalogue.Rayon.values())
			for (Item it : Catalogue.rayon(r))
				if (it.getDescription().getString().toLowerCase(Locale.ROOT).contains(q) || BuiltInRegistries.ITEM.getKey(it).getPath().contains(q)) liste.add(it);
	}

	private void majBoutons() {
		for (int i = 0; i < 3; i++) lots[i].active = choix != null && Catalogue.prix(choix, i) > 0;
		long total = PaquetsBorne.total(bon);
		commander.active = !bon.isEmpty() && restant <= 0 && !d.occupee() && minecraft != null && minecraft.player != null && Catalogue.solde(minecraft.player) >= total;
		if (restant > 0) commander.setMessage(Component.translatable("airain.borne.livraison", temps()));
		else if (d.occupee()) commander.setMessage(Component.translatable("airain.borne.zone_pleine"));
		else commander.setMessage(Component.translatable("airain.borne.commander"));
	}

	private String temps() { int s = (restant + 19) / 20; return (s / 60) + ":" + String.format("%02d", s % 60); }

	private void ajouter(int lot) {
		if (choix == null || Catalogue.prix(choix, lot) <= 0) return;
		var id = BuiltInRegistries.ITEM.getKey(choix);
		List<PaquetsBorne.Ligne> essai = new ArrayList<>(bon);
		int i = -1;
		for (int k = 0; k < essai.size(); k++) if (essai.get(k).id().equals(id) && essai.get(k).lot() == lot) i = k;
		if (i >= 0) {
			PaquetsBorne.Ligne l = essai.get(i);
			if (l.fois() >= 64) return;
			essai.set(i, new PaquetsBorne.Ligne(id, lot, l.fois() + 1));
		} else essai.add(new PaquetsBorne.Ligne(id, lot, 1));
		if (PaquetsBorne.piles(essai) > PaquetsBorne.PILES) { alerte = 60; return; }
		bon.clear(); bon.addAll(essai);
		majBoutons();
	}

	private void envoyer() {
		if (bon.isEmpty()) return;
		PacketDistributor.sendToServer(new PaquetsBorne.Commander(d.pos(), new ArrayList<>(bon)));
		onClose();
	}

	@Override
	public void tick() {
		if (restant > 0) restant--;
		if (alerte > 0) alerte--;
		majBoutons();
	}

	// ------------------------------------------------------------------ dessin
	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		int x = bx(), y = by();
		g.fill(x, y, x + W, y + H, fond);
		g.renderOutline(x, y, W, H, cadre);
		g.renderOutline(x + 2, y + 2, W - 4, H - 4, cadre);
		g.fill(x + 180, y + 40, x + 181, y + H - 6, cadre);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = bx(), y = by();
		List<Component> info = null;
		g.drawString(font, title, x + 8, y + 7, accent, false);
		// rayons
		for (Catalogue.Rayon r : Catalogue.Rayon.values()) {
			int rx = x + 8 + r.ordinal() * 22, ry = y + 20;
			boolean sel = r == rayon && recherche.getValue().isBlank();
			g.fill(rx, ry, rx + 20, ry + 18, sel ? cadre : case_);
			g.renderItem(new ItemStack(r.icone), rx + 2, ry + 1);
			if (mx >= rx && mx < rx + 20 && my >= ry && my < ry + 18) info = List.of(Component.translatable("airain.borne.rayon." + r.cle));
		}
		// grille
		int gx = x + 8, gy = y + 44;
		Item sous = null;
		for (int i = 0; i < COLS * RANGS; i++) {
			int n = defil * COLS + i;
			int cx = gx + (i % COLS) * 18, cy = gy + (i / COLS) * 18;
			boolean dedans = mx >= cx && mx < cx + 18 && my >= cy && my < cy + 18;
			Item it = n < liste.size() ? liste.get(n) : null;
			g.fill(cx, cy, cx + 17, cy + 17, it != null && it == choix ? cadre : dedans && it != null ? survol : case_);
			if (it == null) continue;
			g.renderItem(new ItemStack(it), cx, cy);
			if (dedans) sous = it;
		}
		int lignesTot = (liste.size() + COLS - 1) / COLS;
		if (lignesTot > RANGS) {
			int h = RANGS * 18, bh = Math.max(8, h * RANGS / lignesTot), by0 = gy + (h - bh) * defil / Math.max(1, lignesTot - RANGS);
			g.fill(gx + 164, gy, gx + 166, gy + h, case_); g.fill(gx + 164, by0, gx + 166, by0 + bh, cadre);
		}
		if (liste.isEmpty()) g.drawString(font, Component.translatable("airain.borne.vide"), gx + 4, gy + 4, doux, false);
		// détail de l'objet choisi
		if (choix != null) {
			g.renderItem(new ItemStack(choix), gx, y + 154);
			g.drawString(font, font.plainSubstrByWidth(choix.getDescription().getString(), 120), gx + 20, y + 155, texte, false);
			g.drawString(font, Component.translatable("airain.borne.palier." + Catalogue.palier(choix).cle), gx + 20, y + 164, doux, false);
			for (int i = 0; i < 3; i++) {
				int p = Catalogue.prix(choix, i);
				if (p > 0) prix(g, x + 8 + i * 56, y + 190, p); else g.drawString(font, "—", x + 28 + i * 56, y + 194, doux, false);
			}
		} else g.drawString(font, Component.translatable("airain.borne.choisir"), gx, y + 158, doux, false);
		// bon de commande
		int rx = x + 186;
		g.drawString(font, Component.translatable("airain.borne.bon", PaquetsBorne.piles(bon), PaquetsBorne.PILES), rx, y + 22, accent, false);
		if (bon.isEmpty()) g.drawString(font, Component.translatable("airain.borne.bon_vide"), rx, y + 46, doux, false);
		for (int i = 0; i < LIGNES; i++) {
			int n = defilBon + i;
			if (n >= bon.size()) break;
			PaquetsBorne.Ligne l = bon.get(n);
			int ly = y + 40 + i * 19;
			boolean dedans = mx >= rx && mx < x + W - 8 && my >= ly && my < ly + 18;
			if (dedans) g.fill(rx - 2, ly, x + W - 8, ly + 18, survol);
			g.renderItem(new ItemStack(l.item()), rx, ly + 1);
			g.drawString(font, "×" + Catalogue.LOTS[l.lot()] + (l.fois() > 1 ? "  ×" + l.fois() : ""), rx + 19, ly + 5, texte, false);
			prixCompact(g, x + W - 10, ly + 5, l.prix());
			if (dedans) info = List.of(l.item().getDescription(), Component.translatable("airain.borne.retirer").withStyle(net.minecraft.ChatFormatting.GRAY));
		}
		if (bon.size() > LIGNES) g.drawString(font, (defilBon + 1) + "–" + Math.min(bon.size(), defilBon + LIGNES) + " / " + bon.size(), rx, y + 156, doux, false);
		long total = PaquetsBorne.total(bon), solde = minecraft.player == null ? 0 : Catalogue.solde(minecraft.player);
		g.drawString(font, Component.translatable("airain.borne.total"), rx, y + 162, texte, false);
		prix(g, rx + 40, y + 158, total);
		g.drawString(font, Component.translatable("airain.borne.solde"), rx, y + 182, solde >= total ? doux : 0xFFD04040, false);
		prix(g, rx + 40, y + 178, solde);
		if (alerte > 0) g.drawCenteredString(font, Component.translatable("airain.borne.trop"), x + W / 2, y + H + 4, 0xFFFF6060);
		if (sous != null) {
			List<Component> tt = new ArrayList<>(getTooltipFromItem(minecraft, new ItemStack(sous)));
			tt.add(Component.translatable("airain.borne.palier." + Catalogue.palier(sous).cle).withStyle(net.minecraft.ChatFormatting.GRAY));
			info = tt;
		}
		if (info != null) g.renderTooltip(font, info, java.util.Optional.empty(), mx, my);
	}

	/** Une somme en pièces, de la plus grosse à la plus petite (icônes avec quantité). */
	private void prix(GuiGraphics g, int x, int y, long somme) {
		if (somme <= 0) { g.drawString(font, "0", x + 4, y + 4, doux, false); return; }
		int[] n = Catalogue.decomposer(somme);
		for (int k = n.length - 1; k >= 0; k--) {
			if (n[k] == 0) continue;
			ItemStack s = new ItemStack(Catalogue.piece(k));
			g.renderItem(s, x, y);
			g.renderItemDecorations(font, s, x, y, String.valueOf(n[k]));
			x += 18;
		}
	}

	/** Version texte courte, alignée à droite (la plus grosse pièce + reste approché). */
	private void prixCompact(GuiGraphics g, int droite, int y, long somme) {
		int[] n = Catalogue.decomposer(somme);
		int x = droite;
		for (int k = 0; k < n.length; k++) {
			if (n[k] == 0) continue;
			String t = String.valueOf(n[k]);
			x -= 9;
			g.pose().pushPose(); g.pose().translate(x, y - 1, 0); g.pose().scale(0.5f, 0.5f, 1f);
			g.renderItem(new ItemStack(Catalogue.piece(k)), 0, 0);
			g.pose().popPose();
			x -= font.width(t) + 1;
			g.drawString(font, t, x, y, doux, false);
			x -= 3;
		}
	}

	// ------------------------------------------------------------------ souris
	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (super.mouseClicked(mx, my, b)) return true;
		int x = bx(), y = by();
		for (Catalogue.Rayon r : Catalogue.Rayon.values()) {
			int rx = x + 8 + r.ordinal() * 22, ry = y + 20;
			if (mx >= rx && mx < rx + 20 && my >= ry && my < ry + 18) { rayon = r; recherche.setValue(""); defil = 0; filtrer(); return true; }
		}
		int gx = x + 8, gy = y + 44;
		if (mx >= gx && mx < gx + COLS * 18 && my >= gy && my < gy + RANGS * 18) {
			int n = defil * COLS + (int) ((my - gy) / 18) * COLS + (int) ((mx - gx) / 18);
			if (n < liste.size()) { choix = liste.get(n); majBoutons(); }
			return true;
		}
		int rx = x + 186;
		for (int i = 0; i < LIGNES; i++) {
			int n = defilBon + i, ly = y + 40 + i * 19;
			if (n < bon.size() && mx >= rx && mx < x + W - 8 && my >= ly && my < ly + 18) {
				PaquetsBorne.Ligne l = bon.get(n);
				if (l.fois() > 1 && !hasShiftDown()) bon.set(n, new PaquetsBorne.Ligne(l.id(), l.lot(), l.fois() - 1));
				else bon.remove(n);
				defilBon = Math.max(0, Math.min(defilBon, bon.size() - LIGNES));
				majBoutons();
				return true;
			}
		}
		return false;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double dx, double dy) {
		int x = bx();
		if (mx >= x + 182) defilBon = Math.max(0, Math.min(defilBon - (int) Math.signum(dy), bon.size() - LIGNES));
		else {
			int max = Math.max(0, (liste.size() + COLS - 1) / COLS - RANGS);
			defil = Math.max(0, Math.min(max, defil - (int) Math.signum(dy)));
		}
		return true;
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
