package fr.chatmort.airain.tableau;

import java.util.List;

import com.mojang.math.Axis;

import net.minecraft.ChatFormatting;
import fr.chatmort.airain.gui.InterfaceHD;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.MultiLineEditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
import net.neoforged.neoforge.network.PacketDistributor;

/** Le tableau de service : six notes épinglées sur du liège ; une case vide pour en écrire une. */
public class TableauScreen extends Screen {
	private static final ResourceLocation FOND = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/duty_board.png");
	private static final int W = 276, H = 190, NW = 76, NH = 62;
	private static final int[] PUNAISES = {0xFFBE2824, 0xFFE2B828, 0xFF46964A};
	private final PaquetsTableau.Ouvrir d;
	private MultiLineEditBox saisie;
	private boolean ecriture;
	private int couleur = 1;

	public TableauScreen(PaquetsTableau.Ouvrir d) {
		super(d.titre());
		this.d = d;
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - H) / 2 + 6; }
	private int nx(int i) { return bx() + 16 + (i % 3) * 84; }
	private int ny(int i) { return by() + 18 + (i / 3) * 78; }

	@Override
	protected void init() {
		clearWidgets();
		if (!ecriture) return;
		int i = d.notes().size(), x = nx(i), y = ny(i);
		saisie = new MultiLineEditBox(font, x + 2, y + 2, NW - 4, NH - 16, Component.translatable("airain.tableau.ecrire"), Component.empty());
		// la limite est tenue ici : la limite du jeu affiche un compteur « 14/100 » sous le champ, par-dessus les boutons
		int limite = Tableaux.LONGUEUR * Tableaux.LIGNES;
		saisie.setValueListener(t -> { if (t.length() > limite) saisie.setValue(t.substring(0, limite)); });
		addRenderableWidget(saisie);
		setInitialFocus(saisie);
		for (int c = 0; c < 3; c++) {
			int k = c;
			addRenderableWidget(new Pastille(x + 2 + c * 13, y + NH - 13, PUNAISES[k], c == couleur,
				b -> { couleur = k; String t = saisie.getValue(); init(); saisie.setValue(t); }));
		}
		addRenderableWidget(new Touche(x + NW - 28, y + NH - 13, "✔", 0xFF6AC46A, b -> {
			PacketDistributor.sendToServer(new PaquetsTableau.Action(d.pos(), 0, 0, saisie.getValue(), couleur));
			ecriture = false; init();
		}));
		addRenderableWidget(new Touche(x + NW - 14, y + NH - 13, "✕", 0xFFE06A6A, b -> { ecriture = false; init(); }));
	}

	/** Couleur de la pince (12x12) : pastille d'émail sertie, anneau cramoisi sur la choisie (un bouton à chaîne n'y tient pas). */
	private static final class Pastille extends Button {
		private final int couleur; private final boolean choisie;
		Pastille(int x, int y, int couleur, boolean choisie, OnPress a) {
			super(x, y, 12, 12, Component.literal(choisie ? "●" : "○").withStyle(s -> s.withColor(couleur & 0xFFFFFF)), a, DEFAULT_NARRATION);
			this.couleur = couleur; this.choisie = choisie;
		}
		@Override protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			if (!InterfaceHD.actif()) { super.renderWidget(g, mx, my, pt); return; }
			fr.chatmort.airain.gui.PanneauHD.email(g, getX() + 1, getY() + 1, couleur & 0xFFFFFF, choisie || isHoveredOrFocused());
		}
	}

	/** Petite touche 13x12 (valider, annuler) : plaquette d'airain, signe de couleur, rebord cramoisi au survol. */
	private static final class Touche extends Button {
		private final int signe;
		Touche(int x, int y, String txt, int signe, OnPress a) { super(x, y, 13, 12, Component.literal(txt), a, DEFAULT_NARRATION); this.signe = signe; }
		@Override protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			if (!InterfaceHD.actif()) { super.renderWidget(g, mx, my, pt); return; }
			int x = getX(), y = getY(), bord = isHoveredOrFocused() ? 0xFFB0373A : 0xFFC9974F;
			g.fill(x, y, x + 13, y + 12, bord); g.fill(x + 1, y + 1, x + 12, y + 11, 0xFF2A2E37); g.fill(x + 1, y + 1, x + 12, y + 2, 0xFF1F2228);
			var f = net.minecraft.client.Minecraft.getInstance().font;
			g.drawString(f, getMessage(), x + 7 - f.width(getMessage()) / 2, y + 2, signe, false);
		}
	}

	private int noteSous(double mx, double my) {
		for (int i = 0; i < d.notes().size(); i++)
			if (mx >= nx(i) && mx < nx(i) + NW && my >= ny(i) && my < ny(i) + NH) return i;
		return -1;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (super.mouseClicked(mx, my, b)) return true;
		if (ecriture) return false;
		int i = noteSous(mx, my);
		if (i >= 0) {
			PacketDistributor.sendToServer(new PaquetsTableau.Action(d.pos(), b == 1 ? 2 : 1, d.notes().get(i).id(), "", 0));
			return true;
		}
		int k = d.notes().size();
		if (k < Tableaux.NOTES && mx >= nx(k) && mx < nx(k) + NW && my >= ny(k) && my < ny(k) + NH) {
			ecriture = true; init();
			return true;
		}
		return false;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		g.blit(FOND, bx(), by(), 0, 0, W, H, 512, 256);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		renderBackground(g, mx, my, pt);
		g.drawString(font, title.copy().withStyle(ChatFormatting.BOLD), bx() + W / 2 - font.width(title) / 2 - 2, by() - 12, 0xFFE9B0, true);
		List<PaquetsTableau.NoteVue> notes = d.notes();
		int sous = noteSous(mx, my);
		for (int i = 0; i < notes.size(); i++) {
			PaquetsTableau.NoteVue n = notes.get(i);
			int x = nx(i), y = ny(i);
			float angle = ((n.id() * 37) % 7 - 3) * 0.8f;
			g.pose().pushPose();
			g.pose().translate(x + NW / 2f, y + NH / 2f, 0);
			g.pose().mulPose(Axis.ZP.rotationDegrees(angle));
			g.pose().translate(-NW / 2f, -NH / 2f, 0);
			boolean hd = InterfaceHD.actif();
			if (hd) {
				// interface HD : ombre portée puis feuillet de papier (normal, survolé ou vert si la note est faite)
				g.blit(FOND, 2, 3, 360, 64, NW, NH, 512, 256);
				g.blit(FOND, 0, 0, n.fait() ? 360 : 280, !n.fait() && i == sous ? 64 : 0, NW, NH, 512, 256);
			} else {
				g.fill(1, 1, NW + 1, NH + 1, 0x40000000);
				g.fill(0, 0, NW, NH, n.fait() ? 0xFFD6E0C8 : i == sous ? 0xFFF6EAD0 : 0xFFEEE2C4);
			}
			int ly = 8;
			for (FormattedCharSequence l : font.split(Component.literal(n.texte()).withStyle(ChatFormatting.ITALIC), NW - 8)) {
				if (ly > NH - 18) break;
				g.drawString(font, l, 4, ly, 0x32200F, false);
				ly += 10;
			}
			// note faite : gros trait vert en diagonale par-dessus le texte (interface HD), sinon un simple trait
			if (n.fait()) {
				if (hd) g.blit(FOND, 0, 0, 280, 128, NW, NH, 512, 256);
				else g.fill(3, 26, NW - 3, 27, 0xFF46964A);
			}
			String sig = n.auteur() + " · " + Component.translatable("airain.chronique.jour", n.jour()).getString();
			g.pose().pushPose(); g.pose().scale(0.75f, 0.75f, 1);
			g.drawString(font, sig, (int) (4 / 0.75f), (int) ((NH - 9) / 0.75f), 0x785F46, false);
			if (n.nouvelle()) g.drawString(font, Component.translatable("airain.tableau.nouveau"), (int) ((NW - 30) / 0.75f), (int) ((NH - 9) / 0.75f), 0xBE2824, false);
			g.pose().popPose();
			if (hd) {
				// pince d'airain émaillée de la couleur de la note
				g.blit(FOND, NW / 2 - 5, -3, 440, n.couleur() * 8, 11, 6, 512, 256);
			} else {
				g.fill(NW / 2 - 3, -2, NW / 2 + 3, 4, PUNAISES[n.couleur()]);
				g.fill(NW / 2 - 2, -1, NW / 2, 1, 0x80FFFFFF);
			}
			g.pose().popPose();
		}
		int k = notes.size();
		if (k < Tableaux.NOTES) {
			int x = nx(k), y = ny(k);
			if (ecriture) g.fill(x, y, x + NW, y + NH, 0xFFEEE2C4);
			else {
				Component t = Component.translatable("airain.tableau.nouvelle");
				boolean dessus = sous < 0 && mx >= x && mx < x + NW && my >= y && my < y + NH;
				if (InterfaceHD.actif()) {
					// interface HD : contour à la craie en tirets sur l'ardoise, invitation claire
					for (int q = 0; q < NW; q += 4) { g.fill(x + q, y, x + q + 2, y + 1, 0xFFEFE8D8); g.fill(x + q, y + NH - 1, x + q + 2, y + NH, 0xFFEFE8D8); }
					for (int q = 0; q < NH; q += 4) { g.fill(x, y + q, x + 1, y + q + 2, 0xFFEFE8D8); g.fill(x + NW - 1, y + q, x + NW, y + q + 2, 0xFFEFE8D8); }
					g.drawString(font, t, x + NW / 2 - font.width(t) / 2, y + NH / 2 - 4, dessus ? 0xFFFFFF : 0xFFF6E0, true);
				} else {
					g.renderOutline(x, y, NW, NH, 0xFF785432);
					g.drawString(font, t, x + NW / 2 - font.width(t) / 2, y + NH / 2 - 4, dessus ? 0xFFFFFF : 0x5A3C1E, false);
				}
			}
		}
		for (var w : renderables) w.render(g, mx, my, pt);
		if (sous >= 0 && !ecriture) g.renderTooltip(font, Component.translatable("airain.tableau.aide"), mx, my);
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
