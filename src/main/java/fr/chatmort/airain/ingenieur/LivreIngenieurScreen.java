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
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registry.png");
	private static final int W = 300, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, BLEU = 0x28507A;

	/** Sections : clé du sommaire, puis chapitres {clé de texte, objet illustré}. */
	static final String[] SECTIONS = {"machines", "objets", "empire", "echo", "fusion"};   // fusion : les machines qui marient Create et Ars
	static final String[][][] CHAPITRES = {
		{{"fondation", "airain:foundation_stone"}, {"grand_etendard", "airain:great_standard"}, {"banniere_murale", "airain:foundation_wall_banner"},
		 {"gabarit", "airain:banner_template"}, {"registre", "airain:foundation_registry"}, {"socle", "airain:trophy_pedestal"},
		 {"banc", "airain:maintenance_bench"}, {"modules", "airain:fine_grindstone"}, {"table", "airain:imperial_enchanting_table"},
		 {"desenchanteur", "airain:disenchanter"}, {"balise", "airain:defense_beacon"}, {"gardien", "airain:guardian_spawn_egg"},
		 {"modules_gardien", "airain:lantern_module"}, {"haut_fourneau", "airain:blast_furnace_taphole"}, {"style_imperial", "airain:chiseled_airain"}, {"passerelles", "airain:airain_catwalk"}, {"conduite_air", "airain:airain_air_vent"}, {"atelier", "airain:airain_workbench"}, {"mecanismes", "airain:airain_lift_winch"}, {"mecanique", "airain:airain_load_reliever"}},
		{{"codex", "airain:codex"}, {"chroniques", "airain:chronicles"}, {"reliure", "airain:binder"}, {"manuels", "airain:imperial_arms_regulations"}, {"tableau", "airain:duty_board"},
		 {"atlas", "airain:atlas"}, {"affiches", "airain:blank_poster"}, {"cartes", "airain:empire_map"},
		 {"encre", "airain:runic_ink"}, {"schemas", "kubejs:schema_cuivre"}, {"sceau", "kubejs:sceau_forge"},
		 {"memoires", "kubejs:coeur_d_airain"}, {"resonance", "kubejs:fragment_resonance"}, {"recuperation", "kubejs:ferraille"},
		 {"plaque_netherite", "kubejs:plaque_netherite"}, {"airain", "airain:airain_ingot"}},
		{{"sacre", "airain:sacred_netherite_plate"}, {"couronne", "airain:airain_crown"}, {"capitale_sacree", "airain:foundation_stone"}, {"ameliorations", "airain:expansion_plans"}, {"etoile", "airain:star_block"},
		 {"armure_sacree", "airain:sacred_chestplate"}, {"armure_imperiale", "airain:imperial_chestplate"}, {"armes_sacrees", "airain:sacred_katana"},
		 {"armes_imperiales", "airain:imperial_katana"}, {"sceptre_imperial", "airain:imperial_scepter"}, {"capitaine", "airain:imperial_plate"},
		 {"trone", "airain:imperial_throne"}, {"borne_imperiale", "airain:difference_engine"}, {"charte", "airain:imperial_charter"}},
		{{"diademe", "airain:echo_diadem"}, {"capitale_arcanique", "airain:foundation_stone"}, {"ameliorations", "airain:expansion_plans"}, {"arcanium", "airain:arcanium_ingot"},
		 {"armure_runique", "airain:runic_chestplate"}, {"armure_arcanique", "airain:arcane_chestplate"}, {"armes_runiques", "airain:runic_katana"},
		 {"armes_arcaniques", "airain:arcane_katana"}, {"sceptre_arcanique", "airain:arcane_scepter"}, {"gardien_echo", "airain:primordial_echo_block"},
		 {"solium", "airain:solium"}, {"borne_arcanique", "airain:resonant_archive"}, {"relais", "kubejs:diapason_echo"}},
		// Machines d'Écho : le pont entre Create et Ars Nouveau
		{{"turbine_echo", "airain:echo_turbine"}, {"sourcelink_meca", "airain:mechanical_sourcelink"}, {"diffuseur_echo", "airain:echo_diffuser"},
		 {"condenseur_echo", "airain:echo_condenser"}, {"glyphe_engrenage", "airain:glyph_gear"}}};
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
	/** Sommaire : 5 lignes à gauche (sous le titre et les onglets), le reste à droite ; pas de 14 px. */
	private static final int GAUCHE = 5, PAS = 14, LIGNES = 12;
	/** Pages des chapitres : {chapitre, texte (1 : « .usage », 2 : « .usage2 »), première ligne}. Un texte trop long continue sur la double page suivante. */
	private final List<int[]> pages = new ArrayList<>();
	private final int[] premiere = new int[256];
	private int planche;
	private WidgetsEmpire.Fleche avant, apres;
	private WidgetsEmpire.Signet signet;

	public LivreIngenieurScreen() { super(Component.translatable("item.airain.engineers_manual")); }

	private void paginer() {
		pages.clear();
		for (int i = 0; i < TOUS.size(); i++) {
			premiere[i] = pages.size();
			for (int partie = 1; partie <= 2; partie++) {
				String k = "airain.ingenieur." + TOUS.get(i)[0] + (partie == 1 ? ".usage" : ".usage2");
				if (partie == 2 && !net.minecraft.client.resources.language.I18n.exists(k)) break;
				int n = Math.max(1, font.split(Component.translatable(k), LARGE).size());
				for (int d = 0; d < n; d += LIGNES) pages.add(new int[] {i, partie, d});
			}
		}
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }
	private int dernier() { return SECTIONS.length + pages.size() - 1; }

	@Override
	protected void init() {
		paginer();
		planche = Math.min(planche, dernier());
		avant = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> aller(planche - 1)));
		apres = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> aller(planche + 1)));
		signet = addRenderableWidget(new WidgetsEmpire.Signet(bx(), by(), b -> aller(planche >= SECTIONS.length ? SECTION_DE.get(pages.get(planche - SECTIONS.length)[0]) : 0)));
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
		return i < GAUCHE ? new int[] {bx() + 20, by() + 22 + 56 + i * PAS} : new int[] {bx() + 162, by() + 22 + 2 + (i - GAUCHE) * PAS};
	}

	/** Onglets des cinq sommaires, en bas de la page de gauche. */
	private int[] onglet(int s) {
		int x = bx() + 20;
		for (int i = s - s % 3; i < s; i++) x += largeurOnglet(i) + 10;   // trois onglets par ligne
		return new int[] {x, by() + 22 + 26 + (s / 3) * 11};
	}

	private int largeurOnglet(int s) { return font.width(Component.translatable("airain.ingenieur.onglet." + SECTIONS[s])); }

	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (planche < SECTIONS.length) {
			String[][] ch = CHAPITRES[planche];
			for (int i = 0; i < ch.length; i++) {
				int[] l = ligne(i);
				if (mx >= l[0] && mx < l[0] + LARGE && my >= l[1] - 2 && my < l[1] - 2 + PAS) { aller(SECTIONS.length + premiere[DEBUT[planche] + i]); return true; }
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
			texte(g, Component.translatable("item.airain.engineers_manual").withStyle(ChatFormatting.BOLD), gx, y + 2, ROUGE, 1);
			texte(g, Component.translatable("airain.ingenieur.sommaire." + sec).withStyle(ChatFormatting.ITALIC), gx, y + 14, SEPIA, 1);
			for (int s = 0; s < SECTIONS.length; s++) {                     // onglets des sommaires
				int[] o = onglet(s);
				boolean ici = s == planche, survol = mx >= o[0] && mx < o[0] + largeurOnglet(s) && my >= o[1] - 2 && my < o[1] + 10;
				g.drawString(font, Component.translatable("airain.ingenieur.onglet." + SECTIONS[s]).withStyle(ici ? ChatFormatting.UNDERLINE : ChatFormatting.RESET),
					o[0], o[1], ici ? ROUGE : survol ? BLEU : SEPIA, false);
			}
			g.fill(gx, y + 49, gx + LARGE, y + 50, 0xFF9A7046);
			String[][] ch = CHAPITRES[planche];
			for (int i = 0; i < ch.length; i++) {
				int[] l = ligne(i);
				int x = l[0], yy = l[1];
				icone(g, ch[i][1], x, yy - 3f, 0.8f);
				boolean survol = mx >= x && mx < x + LARGE && my >= yy - 2 && my < yy - 2 + PAS;
				g.drawString(font, Component.translatable("airain.ingenieur." + ch[i][0] + ".court"), x + 16, yy, survol ? BLEU : ENCRE, false);
			}
		} else {
			int[] pg = pages.get(planche - SECTIONS.length);
			String[] c = TOUS.get(pg[0]);
			String k = "airain.ingenieur." + c[0];
			icone(g, c[1], gx + LARGE / 2f - 16, y + 2, 2f);
			Component t = Component.translatable(k + ".titre").withStyle(ChatFormatting.BOLD);
			if (font.width(t) > LARGE) t = Component.translatable(k + ".court").withStyle(ChatFormatting.BOLD);
			g.drawString(font, t, gx + LARGE / 2 - font.width(t) / 2, y + 38, ENCRE, false);
			g.fill(gx + 10, y + 50, gx + LARGE - 10, y + 51, 0xFF9A7046);
			boolean suite = pages.get(planche - SECTIONS.length - 1 >= 0 ? planche - SECTIONS.length - 1 : 0)[0] == pg[0] && planche - SECTIONS.length > 0;
			if (suite) texte(g, Component.translatable("airain.ingenieur.suite").withStyle(ChatFormatting.ITALIC), gx, y + 56, SEPIA, 1);
			else texte(g, Component.translatable(k + ".histoire").withStyle(ChatFormatting.ITALIC), gx, y + 56, SEPIA, 7);
			// en-tête : « Mode d'emploi » pour les machines et objets, « Effets » pour ce qui est réservé à une fin
			String tete = SECTION_DE.get(pg[0]) >= 2 ? "airain.ingenieur.effets" : "airain.ingenieur.mode";
			g.drawString(font, Component.translatable(tete).withStyle(ChatFormatting.BOLD), dx, y, ROUGE, false);
			List<FormattedCharSequence> l = font.split(Component.translatable(k + (pg[1] == 2 ? ".usage2" : ".usage")), LARGE);
			for (int i = pg[2]; i < Math.min(l.size(), pg[2] + LIGNES); i++) g.drawString(font, l.get(i), dx, y + 13 + (i - pg[2]) * 10, ENCRE, false);
		}
		String n = (planche + 1) + " / " + (dernier() + 1);
		g.drawString(font, n, dx + LARGE / 2 - font.width(n) / 2, by() + 162, SEPIA, false);   // sous la page de droite
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
