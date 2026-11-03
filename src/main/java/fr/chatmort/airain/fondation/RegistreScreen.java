package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.math.Axis;
import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/**
 * Le registre des fondations : un livre de l'Empire relié de cuir rouge. Page de titre scellée, puis une page par base
 * (sa bannière, son nom, sa devise, ses coordonnées, la distance et une flèche vers elle, ses trophées),
 * puis les trophées de l'Empire, trois par page.
 */
public class RegistreScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registre.png");
	private static final int W = 300, H = 190, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, VERT = 0x2E5A1E;
	private static final int PAR_PAGE_TROPHEES = 2;
	private final OuvrirRegistre donnees;
	private final List<Page> contenus = new ArrayList<>();
	private int planche;   // double page affichée
	private WidgetsEmpire.Fleche avant, apres;

	private interface Page { void dessiner(GuiGraphics g, int x, int y, float pt); }

	public RegistreScreen(OuvrirRegistre donnees) {
		super(Component.translatable("airain.registre.titre"));
		this.donnees = donnees;
		contenus.add(this::pageTitre);
		for (int i = 0; i < donnees.bases().size(); i++) {
			final int k = i;
			contenus.add((g, x, y, pt) -> pageBase(g, x, y, pt, k));
		}
		for (int i = 0; i < donnees.trophees().size(); i += PAR_PAGE_TROPHEES) {
			final int k = i;
			contenus.add((g, x, y, pt) -> pageTrophees(g, x, y, k));
		}
		if (donnees.bases().isEmpty()) contenus.add(this::pageVide);
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }
	private int planches() { return (contenus.size() + 1) / 2; }

	@Override
	protected void init() {
		int x = bx(), y = by();
		avant = addRenderableWidget(new WidgetsEmpire.Fleche(x + 20, y + 156, false, b -> tourner(-1)));
		apres = addRenderableWidget(new WidgetsEmpire.Fleche(x + W - 36, y + 156, true, b -> tourner(1)));
	}

	private void tourner(int d) {
		int n = Mth.clamp(planche + d, 0, planches() - 1);
		if (n != planche && minecraft != null)
			minecraft.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1f));
		planche = n;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		tourner(sy > 0 ? -1 : 1);
		return true;
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == 262 || key == 267) { tourner(1); return true; }      // flèche droite, page suivante
		if (key == 263 || key == 266) { tourner(-1); return true; }
		return super.keyPressed(key, scan, mods);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		RenderSystem.enableBlend();
		g.blit(LIVRE, bx(), by(), 0, 0, W, 196, 512, 256);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		avant.visible = planche > 0;
		apres.visible = planche < planches() - 1;
		super.render(g, mx, my, pt);
		int x = bx(), y = by();
		for (int c = 0; c < 2; c++) {
			int k = planche * 2 + c;
			if (k >= contenus.size()) break;
			int px = x + (c == 0 ? 20 : 162), py = y + 22;
			contenus.get(k).dessiner(g, px, py, pt);
			String num = String.valueOf(k + 1);
			g.drawString(font, num, px + LARGE / 2 - font.width(num) / 2, y + 162, SEPIA, false);
		}
	}

	// ------------------------------------------------------------------ pages
	private void centre(GuiGraphics g, Component t, int x, int y, int c) {
		g.drawString(font, t, x + LARGE / 2 - font.width(t) / 2, y, c, false);
	}

	private int paragraphe(GuiGraphics g, FormattedText t, int x, int y, int c, int maxLignes, boolean centrer) {
		List<FormattedCharSequence> l = font.split(t, LARGE);
		for (int i = 0; i < Math.min(maxLignes, l.size()); i++) {
			int dx = centrer ? LARGE / 2 - font.width(l.get(i)) / 2 : 0;
			g.drawString(font, l.get(i), x + dx, y, c, false);
			y += 10;
		}
		return y;
	}

	private void filet(GuiGraphics g, int x, int y) {
		g.fill(x + 10, y, x + LARGE - 10, y + 1, 0xFF9A7046);
		g.blit(LIVRE, x + LARGE / 2 - 2, y - 2, 352, 0, 5, 5, 512, 256);
	}

	private void pageTitre(GuiGraphics g, int x, int y, float pt) {
		y += 6;
		paragraphe(g, Component.translatable("airain.registre.titre").withStyle(ChatFormatting.BOLD), x, y, ROUGE, 2, true);
		paragraphe(g, Component.translatable("airain.registre.sous_titre").withStyle(ChatFormatting.ITALIC), x, y + 22, SEPIA, 2, true);
		RenderSystem.enableBlend();
		g.blit(LIVRE, x + LARGE / 2 - 14, y + 46, 320, 0, 28, 28, 512, 256);
		filet(g, x, y + 80);
		centre(g, Component.translatable("airain.registre.compte_bases", donnees.bases().size()), x, y + 88, ENCRE);
		centre(g, Component.translatable("airain.registre.compte_trophees", donnees.trophees().size()), x, y + 99, ENCRE);
		paragraphe(g, Component.translatable("airain.registre.note"), x, y + 112, SEPIA, 1, true);
	}

	private void pageVide(GuiGraphics g, int x, int y, float pt) {
		paragraphe(g, Component.translatable("airain.registre.vide"), x, y + 20, SEPIA, 12, true);
	}

	private void pageBase(GuiGraphics g, int x, int y, float pt, int k) {
		OuvrirRegistre.Base b = donnees.bases().get(k);
		Apparence a = Apparence.unpack(b.apparence(), b.ext());
		RenderSystem.enableBlend();
		g.fill(x + LARGE / 2 - 9, y - 1, x + LARGE / 2 + 9, y, 0xFF5A3A1A);             // tringle
		g.blit(TexturesBanniere.de(a), x + LARGE / 2 - 7, y, 14, 28, 0f, 0f, 16, 32, 16, 32);
		Component nom = b.nom().isEmpty() ? Component.translatable("airain.fondation.sans_nom") : Component.literal(b.nom());
		int yy = paragraphe(g, nom.copy().withStyle(ChatFormatting.BOLD), x, y + 32, ENCRE, 1, true);
		if (!b.devise().isEmpty())
			yy = paragraphe(g, Component.literal("« " + b.devise() + " »").withStyle(ChatFormatting.ITALIC), x, yy, SEPIA, 2, true);
		filet(g, x, yy + 3);
		yy += 9;
		g.drawString(font, Component.translatable("airain.registre.coordonnees"), x, yy, SEPIA, false);
		String c = b.pos().getX() + "  " + b.pos().getY() + "  " + b.pos().getZ();
		g.drawString(font, c, x + LARGE - font.width(c), yy, ENCRE, false);
		yy += 11;
		g.drawString(font, Component.translatable("airain.registre.lieu"), x, yy, SEPIA, false);
		Component dim = Component.translatable("airain.registre.dim." + b.dim().getPath());
		g.drawString(font, dim, x + LARGE - font.width(dim), yy, ENCRE, false);
		yy += 11;
		var joueur = minecraft != null ? minecraft.player : null;
		if (joueur != null && joueur.level().dimension().location().equals(b.dim())) {
			double dx = b.pos().getX() + 0.5 - joueur.getX(), dz = b.pos().getZ() + 0.5 - joueur.getZ();
			int dist = (int) Math.sqrt(dx * dx + dz * dz);
			g.drawString(font, Component.translatable("airain.registre.distance_seule"), x, yy, SEPIA, false);
			Component d = dist < 6 ? Component.translatable("airain.registre.ici") : Component.translatable("airain.registre.blocs", dist);
			g.drawString(font, d, x + LARGE - font.width(d) - (dist < 6 ? 0 : 16), yy, ENCRE, false);
			if (dist >= 6) {                                   // flèche vers la base, selon le regard du joueur
				float cible = (float) (Mth.atan2(-dx, dz) * Mth.RAD_TO_DEG);
				float rel = Mth.wrapDegrees(cible - joueur.getViewYRot(pt));
				g.pose().pushPose();
				g.pose().translate(x + LARGE - 6, yy + 3.5f, 0);
				g.pose().mulPose(Axis.ZP.rotationDegrees(rel));
				g.blit(LIVRE, -6, -6, 304, 0, 13, 13, 512, 256);
				g.pose().popPose();
			}
		} else {
			g.drawString(font, Component.translatable("airain.registre.ailleurs"), x, yy, SEPIA, false);
		}
		yy += 11;
		g.drawString(font, Component.translatable("airain.registre.gardiens"), x, yy, SEPIA, false);
		Component ng = Component.translatable("airain.registre.gardiens_n", b.gardiens(), fr.chatmort.airain.gardien.Gardiens.LIMITE);
		g.drawString(font, ng, x + LARGE - font.width(ng), yy, b.gardiens() > 0 ? ENCRE : SEPIA, false);
		yy += 14;
		List<ItemStack> ici = new ArrayList<>();
		for (OuvrirRegistre.Trophee t : donnees.trophees())
			if (t.base() == k) ici.add(new ItemStack(BuiltInRegistries.ITEM.get(t.objet())));
		if (!ici.isEmpty() && yy + 26 <= y + 134) {
			g.drawString(font, Component.translatable("airain.registre.exposes"), x, yy, SEPIA, false);
			for (int i = 0; i < Math.min(6, ici.size()); i++) g.renderItem(ici.get(i), x + i * 19, yy + 10);
		}
	}

	/** Coupe une ligne trop longue (style compris : gras, italique) et termine par « … ». */
	private FormattedCharSequence coupe(Component t, int w) {
		if (font.width(t) <= w) return t.getVisualOrderText();
		FormattedText f = font.substrByWidth(t, w - font.width("…"));
		return net.minecraft.locale.Language.getInstance().getVisualOrder(FormattedText.composite(f, Component.literal("…")));
	}

	private void pageTrophees(GuiGraphics g, int x, int y, int debut) {
		Component titre = Component.translatable("airain.registre.trophees").withStyle(ChatFormatting.BOLD);
		if (font.width(titre) > LARGE) {                       // titre trop large (anglais) : un peu plus petit
			float k = LARGE / (float) font.width(titre);
			g.pose().pushPose();
			g.pose().translate(x + LARGE / 2f, y + (1 - k) * 4, 0);
			g.pose().scale(k, k, 1);
			g.drawString(font, titre, -font.width(titre) / 2, 0, ROUGE, false);
			g.pose().popPose();
		} else centre(g, titre, x, y, ROUGE);
		filet(g, x, y + 13);
		int yy = y + 20;
		for (int i = debut; i < Math.min(donnees.trophees().size(), debut + PAR_PAGE_TROPHEES); i++) {
			OuvrirRegistre.Trophee t = donnees.trophees().get(i);
			ItemStack s = new ItemStack(BuiltInRegistries.ITEM.get(t.objet()));
			g.renderItem(s, x, yy);
			int ly = paragraphe2(g, s.getHoverName().copy().withStyle(ChatFormatting.BOLD), x + 20, yy, ENCRE, 1, LARGE - 20);
			StringBuilder ef = new StringBuilder();
			for (var e : fr.chatmort.airain.trophee.Trophees.effetsDe(s))
				ef.append(ef.length() > 0 ? ", " : "").append(Component.translatable("airain.trophee.effet." + e.name().toLowerCase()).getString());
			ly = Math.max(ly, yy + 8);
			ly = paragraphe2(g, Component.literal(ef.toString()), x + 20, ly, VERT, 1, LARGE - 20);
			ly = Math.max(ly, yy + 19);
			if (!t.plaque().isEmpty()) {
				Component p = Component.literal("« " + t.plaque() + " »").withStyle(ChatFormatting.ITALIC);
				ly = paragraphe2(g, p, x, ly, SEPIA, 2, LARGE);
			}
			Component jour = Component.translatable("airain.registre.jour", t.jour()).withStyle(ChatFormatting.ITALIC);
			int lj = font.width(jour);
			Component base = t.base() >= 0 && t.base() < donnees.bases().size() && !donnees.bases().get(t.base()).nom().isEmpty()
				? Component.literal(donnees.bases().get(t.base()).nom()) : Component.translatable("airain.registre.hors_base");
			g.drawString(font, coupe(base, LARGE - lj - 6), x, ly, ENCRE, false);
			g.drawString(font, jour, x + LARGE - lj, ly, SEPIA, false);
			yy = ly + 16;
		}
	}

	/** Paragraphe sur une largeur donnée ; la dernière ligne autorisée est coupée proprement si le texte déborde. */
	private int paragraphe2(GuiGraphics g, Component t, int x, int y, int c, int maxLignes, int w) {
		List<FormattedCharSequence> l = font.split(t, w);
		if (l.size() > maxLignes) {
			for (int i = 0; i < maxLignes - 1; i++) { g.drawString(font, l.get(i), x, y, c, false); y += 10; }
			// reste du texte sur la dernière ligne, coupé
			List<FormattedText> morceaux = font.getSplitter().splitLines(t, w, net.minecraft.network.chat.Style.EMPTY);
			FormattedText reste = FormattedText.composite(morceaux.subList(maxLignes - 1, morceaux.size()).toArray(new FormattedText[0]));
			FormattedText f = font.substrByWidth(reste, w - font.width("…"));
			g.drawString(font, net.minecraft.locale.Language.getInstance().getVisualOrder(FormattedText.composite(f, Component.literal("…"))), x, y, c, false);
			return y + 10;
		}
		for (FormattedCharSequence s : l) { g.drawString(font, s, x, y, c, false); y += 10; }
		return y;
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
