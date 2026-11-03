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
		{"desenchanteur", "airain:desenchanteur"}, {"balise", "airain:balise_defense"}, {"codex", "airain:codex"}, {"gardien", "airain:gardien_spawn_egg"}, {"reliure", "airain:reliure"},
		{"tableau", "airain:tableau_service"}, {"atlas", "airain:atlas"}, {"affiches", "airain:affiche_vierge"}};
	/** Table des matières : 7 chapitres à gauche (sous l'introduction), le reste à droite ; icônes réduites, pas de 13 px. */
	private static final int GAUCHE = 7, PAS = 13;
	private int planche;
	private WidgetsEmpire.Fleche avant, apres;
	private WidgetsEmpire.Signet signet;

	public LivreIngenieurScreen() { super(Component.translatable("item.airain.livre_ingenieur")); }

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }

	@Override
	protected void init() {
		avant = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> aller(planche - 1)));
		apres = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> aller(planche + 1)));
		signet = addRenderableWidget(new WidgetsEmpire.Signet(bx(), by(), b -> aller(0)));
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
		if (key == 268 || key == 259) { aller(0); return true; }   // Début / Retour arrière : le sommaire
		if (key == 262 || key == 267) { aller(planche + 1); return true; }
		if (key == 263 || key == 266) { aller(planche - 1); return true; }
		return super.keyPressed(key, scan, mods);
	}

	/** Position d'une ligne de la table des matières : {x, y du texte}. */
	private int[] ligne(int i) {
		return i < GAUCHE ? new int[] {bx() + 20, by() + 22 + 50 + i * PAS} : new int[] {bx() + 162, by() + 22 + 2 + (i - GAUCHE) * PAS};
	}

	/** Table des matières : un clic sur une ligne ouvre le chapitre. */
	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (planche == 0)
			for (int i = 0; i < CHAPITRES.length; i++) {
				int[] l = ligne(i);
				if (mx >= l[0] && mx < l[0] + LARGE && my >= l[1] - 2 && my < l[1] - 2 + PAS) { aller(i + 1); return true; }
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
		avant.visible = planche > 0;
		apres.visible = planche < CHAPITRES.length;
		signet.visible = planche > 0;
		super.render(g, mx, my, pt);
		int gx = bx() + 20, dx = bx() + 162, y = by() + 22;
		if (planche == 0) {
			texte(g, Component.translatable("item.airain.livre_ingenieur").withStyle(ChatFormatting.BOLD), gx, y + 2, ROUGE, 2);
			texte(g, Component.translatable("airain.ingenieur.intro").withStyle(ChatFormatting.ITALIC), gx, y + 16, SEPIA, 3);
			for (int i = 0; i < CHAPITRES.length; i++) {
				int[] l = ligne(i);
				int x = l[0], yy = l[1];
				g.pose().pushPose();                               // icône réduite (12 px), centrée sur la ligne
				g.pose().translate(x, yy - 2.5f, 0);
				g.pose().scale(0.75f, 0.75f, 1f);
				g.renderItem(objet(i), 0, 0);
				g.pose().popPose();
				boolean survol = mx >= x && mx < x + LARGE && my >= yy - 2 && my < yy - 2 + PAS;
				g.drawString(font, Component.translatable("airain.ingenieur." + CHAPITRES[i][0] + ".court"), x + 15, yy, survol ? BLEU : ENCRE, false);
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
		g.drawString(font, n, dx + LARGE / 2 - font.width(n) / 2, by() + 162, SEPIA, false);   // sous la page de droite
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
