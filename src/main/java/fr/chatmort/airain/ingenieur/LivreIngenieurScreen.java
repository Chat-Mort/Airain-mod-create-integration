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
 * Le livre de l'ingénieur, au style du registre. Cinq sommaires (blocs, objets, fin de l'Empire, fin de l'Écho, industrie),
 * chacun sur une double page ; un clic mène au chapitre. Chaque chapitre : à gauche l'objet, son nom et une phrase
 * d'histoire, puis le mode d'emploi (balisé : intertitres, puces, icônes) qui coule sur la gauche puis la droite.
 */
public class LivreIngenieurScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registry.png");
	private static final int W = 300, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, BLEU = 0x28507A;

	/** Sections : clé du sommaire, puis chapitres {clé de texte, objet illustré}. 14 chapitres au plus par sommaire (5 à gauche, 9 à droite). */
	static final String[] SECTIONS = {"machines", "objets", "empire", "echo", "industrie"};
	static final String[][][] CHAPITRES = {
		{{"fondation", "airain:foundation_stone"}, {"grand_etendard", "airain:great_standard"}, {"banniere_murale", "airain:foundation_wall_banner"},
		 {"gabarit", "airain:banner_template"}, {"registre", "airain:foundation_registry"}, {"socle", "airain:trophy_pedestal"},
		 {"banc", "airain:maintenance_bench"}, {"modules", "airain:fine_grindstone"}, {"table", "airain:imperial_enchanting_table"},
		 {"desenchanteur", "airain:disenchanter"}, {"balise", "airain:defense_beacon"}, {"gardien", "airain:guardian_spawn_egg"},
		 {"modules_gardien", "airain:lantern_module"}},
		{{"codex", "airain:codex"}, {"chroniques", "airain:chronicles"}, {"reliure", "airain:binder"}, {"manuels", "airain:imperial_arms_regulations"}, {"tableau", "airain:duty_board"},
		 {"atlas", "airain:atlas"}, {"affiches", "airain:blank_poster"}, {"cartes", "airain:empire_map"},
		 {"encre", "airain:runic_ink"}, {"schemas", "kubejs:schema_cuivre"}, {"sceau", "kubejs:sceau_forge"},
		 {"memoires", "kubejs:coeur_d_airain"}, {"resonance", "kubejs:fragment_resonance"}, {"plaque_netherite", "kubejs:plaque_netherite"}},
		{{"sacre", "airain:sacred_netherite_plate"}, {"couronne", "airain:airain_crown"}, {"capitale_sacree", "airain:foundation_stone"}, {"ameliorations", "airain:expansion_plans"}, {"etoile", "airain:star_block"},
		 {"armure_sacree", "airain:sacred_chestplate"}, {"armure_imperiale", "airain:imperial_chestplate"}, {"armes_sacrees", "airain:sacred_katana"},
		 {"armes_imperiales", "airain:imperial_katana"}, {"sceptre_imperial", "airain:imperial_scepter"}, {"capitaine", "airain:imperial_plate"},
		 {"trone", "airain:imperial_throne"}, {"borne_imperiale", "airain:difference_engine"}, {"charte", "airain:imperial_charter"}},
		{{"diademe", "airain:echo_diadem"}, {"capitale_arcanique", "airain:foundation_stone"}, {"ameliorations", "airain:expansion_plans"}, {"arcanium", "airain:arcanium_ingot"},
		 {"armure_runique", "airain:runic_chestplate"}, {"armure_arcanique", "airain:arcane_chestplate"}, {"armes_runiques", "airain:runic_katana"},
		 {"armes_arcaniques", "airain:arcane_katana"}, {"sceptre_arcanique", "airain:arcane_scepter"}, {"gardien_echo", "airain:primordial_echo_block"},
		 {"solium", "airain:solium"}, {"borne_arcanique", "airain:resonant_archive"}, {"relais", "kubejs:diapason_echo"}},
		// l'industrie : l'airain et ce qu'on en tire, et les machines qui marient Create et Ars
		{{"airain", "airain:airain_ingot"}, {"recuperation", "kubejs:ferraille"}, {"haut_fourneau", "airain:blast_furnace_taphole"}, {"style_imperial", "airain:chiseled_airain"},
		 {"passerelles", "airain:airain_catwalk"}, {"conduite_air", "airain:airain_air_vent"}, {"atelier", "airain:airain_workbench"}, {"mecanismes", "airain:airain_lift_winch"},
		 {"mecanique", "airain:airain_load_reliever"}, {"turbine_echo", "airain:echo_turbine"}, {"sourcelink_meca", "airain:mechanical_sourcelink"}, {"diffuseur_echo", "airain:echo_diffuser"},
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
	/** Sommaire : 5 lignes à gauche (sous le titre et les onglets), 9 à droite ; pas de 14 px. */
	private static final int GAUCHE = 5, PAS = 14;
	private static final int FILET = 0xFF9A7046;

	// ------------------------------------------------------------------ texte balisé du mode d'emploi
	/*
	 * Une ligne de la clé « .usage » par paragraphe (séparés par \n) :
	 *   « ## Titre »   intertitre rouge souligné
	 *   « - texte »    puce
	 *   « @id texte »  l'icône de l'objet id, puis le texte
	 *   ligne vide     petit blanc
	 *   sinon          texte courant (les codes § de Minecraft marchent : §l gras, §r normal)
	 */
	private static final int TITRE = 0, PUCE = 1, OBJET = 2, TEXTE = 3, VIDE = 4;
	/** Une ligne affichable : type, texte, icône (ou null), première ligne de son entrée, hauteur. */
	private record Ligne(int type, FormattedCharSequence t, String id, boolean tete, int haut) {}
	private List<Ligne> lignes(String brut) {
		List<Ligne> r = new ArrayList<>();
		for (String par : brut.split("\n")) {
			if (par.isBlank()) { r.add(new Ligne(VIDE, null, null, true, 5)); continue; }
			int type = TEXTE, retrait = 0; String id = null, t = par;
			if (par.startsWith("## ")) { type = TITRE; t = "§l" + par.substring(3); }
			else if (par.startsWith("- ")) { type = PUCE; t = par.substring(2); retrait = 8; }
			else if (par.startsWith("@") && par.indexOf(' ') > 1) { type = OBJET; id = par.substring(1, par.indexOf(' ')); t = par.substring(par.indexOf(' ') + 1); retrait = 13; }
			List<FormattedCharSequence> l = font.split(FormattedText.of(t), LARGE - retrait);
			for (int k = 0; k < l.size(); k++)
				r.add(new Ligne(type, l.get(k), k == 0 ? id : null, k == 0, type == TITRE ? 13 : type == OBJET && k == 0 ? 11 : 10));
		}
		return r;
	}
	/** Fin de l'entrée qui commence en i (ses lignes de suite ; un intertitre emmène l'entrée qui le suit). */
	private static int finEntree(List<Ligne> L, int i) {
		int j = i + 1;
		while (j < L.size() && !L.get(j).tete()) j++;
		if (L.get(i).type() == TITRE && j < L.size() && L.get(j).type() != TITRE) return finEntree(L, j);
		return j;
	}
	/** Remplit une colonne de y0 à bas à partir de la ligne i ; renvoie l'indice de la première ligne qui n'y tient pas. */
	private static int colonne(List<Ligne> L, int i, int y0, int bas) {
		int h = y0;
		while (i < L.size()) {
			if (h == y0 && L.get(i).type() == VIDE) { i++; continue; }
			int j = finEntree(L, i), hh = 0;
			for (int k = i; k < j; k++) hh += L.get(k).haut();
			if (h + hh > bas) {
				if (h == y0) j = i + 1; else break;           // une entrée plus haute qu'une colonne : on la coupe
				hh = L.get(i).haut();
			}
			h += hh; i = j;
		}
		return i;
	}
	private static final int BAS_G = 136, BAS_D = 128, SUITE = 19;
	/** Haut du texte sur la page de gauche de la première double page (sous l'icône, le titre et l'histoire). */
	private int debutTexte(String k) { return 28 + Math.min(3, font.split(Component.translatable(k + ".histoire"), LARGE).size()) * 10 + 7; }

	/** Doubles pages des chapitres : {chapitre, première ligne à gauche, première ligne à droite, fin}. */
	private final List<int[]> pages = new ArrayList<>();
	private final List<List<Ligne>> textes = new ArrayList<>();
	private final int[] premiere = new int[256];
	private int planche;
	private WidgetsEmpire.Fleche avant, apres;
	private WidgetsEmpire.Signet signet;

	public LivreIngenieurScreen() { super(Component.translatable("item.airain.engineers_manual")); }

	private void paginer() {
		pages.clear(); textes.clear();
		for (int c = 0; c < TOUS.size(); c++) {
			String k = "airain.ingenieur." + TOUS.get(c)[0];
			List<Ligne> L = lignes(Component.translatable(k + ".usage").getString());
			textes.add(L);
			premiere[c] = pages.size();
			int i = 0; boolean prem = true;
			do {
				int a = i, m = colonne(L, i, prem ? debutTexte(k) : SUITE, BAS_G), f = colonne(L, m, 0, BAS_D);
				pages.add(new int[] {c, a, m, f});
				i = f; prem = false;
			} while (i < L.size());
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

	/** Dessine les lignes [a, b) en colonne à partir de (x, y). */
	private void dessiner(GuiGraphics g, List<Ligne> L, int a, int b, int x, int y) {
		boolean debut = true;
		for (int i = a; i < b; i++) {
			Ligne l = L.get(i);
			if (debut && l.type() == VIDE) continue;
			debut = false;
			switch (l.type()) {
				case TITRE -> { g.drawString(font, l.t(), x, y + 2, ROUGE, false); g.fill(x, y + 11, x + LARGE, y + 12, FILET); }
				case PUCE -> { if (l.tete()) g.drawString(font, "•", x + 1, y, ROUGE, false); g.drawString(font, l.t(), x + 8, y, ENCRE, false); }
				case OBJET -> { if (l.id() != null) icone(g, l.id(), x, y - 1, 0.625f); g.drawString(font, l.t(), x + 13, y + (l.id() != null ? 1 : 0), ENCRE, false); }
				case TEXTE -> g.drawString(font, l.t(), x, y, ENCRE, false);
				default -> { }
			}
			y += l.haut();
		}
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
			g.fill(gx, y + 49, gx + LARGE, y + 50, FILET);
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
			List<Ligne> L = textes.get(pg[0]);
			boolean prem = premiere[pg[0]] == planche - SECTIONS.length;
			int g0;
			if (prem) {
				// en-tête : l'icône, le titre à côté (sur deux lignes au besoin), l'histoire en italique, un filet
				icone(g, c[1], gx, y, 1.5f);
				List<FormattedCharSequence> titre = font.split(Component.translatable(k + ".court").withStyle(ChatFormatting.BOLD), LARGE - 28);
				for (int i = 0; i < Math.min(2, titre.size()); i++) g.drawString(font, titre.get(i), gx + 28, y + (titre.size() == 1 ? 8 : 3) + i * 10, ENCRE, false);
				int yy = texte(g, Component.translatable(k + ".histoire").withStyle(ChatFormatting.ITALIC), gx, y + 28, SEPIA, 3);
				g.fill(gx, yy + 2, gx + LARGE, yy + 3, FILET);
				g0 = debutTexte(k);
			} else {
				icone(g, c[1], gx, y, 0.75f);
				g.drawString(font, Component.translatable(k + ".court").append(" ").append(Component.translatable("airain.ingenieur.suite")).withStyle(ChatFormatting.ITALIC), gx + 15, y + 2, SEPIA, false);
				g.fill(gx, y + 14, gx + LARGE, y + 15, FILET);
				g0 = SUITE;
			}
			dessiner(g, L, pg[1], pg[2], gx, y + g0);
			dessiner(g, L, pg[2], pg[3], dx, y);
		}
		String n = (planche + 1) + " / " + (dernier() + 1);
		g.drawString(font, n, dx + LARGE / 2 - font.width(n) / 2, by() + 162, SEPIA, false);   // sous la page de droite
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
