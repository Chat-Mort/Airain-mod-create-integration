package fr.chatmort.airain.ingenieur;

import com.mojang.blaze3d.systems.RenderSystem;
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

import java.util.List;

/**
 * Le livre de l'ingénieur, au style du registre : une table des matières (un clic mène au chapitre), puis une double
 * page par machine de l'Empire. À gauche l'objet, son nom et ce qu'en disait l'Empire ; à droite le mode d'emploi.
 */
public class LivreIngenieurScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registre.png");
	private static final int W = 300, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, BLEU = 0x28507A;
	/** Chapitres : clé de texte et objet illustré. */
	static final String[][] CHAPITRES = {
		{"fondation", "airain:pierre_fondation"}, {"grand_etendard", "airain:grand_etendard"}, {"banniere_murale", "airain:banniere_murale"},
		{"gabarit", "airain:gabarit_banniere"}, {"registre", "airain:registre_fondations"}, {"socle", "airain:socle_trophee"},
		{"banc", "airain:banc_entretien"}, {"modules", "airain:meule_fine"}, {"table", "airain:table_enchantement"},
		{"desenchanteur", "airain:desenchanteur"}, {"balise", "airain:balise_defense"}, {"codex", "airain:codex"}};
	private int planche;

	public LivreIngenieurScreen() { super(Component.translatable("item.airain.livre_ingenieur")); }

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }

	@Override
	protected void init() {
		addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> aller(planche - 1)));
		addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> aller(planche + 1)));
	}

	private void aller(int n) {
		n = Mth.clamp(n, 0, CHAPITRES.length);
		if (n != planche && minecraft != null) minecraft.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1f));
		planche = n;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) { aller(planche + (sy > 0 ? -1 : 1)); return true; }

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == 262 || key == 267) { aller(planche + 1); return true; }
		if (key == 263 || key == 266) { aller(planche - 1); return true; }
		return super.keyPressed(key, scan, mods);
	}

	/** Table des matières : six chapitres par page, un clic sur une ligne ouvre le chapitre. */
	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (planche == 0)
			for (int i = 0; i < CHAPITRES.length; i++) {
				int x = (i < 6 ? bx() + 20 : bx() + 162), y = by() + 22 + (i < 6 ? 52 : 14) + (i % 6) * 17;
				if (i >= 6) y = by() + 22 + 14 + (i - 6) * 20;
				if (mx >= x && mx < x + LARGE && my >= y - 2 && my < y + 16) { aller(i + 1); return true; }
			}
		return super.mouseClicked(mx, my, b);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		RenderSystem.enableBlend();
		g.blit(LIVRE, bx(), by(), 0, 0, W, 196, 512, 256);
	}

	private int texte(GuiGraphics g, FormattedText t, int x, int y, int c, int max) {
		List<FormattedCharSequence> l = font.split(t, LARGE);
		for (int i = 0; i < Math.min(max, l.size()); i++) { g.drawString(font, l.get(i), x, y, c, false); y += 10; }
		return y;
	}

	private ItemStack objet(int i) { return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(CHAPITRES[i][1]))); }

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int gx = bx() + 20, dx = bx() + 162, y = by() + 22;
		if (planche == 0) {
			texte(g, Component.translatable("item.airain.livre_ingenieur").withStyle(ChatFormatting.BOLD), gx, y + 2, ROUGE, 2);
			texte(g, Component.translatable("airain.ingenieur.intro").withStyle(ChatFormatting.ITALIC), gx, y + 16, SEPIA, 3);
			for (int i = 0; i < CHAPITRES.length; i++) {
				int x = i < 6 ? gx : dx, yy = i < 6 ? y + 52 + i * 17 : y + 14 + (i - 6) * 20;
				g.renderItem(objet(i), x, yy - 4);
				boolean survol = mx >= x && mx < x + LARGE && my >= yy - 2 && my < yy + 16;
				g.drawString(font, Component.translatable("airain.ingenieur." + CHAPITRES[i][0] + ".court"), x + 19, yy, survol ? BLEU : ENCRE, false);
			}
		} else {
			int i = planche - 1;
			g.pose().pushPose();
			g.pose().translate(gx + LARGE / 2f - 16, y + 2, 0);
			g.pose().scale(2f, 2f, 1f);
			g.renderItem(objet(i), 0, 0);
			g.pose().popPose();
			Component t = Component.translatable("airain.ingenieur." + CHAPITRES[i][0] + ".titre").withStyle(ChatFormatting.BOLD);
			if (font.width(t) > LARGE) t = Component.translatable("airain.ingenieur." + CHAPITRES[i][0] + ".court").withStyle(ChatFormatting.BOLD);
			g.drawString(font, t, gx + LARGE / 2 - font.width(t) / 2, y + 38, ENCRE, false);
			g.fill(gx + 10, y + 50, gx + LARGE - 10, y + 51, 0xFF9A7046);
			texte(g, Component.translatable("airain.ingenieur." + CHAPITRES[i][0] + ".histoire").withStyle(ChatFormatting.ITALIC), gx, y + 56, SEPIA, 8);
			g.drawString(font, Component.translatable("airain.ingenieur.mode").withStyle(ChatFormatting.BOLD), dx, y, ROUGE, false);
			texte(g, Component.translatable("airain.ingenieur." + CHAPITRES[i][0] + ".usage"), dx, y + 13, ENCRE, 12);
		}
		String n = (planche + 1) + " / " + (CHAPITRES.length + 1);
		g.drawString(font, n, bx() + W / 2 - font.width(n) / 2, by() + 162, SEPIA, false);
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
