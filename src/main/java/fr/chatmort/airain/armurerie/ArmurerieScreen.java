package fr.chatmort.airain.armurerie;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.mojang.blaze3d.systems.RenderSystem;

import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.ItemStack;

/**
 * Écran d'un manuel des armes (Règlement de l'Empire ou Traité de l'Écho), au style des Chroniques :
 * page de garde et sommaire, puis une double page par entrée (à gauche l'objet, son nom et sa devise ;
 * à droite ses caractéristiques, lues sur l'objet lui-même, ses pouvoirs et sa forge).
 * Une entrée jamais portée par l'équipe reste masquée (« ?????????? »).
 */
public class ArmurerieScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registry.png");
	private static final int W = 300, LARGE = 118, LIGNES = 13;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, BLEU = 0x28507A, VIOLET = 0x5A2A7A, GRIS = 0x9A8A78;

	/** Une ligne de page : texte, couleur, page où sauter (-1 : aucune), centrée ; ou une rangée d'objets dessinés en grand. */
	private record Ligne(FormattedCharSequence texte, int couleur, int saut, boolean centre, List<ItemStack> objets) {
		Ligne(FormattedCharSequence t, int c, int s, boolean ce) { this(t, c, s, ce, null); }
	}

	private final boolean echo;
	private final Set<String> vus = new HashSet<>();
	private final List<List<Ligne>> pages = new ArrayList<>();
	private List<Ligne> page;
	private int planche;

	public ArmurerieScreen(boolean echo, CompoundTag donnees) {
		super(Component.translatable(echo ? "item.airain.echo_arms_treatise" : "item.airain.empire_arms_regulations"));
		this.echo = echo;
		for (Tag t : donnees.getList("vus", Tag.TAG_STRING)) vus.add(t.getAsString());
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }
	/** Couleur des titres : rouge pour l'Empire, violet pour l'Écho. */
	private int titreCouleur() { return echo ? VIOLET : ROUGE; }
	private String cle(String suite) { return "airain.armurerie." + suite; }

	// ---- mise en page
	private void nouvellePage() { page = new ArrayList<>(); pages.add(page); }
	private void ligne(Ligne l) { if (page == null || page.size() >= LIGNES) nouvellePage(); page.add(l); }
	private void texte(Component t, int c) { for (FormattedCharSequence s : font.split(t, LARGE)) ligne(new Ligne(s, c, -1, false)); }
	private void centre(Component t, int c) { for (FormattedCharSequence s : font.split(t, LARGE)) ligne(new Ligne(s, c, -1, true)); }
	private void vide() { if (page != null && !page.isEmpty() && page.size() < LIGNES) page.add(new Ligne(FormattedCharSequence.EMPTY, 0, -1, false)); }
	/** La prochaine entrée commence toujours sur une page de gauche (une double page par entrée). */
	private void gauche() { nouvellePage(); if (pages.size() % 2 == 0) nouvellePage(); }

	private static ItemStack objet(String id) { return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("airain", id))); }
	private boolean connue(Armurerie.Entree e) { for (String o : e.objets()) if (vus.contains(o)) return true; return false; }

	/** Les pouvoirs écrits dans les fichiers de langue : p1, p2… jusqu'à la première clé absente. */
	private List<Component> paragraphes(String base) {
		List<Component> l = new ArrayList<>();
		for (int i = 1; I18n.exists(base + ".p" + i); i++) l.add(Component.translatable(base + ".p" + i));
		return l;
	}

	/** Nombre lisible : entier sans décimale, sinon une décimale (virgule en français). */
	private static String nb(double v) {
		String s = Math.abs(v - Math.rint(v)) < 1e-6 ? String.valueOf((long) Math.rint(v)) : String.format(java.util.Locale.ROOT, "%.1f", v);
		var mc = net.minecraft.client.Minecraft.getInstance();
		return mc.options.languageCode.startsWith("fr") ? s.replace('.', ',') : s;
	}

	/** Somme des bonus « + valeur » d'un attribut portés par l'objet (dégâts, vitesse, armure…). */
	private static double attribut(ItemStack s, net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> a) {
		double v = 0;
		for (var e : s.getAttributeModifiers().modifiers())
			if (e.attribute().equals(a) && e.modifier().operation() == AttributeModifier.Operation.ADD_VALUE) v += e.modifier().amount();
		return v;
	}

	private void stat(String nom, String valeur) {
		texte(Component.translatable(cle("stat." + nom)).append(" : ").append(Component.literal(valeur).withStyle(ChatFormatting.BOLD)), ENCRE);
	}

	private void construire() {
		pages.clear();
		List<Armurerie.Entree> entrees = Armurerie.de(echo);
		// page de garde
		nouvellePage();
		vide(); vide();
		centre(title.copy().withStyle(ChatFormatting.BOLD), titreCouleur());
		vide();
		centre(Component.translatable(cle(echo ? "sous_titre.echo" : "sous_titre.empire")).withStyle(ChatFormatting.ITALIC), SEPIA);
		vide(); vide();
		int connues = 0;
		for (Armurerie.Entree e : entrees) if (connue(e)) connues++;
		centre(Component.translatable(cle("compte"), connues, entrees.size()), ENCRE);
		// sommaire sur deux pages (1 et 2), préambule en page 3 ; les sauts sont remplis après, une fois les pages placées
		nouvellePage(); List<Ligne> sommaire1 = page;
		nouvellePage(); List<Ligne> sommaire2 = page;
		nouvellePage();
		vide(); vide();
		centre(Component.translatable(cle(echo ? "preambule.echo" : "preambule.empire")).withStyle(ChatFormatting.ITALIC), SEPIA);
		// une double page par entrée
		int[] debut = new int[entrees.size()];
		for (int i = 0; i < entrees.size(); i++) {
			Armurerie.Entree e = entrees.get(i);
			gauche();
			debut[i] = pages.size() - 1;
			if (!connue(e)) {
				vide(); vide(); vide();
				centre(Component.literal("??????????").withStyle(ChatFormatting.BOLD), GRIS);
				vide();
				centre(Component.translatable(cle("inconnue")).withStyle(ChatFormatting.ITALIC), GRIS);
				continue;
			}
			entree(e);
		}
		// sommaire : une ligne par entrée, cliquable si connue
		sommaire1.add(new Ligne(Component.translatable(cle("sommaire")).withStyle(ChatFormatting.BOLD).getVisualOrderText(), titreCouleur(), -1, true));
		sommaire1.add(new Ligne(FormattedCharSequence.EMPTY, 0, -1, false));
		for (int i = 0; i < entrees.size(); i++) {
			Armurerie.Entree e = entrees.get(i);
			List<Ligne> cible = sommaire1.size() < LIGNES ? sommaire1 : sommaire2;
			Component nom = connue(e) ? nomEntree(e) : Component.literal("??????????");
			cible.add(new Ligne(font.split(Component.literal("· ").append(nom), LARGE).get(0), connue(e) ? ENCRE : GRIS, connue(e) ? debut[i] : -1, false));
		}
	}

	/** Le nom d'une entrée : celui de l'arme, ou le titre de la page pour un ensemble ou des coiffes. */
	private Component nomEntree(Armurerie.Entree e) {
		return e.sorte() == Armurerie.Sorte.ARME ? objet(e.objets().get(0)).getHoverName() : Component.translatable(cle(e.cle() + ".titre"));
	}

	/** Une double page : à gauche l'objet et sa devise, à droite ses caractéristiques et ses pouvoirs. */
	private void entree(Armurerie.Entree e) {
		List<ItemStack> objets = new ArrayList<>();
		for (String o : e.objets()) objets.add(objet(o));
		// page de gauche
		ligne(new Ligne(FormattedCharSequence.EMPTY, 0, -1, true, objets));
		vide(); vide(); vide();
		centre(nomEntree(e).copy().withStyle(ChatFormatting.BOLD), titreCouleur());
		centre(Component.translatable(cle(e.cle() + ".sous_titre")).withStyle(ChatFormatting.ITALIC), SEPIA);
		vide();
		texte(Component.translatable(cle(e.cle() + ".citation")).withStyle(ChatFormatting.ITALIC), ENCRE);
		// page de droite
		nouvellePage();
		texte(Component.translatable(cle("caracteristiques")).withStyle(ChatFormatting.BOLD), titreCouleur());
		switch (e.sorte()) {
			case ARME -> {
				ItemStack s = objets.get(0);
				stat("degats", nb(1 + attribut(s, Attributes.ATTACK_DAMAGE)));
				stat("vitesse", nb(4 + attribut(s, Attributes.ATTACK_SPEED)));
				double portee = attribut(s, Attributes.ENTITY_INTERACTION_RANGE), recul = attribut(s, Attributes.ATTACK_KNOCKBACK),
					balayage = attribut(s, Attributes.SWEEPING_DAMAGE_RATIO);
				if (portee != 0) stat("portee", "+" + nb(portee));
				if (recul != 0) stat("recul", "+" + nb(recul));
				if (balayage != 0) stat("balayage", "+" + nb(balayage * 100) + " %");
				if (s.getMaxDamage() > 0) stat("durabilite", String.valueOf(s.getMaxDamage()));
			}
			case ENSEMBLE, COIFFE -> {
				double armure = 0, robustesse = 0, recul = 0;
				for (ItemStack s : objets) {
					double a = attribut(s, Attributes.ARMOR);
					texte(Component.literal("· ").append(s.getHoverName()).append(" : " + nb(a)), ENCRE);
					armure += a; robustesse += attribut(s, Attributes.ARMOR_TOUGHNESS); recul += attribut(s, Attributes.KNOCKBACK_RESISTANCE);
				}
				if (e.sorte() == Armurerie.Sorte.ENSEMBLE) {
					stat("armure", nb(armure));
					stat("robustesse", nb(robustesse));
					if (recul != 0) stat("recul_resistance", nb(recul * 100) + " %");
				}
			}
		}
		vide();
		List<Component> pouvoirs = paragraphes(cle(e.cle()));
		if (!pouvoirs.isEmpty()) {
			texte(Component.translatable(cle(e.sorte() == Armurerie.Sorte.ENSEMBLE ? "ensemble" : "pouvoirs")).withStyle(ChatFormatting.BOLD), titreCouleur());
			for (Component p : pouvoirs) { texte(p, ENCRE); vide(); }
		}
		if (I18n.exists(cle(e.cle() + ".forge"))) texte(Component.translatable(cle(e.cle() + ".forge")).withStyle(ChatFormatting.ITALIC), SEPIA);
		texte(Component.translatable(cle(echo ? "reserve.echo" : "reserve.empire")).withStyle(ChatFormatting.ITALIC), SEPIA);
	}

	// ---- navigation, comme les Chroniques
	private WidgetsEmpire.Fleche avant, apres;
	private WidgetsEmpire.Signet signet;

	@Override
	protected void init() {
		if (pages.isEmpty()) construire();
		avant = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> aller(planche - 1)));
		apres = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> aller(planche + 1)));
		signet = addRenderableWidget(new WidgetsEmpire.Signet(bx(), by(), b -> aller(0)));
	}

	private int planches() { return (pages.size() + 1) / 2; }

	private void aller(int n) {
		n = Mth.clamp(n, 0, planches() - 1);
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

	private int px(int cote) { return cote == 0 ? bx() + 20 : bx() + 162; }

	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		for (int cote = 0; cote < 2; cote++) {
			int k = planche * 2 + cote;
			if (k >= pages.size()) continue;
			List<Ligne> p = pages.get(k);
			for (int i = 0; i < p.size(); i++) {
				int x = px(cote), y = by() + 18 + i * 10;
				if (mx < x || mx >= x + LARGE || my < y - 1 || my >= y + 9) continue;
				if (p.get(i).saut() >= 0) { aller(p.get(i).saut() / 2); return true; }
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

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		avant.visible = planche > 0;
		apres.visible = planche < planches() - 1;
		signet.visible = planche > 0;
		super.render(g, mx, my, pt);
		for (int cote = 0; cote < 2; cote++) {
			int k = planche * 2 + cote;
			if (k >= pages.size()) continue;
			List<Ligne> p = pages.get(k);
			for (int i = 0; i < p.size(); i++) {
				Ligne l = p.get(i);
				int x = px(cote), y = by() + 18 + i * 10;
				if (l.objets() != null) { objets(g, l.objets(), x, y); continue; }
				boolean survol = l.saut() >= 0 && mx >= x && mx < x + LARGE && my >= y - 1 && my < y + 9;
				int c = survol ? BLEU : l.couleur();
				if (l.centre()) x += (LARGE - font.width(l.texte())) / 2;
				g.drawString(font, l.texte(), x, y, c, false);
				if (survol) g.fill(x, y + 9, x + font.width(l.texte()), y + 10, 0xFF000000 | BLEU);
			}
		}
		for (int cote = 0; cote < 2; cote++) {                 // numéro sous chaque page
			int k = planche * 2 + cote;
			if (k >= pages.size()) break;
			String n = String.valueOf(k + 1);
			g.drawString(font, n, px(cote) + LARGE / 2 - font.width(n) / 2, by() + 162, SEPIA, false);
		}
	}

	/** Les objets d'une entrée, côte à côte et centrés : en grand pour une arme, plus petits pour un ensemble. */
	private void objets(GuiGraphics g, List<ItemStack> l, int x, int y) {
		float e = l.size() == 1 ? 2.5f : l.size() == 2 ? 2f : l.size() == 3 ? 1.75f : 1.5f;
		float pas = 16 * e + 4, total = pas * l.size() - 4;
		g.pose().pushPose();
		g.pose().translate(x + (LARGE - total) / 2f, y - 2, 0);
		g.pose().scale(e, e, 1);
		for (int i = 0; i < l.size(); i++) g.renderItem(l.get(i), Math.round(i * pas / e), 0);
		g.pose().popPose();
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
