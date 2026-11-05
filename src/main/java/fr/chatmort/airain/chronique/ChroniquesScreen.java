package fr.chatmort.airain.chronique;

import java.util.ArrayList;
import java.util.List;

import com.mojang.blaze3d.systems.RenderSystem;

import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;

/**
 * Les Chroniques oubliées, au style du registre : page de garde et sommaire, « Où en étions-nous ? »,
 * le récit, le journal de bord et les archives (un clic rouvre l'écrit).
 */
public class ChroniquesScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registry.png");
	private static final int W = 300, LARGE = 118, LIGNES = 13;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, BLEU = 0x28507A;

	/** Une ligne de page : texte, couleur, et éventuellement un écrit à rouvrir ou une page où sauter. */
	private record Ligne(FormattedCharSequence texte, int couleur, ItemStack ecrit, int saut, boolean centre) {}

	private final List<List<Ligne>> pages = new ArrayList<>();
	private final int[] sections = new int[4];
	private final CompoundTag d;
	private int planche;

	public ChroniquesScreen(CompoundTag donnees) {
		super(Component.translatable("item.airain.chronicles"));
		this.d = donnees;
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }

	// ---- mise en page
	private List<Ligne> page;

	private void nouvellePage() { page = new ArrayList<>(); pages.add(page); }

	private void ligne(Ligne l) {
		if (page == null || page.size() >= LIGNES) nouvellePage();
		page.add(l);
	}

	private void texte(Component t, int c) { for (FormattedCharSequence s : font.split(t, LARGE)) ligne(new Ligne(s, c, null, -1, false)); }

	private void vide() { if (page != null && !page.isEmpty() && page.size() < LIGNES) page.add(new Ligne(FormattedCharSequence.EMPTY, 0, null, -1, false)); }

	private void titre(Component t) {
		nouvellePage();
		ligne(new Ligne(t.copy().withStyle(ChatFormatting.BOLD).getVisualOrderText(), ROUGE, null, -1, true));
		vide();
	}

	private static Component arg(String a) { return a.startsWith("#") ? Component.translatable(a.substring(1)) : Component.literal(a); }

	private void construire() {
		pages.clear();
		// page de garde
		nouvellePage();
		vide(); vide();
		ligne(new Ligne(Component.translatable("item.airain.chronicles").withStyle(ChatFormatting.BOLD).getVisualOrderText(), ROUGE, null, -1, true));
		for (FormattedCharSequence st : font.split(Component.translatable("airain.chronique.sous_titre").withStyle(ChatFormatting.ITALIC), LARGE))
			ligne(new Ligne(st, SEPIA, null, -1, true));
		vide(); vide();
		List<String> auteurs = new ArrayList<>();
		for (Tag t : d.getList("auteurs", Tag.TAG_STRING)) auteurs.add(t.getAsString());
		if (!auteurs.isEmpty()) {
			ligne(new Ligne(Component.translatable("airain.chronique.tenues").getVisualOrderText(), SEPIA, null, -1, true));
			ligne(new Ligne(Component.literal(String.join(", ", auteurs)).getVisualOrderText(), ENCRE, null, -1, true));
			vide();
		}
		ligne(new Ligne(Component.translatable("airain.chronique.jour", d.getInt("aujourdhui")).getVisualOrderText(), ENCRE, null, -1, true));
		// sommaire (rempli plus bas, une fois les sections placées)
		nouvellePage();
		List<Ligne> sommaire = page;
		// où en étions-nous
		List<String> recit = new ArrayList<>();
		for (Tag t : d.getList("recit", Tag.TAG_STRING)) recit.add(t.getAsString());
		List<String> ordonne = new ArrayList<>();
		for (String k : Chronique.RECIT) if (recit.contains(k)) ordonne.add(k);
		titre(Component.translatable("airain.chronique.ou"));
		sections[0] = pages.size() - 1;
		ListTag2 journal = new ListTag2(d.getList("journal", Tag.TAG_COMPOUND));
		String dernier = null;
		for (String k : ordonne) if (!k.startsWith("echo_")) dernier = k;
		if (dernier == null) texte(Component.translatable("airain.chronique.ou_vide"), SEPIA);
		else {
			texte(Component.translatable("airain.chronique.ou_chapitre").withStyle(ChatFormatting.BOLD), SEPIA);
			texte(Component.translatable("airain.chronique.recit." + dernier + ".titre"), ENCRE);
			vide();
			texte(Component.translatable("airain.chronique.ou_suite").withStyle(ChatFormatting.BOLD), SEPIA);
			texte(Component.translatable("airain.chronique.suite." + dernier), ENCRE);
		}
		if (journal.taille() > 0) {
			vide();
			texte(Component.translatable("airain.chronique.ou_dernier").withStyle(ChatFormatting.BOLD), SEPIA);
			texte(entree(journal.get(journal.taille() - 1)), ENCRE);
		}
		var notes = d.getList("notes", Tag.TAG_COMPOUND);
		if (!notes.isEmpty()) {
			vide();
			texte(Component.translatable("airain.chronique.notes").withStyle(ChatFormatting.BOLD), SEPIA);
			for (int i = 0; i < notes.size(); i++)
				texte(Component.literal(notes.getCompound(i).getString("auteur") + " : ").withStyle(ChatFormatting.BOLD)
					.append(Component.literal(notes.getCompound(i).getString("texte").replace('\n', ' ')).withStyle(ChatFormatting.ITALIC)), ENCRE);
		}
		// le récit
		titre(Component.translatable("airain.chronique.recit"));
		sections[1] = pages.size() - 1;
		if (ordonne.isEmpty()) texte(Component.translatable("airain.chronique.recit_vide"), SEPIA);
		for (String k : ordonne) {
			texte(Component.translatable("airain.chronique.recit." + k + ".titre").withStyle(ChatFormatting.BOLD), ROUGE);
			texte(Component.translatable("airain.chronique.recit." + k), ENCRE);
			vide();
		}
		// le journal de bord
		titre(Component.translatable("airain.chronique.journal"));
		sections[2] = pages.size() - 1;
		if (journal.taille() == 0) texte(Component.translatable("airain.chronique.journal_vide"), SEPIA);
		int jourPrec = -1;
		for (int i = 0; i < journal.taille(); i++) {
			CompoundTag e = journal.get(i);
			if (e.getInt("jour") != jourPrec) {
				jourPrec = e.getInt("jour");
				texte(Component.translatable("airain.chronique.jour", jourPrec).withStyle(ChatFormatting.BOLD), ROUGE);
			}
			texte(Component.literal("· ").append(entree(e)), ENCRE);
		}
		// les archives : l'index complet, rangé par camp et par auteur ; les écrits pas encore trouvés restent masqués
		titre(Component.translatable("airain.chronique.archives"));
		sections[3] = pages.size() - 1;
		java.util.Map<String, ItemStack> trouves = new java.util.LinkedHashMap<>();
		for (Tag t : d.getList("archives", Tag.TAG_COMPOUND)) {
			ItemStack s = minecraft != null && minecraft.level != null
				? ItemStack.parseOptional(minecraft.level.registryAccess(), (CompoundTag) t) : ItemStack.EMPTY;
			if (s.isEmpty()) continue;
			var cd = s.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);
			String doc = cd != null ? cd.copyTag().getString("airain_doc") : "";
			trouves.putIfAbsent(doc.isEmpty() ? "?" + trouves.size() : doc, s);
		}
		int total = 0, vus = 0;
		for (String[][] g : Chronique.INDEX) for (int i = 1; i < g.length; i++) { total++; if (trouves.containsKey(g[i][0])) vus++; }
		texte(Component.translatable("airain.chronique.archives_compte", vus, total).withStyle(ChatFormatting.BOLD), ENCRE);
		texte(Component.translatable(vus == 0 ? "airain.chronique.archives_vide" : "airain.chronique.archives_aide").withStyle(ChatFormatting.ITALIC), SEPIA);
		String camp = "";
		java.util.Set<String> places = new java.util.HashSet<>();
		for (String[][] g : Chronique.INDEX) {
			String c = g[0][0];
			if (!c.equals(camp)) {
				camp = c;
				int n = 0, v = 0;
				for (String[][] h : Chronique.INDEX) if (h[0][0].equals(c)) for (int i = 1; i < h.length; i++) { n++; if (trouves.containsKey(h[i][0])) v++; }
				vide();
				ligne(new Ligne(Component.translatable("airain.chronique.camp." + c).append(" · " + v + "/" + n).withStyle(ChatFormatting.BOLD).getVisualOrderText(), ROUGE, null, -1, true));
			}
			vide();
			texte(Component.translatable("airain.chronique.auteur." + g[0][1]).withStyle(ChatFormatting.UNDERLINE), ENCRE);
			for (int i = 1; i < g.length; i++) {
				ItemStack s = trouves.get(g[i][0]);
				places.add(g[i][0]);
				if (s == null) { ligne(new Ligne(Component.literal("  ??????????").getVisualOrderText(), 0x9A8A78, null, -1, false)); continue; }
				for (FormattedCharSequence l : font.split(Component.literal("✎ ").append(nomEcrit(g[i][1], s)), LARGE)) ligne(new Ligne(l, BLEU, s, -1, false));
			}
		}
		boolean autres = false;   // écrits hors index (anciens, ou ajoutés par le pack) : à la fin
		for (var e : trouves.entrySet()) {
			if (places.contains(e.getKey())) continue;
			if (!autres) { vide(); texte(Component.translatable("airain.chronique.auteur.autres").withStyle(ChatFormatting.UNDERLINE), ENCRE); autres = true; }
			for (FormattedCharSequence l : font.split(Component.literal("✎ ").append(nomEcrit(null, e.getValue())), LARGE)) ligne(new Ligne(l, BLEU, e.getValue(), -1, false));
		}
		// sommaire
		sommaire.add(new Ligne(Component.translatable("airain.chronique.sommaire").withStyle(ChatFormatting.BOLD).getVisualOrderText(), ROUGE, null, -1, true));
		sommaire.add(new Ligne(FormattedCharSequence.EMPTY, 0, null, -1, false));
		String[] noms = {"ou", "recit", "journal", "archives"};
		for (int i = 0; i < 4; i++) {
			sommaire.add(new Ligne(Component.literal((i + 1) + ". ").append(Component.translatable("airain.chronique." + noms[i])).getVisualOrderText(), ENCRE, null, sections[i], false));
			sommaire.add(new Ligne(FormattedCharSequence.EMPTY, 0, null, -1, false));
		}
	}

	private static Component entree(CompoundTag e) {
		var a = e.getList("args", Tag.TAG_STRING);
		Object[] args = new Object[a.size()];
		for (int i = 0; i < a.size(); i++) args[i] = arg(a.getString(i));
		return Component.translatable(e.getString("cle"), args);
	}

	/** Titre d'un écrit : la clé de l'index si elle est traduite, sinon le nom de l'objet ou le titre du livre. */
	private static Component nomEcrit(String cle, ItemStack s) {
		if (cle != null && net.minecraft.client.resources.language.I18n.exists(cle)) return Component.translatable(cle);
		if (s.has(net.minecraft.core.component.DataComponents.CUSTOM_NAME)) return s.getHoverName().copy().withStyle(st -> st.withItalic(false).withColor((net.minecraft.network.chat.TextColor) null));
		var livre = s.get(net.minecraft.core.component.DataComponents.WRITTEN_BOOK_CONTENT);
		return livre != null && !livre.title().raw().isBlank() ? Component.literal(livre.title().raw()) : s.getHoverName();
	}

	/** Petit accès indexé à une liste NBT. */
	private record ListTag2(net.minecraft.nbt.ListTag l) {
		int taille() { return l.size(); }
		CompoundTag get(int i) { return l.getCompound(i); }
	}

	@Override
	protected void init() {
		if (pages.isEmpty()) construire();
		avant = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> aller(planche - 1)));
		apres = addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> aller(planche + 1)));
		signet = addRenderableWidget(new WidgetsEmpire.Signet(bx(), by(), b -> aller(0)));
	}

	private WidgetsEmpire.Fleche avant, apres;
	private WidgetsEmpire.Signet signet;

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
				Ligne l = p.get(i);
				if (l.saut() >= 0) { aller(l.saut() / 2); return true; }
				if (l.ecrit() != null && minecraft != null) {
					BookViewScreen.BookAccess acces = BookViewScreen.BookAccess.fromItem(l.ecrit());
					if (acces != null) { minecraft.setScreen(new BookViewScreen(acces)); return true; }
				}
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
				boolean survol = (l.saut() >= 0 || l.ecrit() != null) && mx >= x && mx < x + LARGE && my >= y - 1 && my < y + 9;
				int c = survol ? BLEU : l.couleur();
				if (l.centre()) x += (LARGE - font.width(l.texte())) / 2;
				g.drawString(font, l.texte(), x, y, c, false);
				if (survol) g.fill(x, y + 9, x + font.width(l.texte()), y + 10, 0xFF000000 | BLEU);
			}
		}
		for (int cote = 0; cote < 2; cote++) {                 // numéro sous chaque page, comme le registre
			int k = planche * 2 + cote;
			if (k >= pages.size()) break;
			String n = String.valueOf(k + 1);
			g.drawString(font, n, px(cote) + LARGE / 2 - font.width(n) / 2, by() + 162, SEPIA, false);
		}
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
