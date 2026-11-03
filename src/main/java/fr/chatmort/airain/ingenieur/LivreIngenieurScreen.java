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

import java.util.ArrayList;
import java.util.List;

/**
 * Le livre de l'ingénieur, au style du registre. Quatre sommaires (machines et blocs, objets et ressources, fin de l'Empire,
 * fin de l'Écho), chacun sur une double page ; un clic mène au chapitre. Ensuite une double page par sujet : à gauche
 * l'objet, son nom et ce qu'en disait l'Empire (et la suite du mode d'emploi s'il est long) ; à droite le mode d'emploi.
 */
public class LivreIngenieurScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registre.png");
	private static final int W = 300, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, BLEU = 0x28507A;

	/** Sections : clé du sommaire, puis chapitres {clé de texte, objet illustré}. */
	static final String[] SECTIONS = {"machines", "objets", "empire", "echo"};
	static final String[][][] CHAPITRES = {
		{{"fondation", "airain:pierre_fondation"}, {"grand_etendard", "airain:grand_etendard"}, {"banniere_murale", "airain:banniere_murale"},
		 {"gabarit", "airain:gabarit_banniere"}, {"registre", "airain:registre_fondations"}, {"socle", "airain:socle_trophee"},
		 {"banc", "airain:banc_entretien"}, {"modules", "airain:meule_fine"}, {"table", "airain:table_enchantement"},
		 {"desenchanteur", "airain:desenchanteur"}, {"balise", "airain:balise_defense"}, {"gardien", "airain:gardien_spawn_egg"},
		 {"modules_gardien", "airain:module_lanterne"}},
		{{"codex", "airain:codex"}, {"chroniques", "airain:chroniques"}, {"reliure", "airain:reliure"}, {"tableau", "airain:tableau_service"},
		 {"atlas", "airain:atlas"}, {"affiches", "airain:affiche_vierge"}, {"cartes", "airain:carte_empire"},
		 {"encre", "airain:encre_runique"}, {"sacre", "airain:plaque_netherite_sacree"}},
		{{"couronne", "airain:couronne_airain"}, {"capitale_sacree", "airain:pierre_fondation"}, {"etoile", "airain:bloc_etoile"},
		 {"armure_sacree", "airain:plastron_sacre"}, {"armure_imperiale", "airain:plastron_imperial"}, {"armes_sacrees", "airain:katana_sacre"},
		 {"armes_imperiales", "airain:katana_imperial"}, {"sceptre_imperial", "airain:sceptre_imperial"}, {"capitaine", "airain:plaque_imperiale"},
		 {"trone", "airain:trone_imperial"}, {"charte", "airain:charte"}},
		{{"diademe", "airain:diademe_echo"}, {"capitale_arcanique", "airain:pierre_fondation"}, {"arcanium", "airain:lingot_arcanium"},
		 {"armure_runique", "airain:plastron_runique"}, {"armure_arcanique", "airain:plastron_arcanique"}, {"armes_runiques", "airain:katana_runique"},
		 {"armes_arcaniques", "airain:katana_arcanique"}, {"sceptre_arcanique", "airain:sceptre_arcanique"}, {"gardien_echo", "airain:bloc_echo_primordial"},
		 {"solium", "airain:solium"}, {"relais", "kubejs:diapason_echo"}}};
	/** Chapitres à la suite, et la section de chacun. */
	private static final List<String[]> TOUS = new ArrayList<>();
	private static final List<Integer> SECTION_DE = new ArrayList<>();
	private static final int[] DEBUT = new int[SECTIONS.length];
	static {
		for (int s = 0; s < CHAPITRES.length; s++) {
			DEBUT[s] = TOUS.size();
			for (String[] c : CHAPITRES[s]) { TOUS.add(c); SECTION_DE.add(s); }
		}
	}
	/** Sommaire : 9 lignes à gauche (sous le titre), le reste à droite ; icônes réduites, pas de 12 px. */
	private static final int GAUCHE = 9, PAS = 12;
	private int planche;
	private WidgetsEmpire.Fleche avant, apres;
	private WidgetsEmpire.Signet signet;

	public LivreIngenieurScreen() { super(Component.translatable("item.airain.livre_ingenieur")); }

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }
	private static int dernier() { return SECTIONS.length + TOUS.size() - 1; }

	@Override
	protected void init() {
		avant = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> aller(planche - 1)));
		apres = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> aller(planche + 1)));
		signet = addRenderableWidget(new WidgetsEmpire.Signet(bx(), by(), b -> aller(planche >= SECTIONS.length ? SECTION_DE.get(planche - SECTIONS.length) : 0)));
	}

	private void aller(int n) {
		n = Mth.clamp(n, 0, dernier());
		if (n != planche && minecraft != null) minecraft.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1f));
		planche = n;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) { aller(planche + (sy > 0 ? -1 : 1)); return true; }

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == 268 || key == 259) { aller(0); return true; }   // Début / Retour arrière : le premier sommaire
		if (key == 262 || key == 267) { aller(planche + 1); return true; }
		if (key == 263 || key == 266) { aller(planche - 1); return true; }
		return super.keyPressed(key, scan, mods);
	}

	/** Position d'une ligne du sommaire : {x, y du texte}. */
	private int[] ligne(int i) {
		return i < GAUCHE ? new int[] {bx() + 20, by() + 22 + 44 + i * PAS} : new int[] {bx() + 162, by() + 22 + 2 + (i - GAUCHE) * PAS};
	}

	/** Onglets des quatre sommaires, en bas de la page de gauche. */
	private int[] onglet(int s) {
		int x = bx() + 20;
		for (int i = 0; i < s; i++) x += largeurOnglet(i) + 7;
		return new int[] {x, by() + 22 + 26};
	}

	private int largeurOnglet(int s) { return font.width(Component.translatable("airain.ingenieur.onglet." + SECTIONS[s])); }

	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (planche < SECTIONS.length) {
			String[][] ch = CHAPITRES[planche];
			for (int i = 0; i < ch.length; i++) {
				int[] l = ligne(i);
				if (mx >= l[0] && mx < l[0] + LARGE && my >= l[1] - 2 && my < l[1] - 2 + PAS) { aller(SECTIONS.length + DEBUT[planche] + i); return true; }
			}
			for (int s = 0; s < SECTIONS.length; s++) {
				int[] o = onglet(s);
				if (mx >= o[0] && mx < o[0] + largeurOnglet(s) && my >= o[1] - 2 && my < o[1] + 10) { aller(s); return true; }
			}
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

	private static ItemStack objet(String id) { return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(id))); }

	private void icone(GuiGraphics g, String id, float x, float y, float echelle) {
		g.pose().pushPose();
		g.pose().translate(x, y, 0);
		g.pose().scale(echelle, echelle, 1f);
		g.renderItem(objet(id), 0, 0);
		g.pose().popPose();
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		avant.visible = planche > 0;
		apres.visible = planche < dernier();
		signet.visible = planche > 0;
		super.render(g, mx, my, pt);
		int gx = bx() + 20, dx = bx() + 162, y = by() + 22;
		if (planche < SECTIONS.length) {
			String sec = SECTIONS[planche];
			texte(g, Component.translatable("item.airain.livre_ingenieur").withStyle(ChatFormatting.BOLD), gx, y + 2, ROUGE, 1);
			texte(g, Component.translatable("airain.ingenieur.sommaire." + sec).withStyle(ChatFormatting.ITALIC), gx, y + 14, SEPIA, 1);
			for (int s = 0; s < SECTIONS.length; s++) {                     // onglets des sommaires
				int[] o = onglet(s);
				boolean ici = s == planche, survol = mx >= o[0] && mx < o[0] + largeurOnglet(s) && my >= o[1] - 2 && my < o[1] + 10;
				g.drawString(font, Component.translatable("airain.ingenieur.onglet." + SECTIONS[s]).withStyle(ici ? ChatFormatting.UNDERLINE : ChatFormatting.RESET),
					o[0], o[1], ici ? ROUGE : survol ? BLEU : SEPIA, false);
			}
			g.fill(gx, y + 38, gx + LARGE, y + 39, 0xFF9A7046);
			String[][] ch = CHAPITRES[planche];
			for (int i = 0; i < ch.length; i++) {
				int[] l = ligne(i);
				int x = l[0], yy = l[1];
				icone(g, ch[i][1], x, yy - 2f, 0.7f);
				boolean survol = mx >= x && mx < x + LARGE && my >= yy - 2 && my < yy - 2 + PAS;
				g.drawString(font, Component.translatable("airain.ingenieur." + ch[i][0] + ".court"), x + 14, yy, survol ? BLEU : ENCRE, false);
			}
		} else {
			String[] c = TOUS.get(planche - SECTIONS.length);
			String k = "airain.ingenieur." + c[0];
			icone(g, c[1], gx + LARGE / 2f - 16, y + 2, 2f);
			Component t = Component.translatable(k + ".titre").withStyle(ChatFormatting.BOLD);
			if (font.width(t) > LARGE) t = Component.translatable(k + ".court").withStyle(ChatFormatting.BOLD);
			g.drawString(font, t, gx + LARGE / 2 - font.width(t) / 2, y + 38, ENCRE, false);
			g.fill(gx + 10, y + 50, gx + LARGE - 10, y + 51, 0xFF9A7046);
			// le mode d'emploi remplit la page de droite ; s'il est long, la suite passe sous l'histoire, à gauche
			List<FormattedCharSequence> mode = font.split(Component.translatable(k + ".usage"), LARGE);
			boolean long_ = mode.size() > 12;
			int yy = texte(g, Component.translatable(k + ".histoire").withStyle(ChatFormatting.ITALIC), gx, y + 56, SEPIA, long_ ? Math.max(2, 7 - (mode.size() - 12)) : 8);
			g.drawString(font, Component.translatable("airain.ingenieur.mode").withStyle(ChatFormatting.BOLD), dx, y, ROUGE, false);
			for (int i = 0; i < Math.min(12, mode.size()); i++) g.drawString(font, mode.get(i), dx, y + 13 + i * 10, ENCRE, false);
			int ly = yy + 4;
			for (int i = 12; i < mode.size() && ly <= by() + 144; i++, ly += 10) g.drawString(font, mode.get(i), gx, ly, ENCRE, false);
		}
		String n = (planche + 1) + " / " + (dernier() + 1);
		g.drawString(font, n, dx + LARGE / 2 - font.width(n) / 2, by() + 162, SEPIA, false);   // sous la page de droite
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
