package fr.chatmort.airain.manuel;

import java.util.ArrayList;
import java.util.List;

import com.mojang.blaze3d.systems.RenderSystem;

import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;

/**
 * Écran d'un manuel d'armes, au style des Chroniques : page de garde, sommaire (les pages pas encore dévoilées restent
 * « ?????????? »), puis une page par arme, coiffe ou ensemble d'armure. Les caractéristiques sont lues sur l'objet
 * lui-même (dégâts, vitesse, portée, protection…) : elles restent justes si l'on change les chiffres dans le code.
 */
public class ManuelScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registry.png");
	private static final int W = 300, LARGE = 118, LIGNES = 13;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, GRIS = 0x9A8A78, BLEU = 0x28507A;

	/** Une ligne : texte, couleur, page où sauter (-1 : aucune), centrée, et un objet dessiné en grand (icône de page). */
	private record Ligne(FormattedCharSequence texte, int couleur, int saut, boolean centre, ItemStack icone) {}

	private final int camp;
	private final List<String> devoilees;
	private final int accent;   // rouge de l'Empire, violet de l'Écho
	private final List<List<Ligne>> pages = new ArrayList<>();
	private List<Ligne> page;
	private int planche;

	public ManuelScreen(OuvrirManuel m) {
		super(Component.translatable(nomLivre(m.camp())));
		this.camp = m.camp();
		this.devoilees = m.pages();
		this.accent = camp == Manuel.EMPIRE ? 0x8A1A14 : 0x5A2A82;
	}

	private static String nomLivre(int camp) { return "item.airain." + (camp == Manuel.EMPIRE ? "imperial_arms_regulations" : "echo_arms_treatise"); }

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }

	// ---- mise en page (comme les Chroniques)
	private void nouvellePage() { page = new ArrayList<>(); pages.add(page); }
	private void ligne(Ligne l) { if (page == null || page.size() >= LIGNES) nouvellePage(); page.add(l); }
	private void texte(Component t, int c) { for (FormattedCharSequence s : font.split(t, LARGE)) ligne(new Ligne(s, c, -1, false, null)); }
	private void centre(Component t, int c) { for (FormattedCharSequence s : font.split(t, LARGE)) ligne(new Ligne(s, c, -1, true, null)); }
	private void vide() { if (page != null && !page.isEmpty() && page.size() < LIGNES) page.add(new Ligne(FormattedCharSequence.EMPTY, 0, -1, false, null)); }

	private static ItemStack pile(String id) { return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(id))); }
	private static Component tr(String cle, Object... a) { return Component.translatable(cle, a); }
	private static String n(double v) { return v == Math.rint(v) ? String.valueOf((long) v) : String.format(java.util.Locale.ROOT, "%.1f", v).replace('.', ','); }

	private void construire() {
		pages.clear();
		List<Manuel.Entree> miennes = new ArrayList<>();
		for (Manuel.Entree e : Manuel.ENTREES) if (e.camp() == camp) miennes.add(e);
		// page de garde
		nouvellePage();
		vide(); vide();
		centre(tr(nomLivre(camp)).copy().withStyle(ChatFormatting.BOLD), accent);
		vide();
		centre(tr("airain.manuel.sous_titre." + camp).copy().withStyle(ChatFormatting.ITALIC), SEPIA);
		vide();
		int vues = 0;
		for (Manuel.Entree e : miennes) if (devoilees.contains(e.cle())) vues++;
		centre(tr("airain.manuel.compte", vues, miennes.size()), ENCRE);
		vide();
		texte(tr("airain.manuel.preambule." + camp).copy().withStyle(ChatFormatting.ITALIC), ENCRE);
		// les fiches d'abord, à part, pour connaître leur place dans le livre
		List<List<Ligne>> garde = new ArrayList<>(pages);
		pages.clear(); page = null;
		int[] debutFiche = new int[miennes.size()];
		for (int i = 0; i < miennes.size(); i++) {
			Manuel.Entree e = miennes.get(i);
			if (!devoilees.contains(e.cle())) { debutFiche[i] = -1; continue; }
			if (pages.size() % 2 == 1) nouvellePage();   // chaque fiche commence sur une page de gauche
			nouvellePage();
			debutFiche[i] = pages.size() - 1;
			fiche(e);
		}
		List<List<Ligne>> fiches = new ArrayList<>(pages);
		// le sommaire, après la page de garde : chaque titre dévoilé renvoie à sa fiche
		pages.clear(); pages.addAll(garde); page = null;
		nouvellePage();
		centre(tr("airain.livre.sommaire").copy().withStyle(ChatFormatting.BOLD), accent);
		List<int[]> renvois = new ArrayList<>();   // {page, ligne, n° de fiche}
		String section = "";
		for (int i = 0; i < miennes.size(); i++) {
			Manuel.Entree e = miennes.get(i);
			if (!e.section().equals(section)) {
				section = e.section();
				vide();
				texte(tr("airain.manuel.section." + section).copy().withStyle(ChatFormatting.UNDERLINE), ENCRE);
			}
			if (debutFiche[i] < 0) { ligne(new Ligne(Component.literal("  ??????????").getVisualOrderText(), GRIS, -1, false, null)); continue; }
			ligne(new Ligne(Component.literal("• ").append(tr("airain.manuel." + e.cle() + ".titre")).getVisualOrderText(), BLEU, 0, false, null));
			renvois.add(new int[] {pages.size() - 1, page.size() - 1, debutFiche[i]});
		}
		if (pages.size() % 2 == 1) nouvellePage();   // les fiches commencent sur une page de gauche
		int decalage = pages.size();
		for (int[] r : renvois) {
			Ligne l = pages.get(r[0]).get(r[1]);
			pages.get(r[0]).set(r[1], new Ligne(l.texte(), l.couleur(), decalage + r[2], false, null));
		}
		pages.addAll(fiches);
	}

	/** La page d'une arme, d'une coiffe ou d'un ensemble. */
	private void fiche(Manuel.Entree e) {
		String k = "airain.manuel." + e.cle();
		ItemStack icone = pile(e.ensemble() ? e.objets()[1] : e.objets()[0]);
		ligne(new Ligne(FormattedCharSequence.EMPTY, 0, -1, true, icone));   // l'objet, dessiné en grand sur deux lignes
		vide();
		centre(tr(k + ".titre").copy().withStyle(ChatFormatting.BOLD), accent);
		centre(tr(k + ".sous_titre").copy().withStyle(ChatFormatting.ITALIC), SEPIA);
		vide();
		texte(Component.literal("« ").append(tr(k + ".devise")).append(" »").withStyle(ChatFormatting.ITALIC), ENCRE);
		vide();
		List<Component> stats = e.ensemble() ? statsEnsemble(e) : stats(icone);
		if (!stats.isEmpty()) {
			texte(tr("airain.manuel.caracteristiques").copy().withStyle(ChatFormatting.BOLD), accent);
			for (Component c : stats) texte(c, ENCRE);
			vide();
		}
		texte(tr(e.ensemble() ? "airain.manuel.effets" : "airain.manuel.pouvoirs").copy().withStyle(ChatFormatting.BOLD), accent);
		texte(tr(k + ".pouvoir"), ENCRE);
		vide();
		texte(tr(k + ".forge").copy().withStyle(ChatFormatting.ITALIC), SEPIA);
		texte(tr("airain.manuel.reserve." + camp).copy().withStyle(ChatFormatting.ITALIC), SEPIA);
	}

	/** Caractéristiques lues sur l'objet : dégâts, vitesse, portée, recul, balayage, protection, durabilité. */
	private static List<Component> stats(ItemStack s) {
		List<Component> l = new ArrayList<>();
		double[] v = new double[8];   // dégâts, vitesse, portée, recul, balayage, armure, robustesse, recul encaissé
		EquipmentSlot slot = s.getItem() instanceof ArmorItem a ? a.getEquipmentSlot() : EquipmentSlot.MAINHAND;
		s.forEachModifier(slot, (attr, mod) -> {
			if (mod.operation() != AttributeModifier.Operation.ADD_VALUE) return;
			if (attr.is(Attributes.ATTACK_DAMAGE)) v[0] += mod.amount();
			else if (attr.is(Attributes.ATTACK_SPEED)) v[1] += mod.amount();
			else if (attr.is(Attributes.ENTITY_INTERACTION_RANGE)) v[2] += mod.amount();
			else if (attr.is(Attributes.ATTACK_KNOCKBACK)) v[3] += mod.amount();
			else if (attr.is(Attributes.SWEEPING_DAMAGE_RATIO)) v[4] += mod.amount();
			else if (attr.is(Attributes.ARMOR)) v[5] += mod.amount();
			else if (attr.is(Attributes.ARMOR_TOUGHNESS)) v[6] += mod.amount();
			else if (attr.is(Attributes.KNOCKBACK_RESISTANCE)) v[7] += mod.amount();
		});
		if (v[0] != 0) l.add(tr("airain.manuel.stat.degats", n(1 + v[0])));          // le joueur frappe à 1 de base
		if (v[1] != 0) l.add(tr("airain.manuel.stat.vitesse", n(4 + v[1])));         // 4 coups par seconde de base
		if (v[2] != 0) l.add(tr("airain.manuel.stat.portee", n(v[2])));
		if (v[3] != 0) l.add(tr("airain.manuel.stat.recul", n(v[3])));
		if (v[4] != 0) l.add(tr("airain.manuel.stat.balayage", n(v[4] * 100)));
		armure(l, v[5], v[6], v[7]);
		if (s.getMaxDamage() > 0) l.add(tr("airain.manuel.stat.durabilite", s.getMaxDamage()));
		if (s.has(DataComponents.FIRE_RESISTANT)) l.add(tr("airain.manuel.stat.ignifuge"));
		return l;
	}

	/** Ensemble d'armure : protection totale des quatre pièces. */
	private static List<Component> statsEnsemble(Manuel.Entree e) {
		List<Component> l = new ArrayList<>();
		double[] v = new double[3];
		for (String id : e.objets()) {
			ItemStack s = pile(id);
			if (!(s.getItem() instanceof ArmorItem a)) continue;
			s.forEachModifier(a.getEquipmentSlot(), (attr, mod) -> {
				if (mod.operation() != AttributeModifier.Operation.ADD_VALUE) return;
				if (attr.is(Attributes.ARMOR)) v[0] += mod.amount();
				else if (attr.is(Attributes.ARMOR_TOUGHNESS)) v[1] += mod.amount();
				else if (attr.is(Attributes.KNOCKBACK_RESISTANCE)) v[2] += mod.amount();
			});
		}
		l.add(tr("airain.manuel.stat.pieces", e.objets().length));
		armure(l, v[0], v[1], v[2]);
		return l;
	}

	private static void armure(List<Component> l, double armure, double robustesse, double recul) {
		if (armure != 0) l.add(tr("airain.manuel.stat.armure", n(armure)));
		if (robustesse != 0) l.add(tr("airain.manuel.stat.robustesse", n(robustesse)));
		if (recul != 0) l.add(tr("airain.manuel.stat.resistance_recul", n(recul * 100)));
	}

	// ---- navigation (comme les Chroniques)
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
		if (key == 268 || key == 259) { aller(0); return true; }   // Début / Retour arrière : la page de garde
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
				if (l.icone() != null) {                                  // icône de la page : objet agrandi deux fois
					g.pose().pushPose();
					g.pose().translate(x + LARGE / 2f - 16, y - 2, 0);
					g.pose().scale(2f, 2f, 1f);
					g.renderItem(l.icone(), 0, 0);
					g.pose().popPose();
					continue;
				}
				boolean survol = l.saut() >= 0 && mx >= x && mx < x + LARGE && my >= y - 1 && my < y + 9;
				int c = survol ? BLEU : l.couleur();
				if (l.centre()) x += (LARGE - font.width(l.texte())) / 2;
				g.drawString(font, l.texte(), x, y, c, false);
				if (survol) g.fill(x, y + 9, x + font.width(l.texte()), y + 10, 0xFF000000 | BLEU);
			}
		}
		for (int cote = 0; cote < 2; cote++) {                         // numéro sous chaque page
			int k = planche * 2 + cote;
			if (k >= pages.size()) break;
			String num = String.valueOf(k + 1);
			g.drawString(font, num, px(cote) + LARGE / 2 - font.width(num) / 2, by() + 162, SEPIA, false);
		}
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
