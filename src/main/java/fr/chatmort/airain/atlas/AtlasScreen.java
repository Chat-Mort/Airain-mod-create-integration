package fr.chatmort.airain.atlas;

import java.util.ArrayList;
import java.util.List;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.math.Axis;

import fr.chatmort.airain.fondation.Apparence;
import fr.chatmort.airain.fondation.TexturesBanniere;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/**
 * L'atlas impérial : une carte d'explorateur sur les deux pages du livre. Parchemin clair là où l'équipe est passée,
 * hachures ailleurs ; icônes des bases, des lieux visités et des morts. Glisser pour se déplacer, molette pour le zoom.
 */
public class AtlasScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registre.png");
	private static final ResourceLocation ICONES = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/atlas.png");
	private static final int W = 300, X0 = 14, Y0 = 19, X1 = 286, Y1 = 155;
	private static final int[] ECHELLES = {1, 2, 4, 8, 16};
	/** Catégories (filtres) et leur case dans la planche d'icônes. */
	private static final String[] TYPES = {"base", "poste", "ruine", "camp", "relais", "station", "lieu", "mort"};
	private final boolean[] visibles = {true, true, true, true, true, true, true, true};
	private final CompoundTag d;
	private final LongOpenHashSet chunks;
	private double cx, cz;
	private int zoom = 2;

	private record Point(int x, int z, int type, Component nom, Apparence banniere) {}
	private final List<Point> points = new ArrayList<>();

	public AtlasScreen(CompoundTag donnees) {
		super(Component.translatable("item.airain.atlas"));
		d = donnees;
		chunks = new LongOpenHashSet(d.getLongArray("chunks"));
		for (Tag t : d.getList("fondations", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) t;
			points.add(new Point(c.getInt("x"), c.getInt("z"), 0, c.getString("nom").isEmpty() ? Component.translatable("airain.fondation.sans_nom") : Component.literal(c.getString("nom")),
				Apparence.unpack(c.getInt("apparence"), c.getInt("ext"))));
		}
		for (Tag t : d.getList("lieux", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) t;
			String id = c.getString("id");
			int k = java.util.Arrays.asList(TYPES).indexOf(c.getString("type"));
			String court = id.substring(id.indexOf(':') + 1).replace('_', ' ');
			points.add(new Point(c.getInt("x"), c.getInt("z"), Math.max(1, k),
				Component.translatableWithFallback("airain.atlas.lieu." + id.replace(':', '.'), court.substring(0, 1).toUpperCase() + court.substring(1))
					.append(Component.literal(" · ")).append(Component.translatable("airain.chronique.jour", c.getInt("jour")).withStyle(ChatFormatting.GRAY)), null));
		}
		for (Tag t : d.getList("morts", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) t;
			points.add(new Point(c.getInt("x"), c.getInt("z"), 7, Component.translatable("airain.atlas.mort", c.getString("nom"), c.getInt("jour")), null));
		}
	}

	@Override
	protected void init() {
		if (minecraft != null && minecraft.player != null && cx == 0 && cz == 0) { cx = minecraft.player.getX(); cz = minecraft.player.getZ(); }
	}

	private int bx() { return (width - W) / 2; }
	private int by() { return (height - 196) / 2; }
	private int ech() { return ECHELLES[zoom]; }
	private int sx(double x) { return (int) Math.round(bx() + (X0 + X1) / 2.0 + (x - cx) / ech()); }
	private int sy(double z) { return (int) Math.round(by() + (Y0 + Y1) / 2.0 + (z - cz) / ech()); }
	private double wx(double px) { return cx + (px - bx() - (X0 + X1) / 2.0) * ech(); }
	private double wz(double py) { return cz + (py - by() - (Y0 + Y1) / 2.0) * ech(); }
	private boolean dansCarte(double mx, double my) { return mx >= bx() + X0 && mx < bx() + X1 && my >= by() + Y0 && my < by() + Y1; }

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		zoom = Mth.clamp(zoom + (sy > 0 ? -1 : 1), 0, ECHELLES.length - 1);
		return true;
	}

	@Override
	public boolean mouseDragged(double mx, double my, int b, double dx, double dy) {
		if (!dansCarte(mx, my)) return false;
		cx -= dx * ech(); cz -= dy * ech();
		return true;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		int fx = bx() + 20, fy = by() + 159;
		for (int i = 0; i < TYPES.length; i++) {
			int x = fx + i * 15;
			if (mx >= x && mx < x + 12 && my >= fy && my < fy + 12) { visibles[i] = !visibles[i]; return true; }
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
		int x0 = bx() + X0, y0 = by() + Y0, x1 = bx() + X1, y1 = by() + Y1;
		g.enableScissor(x0, y0, x1, y1);
		g.fill(x0, y0, x1, y1, 0xFFB49A6C);
		for (int y = y0; y < y1; y += 3) g.fill(x0, y, x1, y + 1, 0x18000000);
		// chunks parcourus
		int e = ech(), cote = Math.max(1, 16 / e);
		int c0x = Mth.floor(wx(x0)) >> 4, c1x = Mth.floor(wx(x1)) >> 4, c0z = Mth.floor(wz(y0)) >> 4, c1z = Mth.floor(wz(y1)) >> 4;
		for (int cx2 = c0x; cx2 <= c1x; cx2++)
			for (int cz2 = c0z; cz2 <= c1z; cz2++)
				if (chunks.contains(net.minecraft.world.level.ChunkPos.asLong(cx2, cz2))) {
					int px = sx(cx2 * 16), py = sy(cz2 * 16);
					g.fill(px, py, px + cote, py + cote, 0xFFE4CEA0);
				}
		// quadrillage tous les 256 blocs
		for (int gx = Mth.floor(wx(x0) / 256) * 256; gx < wx(x1); gx += 256) g.fill(sx(gx), y0, sx(gx) + 1, y1, 0x22785A32);
		for (int gz = Mth.floor(wz(y0) / 256) * 256; gz < wz(y1); gz += 256) g.fill(x0, sy(gz), x1, sy(gz) + 1, 0x22785A32);
		// icônes
		Point survol = null;
		for (Point p : points) {
			if (!visibles[p.type()]) continue;
			int px = sx(p.x()), py = sy(p.z());
			if (px < x0 - 8 || px > x1 + 8 || py < y0 - 8 || py > y1 + 8) continue;
			if (p.banniere() != null) {
				g.fill(px - 4, py - 13, px - 3, py + 1, 0xFF3C2814);
				g.blit(TexturesBanniere.de(p.banniere()), px - 3, py - 13, 6, 12, 0f, 0f, 16, 32, 16, 32);
			} else g.blit(ICONES, px - 5, py - 5, 10, 10, p.type() * 16, 0, 16, 16, 160, 16);
			if (Math.abs(mx - px) <= 5 && Math.abs(my - py) <= 6) survol = p;
		}
		// le joueur
		if (minecraft != null && minecraft.player != null) {
			int px = sx(minecraft.player.getX()), py = sy(minecraft.player.getZ());
			g.pose().pushPose();
			g.pose().translate(px, py, 0);
			g.pose().mulPose(Axis.ZP.rotationDegrees(minecraft.player.getYRot() + 180));
			g.blit(ICONES, -5, -5, 10, 10, 8 * 16, 0, 16, 16, 160, 16);
			g.pose().popPose();
		}
		g.disableScissor();
		// pli de la carte au dos du livre : une ombre douce, plus sombre au centre
		for (int k = 0; k < 4; k++) g.fill(bx() + 146 + k, y0, bx() + 154 - k, y1, 0x0C200804);
		// cadre de la carte et cartouche du titre (le monde affiché)
		g.fill(x0 - 1, y0 - 1, x1 + 1, y0, 0xFF6E5034); g.fill(x0 - 1, y1, x1 + 1, y1 + 1, 0xFF6E5034);
		g.fill(x0 - 1, y0, x0, y1, 0xFF6E5034); g.fill(x1, y0, x1 + 1, y1, 0xFF6E5034);
		Component dim = Component.translatable("airain.registre.dim." + ResourceLocation.parse(d.getString("dim")).getPath()).copy().withStyle(ChatFormatting.BOLD);
		int lt = font.width(dim);
		g.fill(x0 + 3, y0 + 3, x0 + 11 + lt, y0 + 15, 0xFF6E5034);
		g.fill(x0 + 4, y0 + 4, x0 + 10 + lt, y0 + 14, 0xFFE9D3A5);
		g.drawString(font, dim, x0 + 7, y0 + 5, 0x8A1A14, false);
		// barre du bas : filtres, coordonnées, échelle
		int fx = bx() + 20, fy = by() + 159;
		for (int i = 0; i < TYPES.length; i++) {
			int x = fx + i * 15;
			g.fill(x - 1, fy - 1, x + 13, fy + 13, visibles[i] ? 0xFF9A7046 : 0xFF5A4630);
			g.blit(ICONES, x, fy, 12, 12, (i == 0 ? 9 : i) * 16, 0, 16, 16, 160, 16);
			if (mx >= x && mx < x + 12 && my >= fy && my < fy + 12)
				g.renderTooltip(font, Component.translatable("airain.atlas.type." + TYPES[i]), mx, my);
		}
		String bas = dansCarte(mx, my) ? "x " + (int) wx(mx) + "  z " + (int) wz(my) + "   1:" + ech() : "1:" + ech();
		g.drawString(font, bas, bx() + W - 20 - font.width(bas), fy + 2, 0x6E5034, false);
		if (survol != null) g.renderTooltip(font, survol.nom(), mx, my);
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
