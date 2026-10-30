package fr.chatmort.airain.codex;

import com.mojang.blaze3d.systems.RenderSystem;
import fr.chatmort.airain.gui.WidgetsEmpire;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Le Codex de l'Empire, au style du registre. Première double page : le titre et l'avancement par force (un clic
 * mène à la force). Ensuite, une double page par créature : à gauche son portrait, son nom, sa force et ses victoires ;
 * à droite son histoire, puis la note d'ingénieur (dix victoires, ou un boss vaincu) et, pour un boss, sa page d'honneur.
 */
public class CodexScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registre.png");
	private static final ResourceLocation ICONES = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/codex.png");
	private static final int W = 300, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14, VERT = 0x2E5A1E, GRIS = 0x9A8A70;
	private final CompoundTag victoires, jours;
	private final Map<String, Entity> modeles = new HashMap<>();
	private int planche;

	public CodexScreen(OuvrirCodex m) {
		super(Component.translatable("item.airain.codex"));
		victoires = m.donnees().getCompound("victoires");
		jours = m.donnees().getCompound("jours");
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }
	private int planches() { return 1 + Codex.ENTREES.size(); }

	@Override
	protected void init() {
		addRenderableWidget(new WidgetsEmpire.Fleche(bx() + 20, by() + 156, false, b -> tourner(-1)));
		addRenderableWidget(new WidgetsEmpire.Fleche(bx() + W - 36, by() + 156, true, b -> tourner(1)));
	}

	private void tourner(int d) { aller(planche + d); }

	private void aller(int n) {
		n = Mth.clamp(n, 0, planches() - 1);
		if (n != planche && minecraft != null) minecraft.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1f));
		planche = n;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) { tourner(sy > 0 ? -1 : 1); return true; }

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == 262 || key == 267) { tourner(1); return true; }
		if (key == 263 || key == 266) { tourner(-1); return true; }
		return super.keyPressed(key, scan, mods);
	}

	/** Sur le sommaire, un clic sur une force ouvre sa première page. */
	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		if (planche == 0) {
			int x = bx() + 162, y = by() + 22 + 24;
			for (Codex.Force f : Codex.Force.values()) {
				if (mx >= x && mx < x + LARGE && my >= y && my < y + 26) {
					for (int i = 0; i < Codex.ENTREES.size(); i++)
						if (Codex.ENTREES.get(i).force() == f) { aller(i + 1); return true; }
				}
				y += 32;
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
		super.render(g, mx, my, pt);
		int gx = bx() + 20, dx = bx() + 162, y = by() + 22;
		if (planche == 0) sommaire(g, gx, dx, y);
		else page(g, Codex.ENTREES.get(planche - 1), gx, dx, y, mx, my);
		String n = planche + 1 + " / " + planches();
		g.drawString(font, n, bx() + W / 2 - font.width(n) / 2, by() + 162, SEPIA, false);
	}

	private void centre(GuiGraphics g, Component t, int x, int y, int c) { g.drawString(font, t, x + LARGE / 2 - font.width(t) / 2, y, c, false); }

	private int texte(GuiGraphics g, FormattedText t, int x, int y, int c, int max) {
		List<FormattedCharSequence> l = font.split(t, LARGE);
		for (int i = 0; i < Math.min(max, l.size()); i++) { g.drawString(font, l.get(i), x, y, c, false); y += 10; }
		return y;
	}

	private void icone(GuiGraphics g, Codex.Force f, int x, int y, int taille) {
		RenderSystem.enableBlend();
		g.blit(ICONES, x, y, taille, taille, f.ordinal() * 16, 0, 16, 16, 64, 64);
	}

	private int ouvertes(Codex.Force f) {
		int n = 0;
		for (Codex.Entree e : Codex.ENTREES) if (e.force() == f && victoires.getInt(e.id()) > 0) n++;
		return n;
	}

	private void sommaire(GuiGraphics g, int gx, int dx, int y) {
		texte(g, Component.translatable("item.airain.codex").withStyle(ChatFormatting.BOLD), gx, y + 6, ROUGE, 2);
		texte(g, Component.translatable("airain.codex.intro"), gx, y + 26, SEPIA, 10);
		centre(g, Component.translatable("airain.codex.forces").withStyle(ChatFormatting.BOLD), dx, y + 4, ENCRE);
		int yy = y + 24;
		for (Codex.Force f : Codex.Force.values()) {
			int tot = 0;
			for (Codex.Entree e : Codex.ENTREES) if (e.force() == f) tot++;
			icone(g, f, dx, yy, 24);
			g.drawString(font, Component.translatable("airain.codex.force." + f.name().toLowerCase()), dx + 30, yy + 3, ENCRE, false);
			int o = ouvertes(f);
			g.drawString(font, Component.translatable("airain.codex.avancement", o, tot), dx + 30, yy + 14, o == tot ? VERT : SEPIA, false);
			yy += 32;
		}
	}

	private Entity modele(String id) {
		if (minecraft == null || minecraft.level == null) return null;
		return modeles.computeIfAbsent(id, k -> {
			try {
				EntityType<?> t = BuiltInRegistries.ENTITY_TYPE.get(Codex.rl(k));
				return t.create(minecraft.level);
			} catch (Exception ex) { return null; }
		});
	}

	private void page(GuiGraphics g, Codex.Entree e, int gx, int dx, int y, int mx, int my) {
		int n = victoires.getInt(e.id());
		boolean connu = n > 0, note = e.boss() ? n > 0 : n >= 10;
		icone(g, e.force(), gx, y - 4, 12);
		g.drawString(font, Component.translatable("airain.codex.force." + e.force().name().toLowerCase()), gx + 15, y - 2, SEPIA, false);
		// portrait (ou silhouette de l'emblème)
		int px = gx + LARGE / 2, py = y + 82;
		if (connu && modele(e.id()) instanceof LivingEntity le) {
			float h = Math.max(le.getBbHeight(), le.getBbWidth());
			int echelle = (int) Mth.clamp(40 / h, 4, 34);
			try {
				InventoryScreen.renderEntityInInventoryFollowsMouse(g, gx + 4, y + 12, gx + LARGE - 4, py, echelle, 0.0625f, mx, my, le);
			} catch (Exception ignore) {}
		} else {
			RenderSystem.setShaderColor(0.35f, 0.3f, 0.25f, 0.6f);
			icone(g, e.force(), px - 24, y + 22, 48);
			RenderSystem.setShaderColor(1f, 1f, 1f, 1f);
		}
		Component nom = connu ? EntityType.byString(e.id()).map(EntityType::getDescription).orElse(Component.literal(e.id()))
			: Component.literal("? ? ?");
		centre(g, nom.copy().withStyle(ChatFormatting.BOLD), gx, y + 88, connu ? ENCRE : GRIS);
		centre(g, Component.translatable("airain.registre.dim." + e.dim()), gx, y + 100, SEPIA);
		if (e.boss()) centre(g, Component.translatable("airain.codex.boss").withStyle(ChatFormatting.ITALIC), gx, y + 111, ROUGE);
		if (connu) centre(g, Component.translatable("airain.codex.victoires", n), gx, y + 122, VERT);
		// page de droite : histoire, note, honneur
		if (!connu) {
			texte(g, Component.translatable("airain.codex.inconnu").withStyle(ChatFormatting.ITALIC), dx, y + 10, GRIS, 6);
			return;
		}
		int yy = texte(g, Component.translatable("airain.codex." + e.cle() + ".lore"), dx, y, ENCRE, 7);
		yy += 4;
		g.fill(dx + 10, yy, dx + LARGE - 10, yy + 1, 0xFF9A7046);
		yy += 5;
		if (note) {
			g.drawString(font, Component.translatable("airain.codex.note_titre").withStyle(ChatFormatting.BOLD), dx, yy, ROUGE, false);
			yy = texte(g, Component.translatable("airain.codex." + e.cle() + ".note"), dx, yy + 11, SEPIA, 5);
		} else {
			texte(g, Component.translatable("airain.codex.note_cachee", 10 - n).withStyle(ChatFormatting.ITALIC), dx, yy, GRIS, 3);
		}
		if (e.boss() && connu)
			centre(g, Component.translatable("airain.codex.honneur", jours.getInt(e.id())).withStyle(ChatFormatting.ITALIC), dx, y + 124, ROUGE);
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
