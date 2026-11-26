package fr.chatmort.airain.fonderie;

import java.util.ArrayList;
import java.util.List;

import com.mojang.blaze3d.platform.Lighting;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;

/** 1.70 : fenêtre d'aperçu d'un carton imprimé : la zone posée en 3D, à tourner (glisser) et zoomer (molette). */
public class CartonScreen extends Screen {
	private final ItemStack carton;
	private final List<BlockPos> pos = new ArrayList<>();
	private final List<BlockState> etats = new ArrayList<>();
	private int nx = 1, ny = 1, nz = 1;
	private float lacet = 45, tangage = 30, zoom = 1;
	private static final int W = 230, H = 190;

	public CartonScreen(ItemStack s) {
		super(s.getHoverName());
		carton = s.copy();
		Motif.Grille g = Motif.grille(carton, Minecraft.getInstance().level);
		if (g == null) return;
		boolean mur = g.type.equals("wall");
		int bl = g.bord != null ? g.bordL : 0;
		int n = Math.min(24, Math.max(12, Math.max(g.sx, g.sz) + 2 * bl));
		nx = n; ny = mur ? Math.min(16, Math.max(8, g.sy + 2 * bl)) : Math.max(1, g.sy); nz = mur ? 1 : n;
		BlockPos a = BlockPos.ZERO, b = new BlockPos(nx - 1, ny - 1, nz - 1);
		int r = Motif.rot(carton);
		for (BlockPos c : BlockPos.betweenClosed(a, b)) {
			BlockState st = Motif.etatZone(g, r, a, b, c);
			if (st != null) { pos.add(c.immutable()); etats.add(st); }
		}
		if (mur) { lacet = 20; tangage = 10; }
	}

	@Override
	protected void init() {
		int x = (width - W) / 2, y = (height - H) / 2;
		addRenderableWidget(Button.builder(Component.literal("<"), b -> lacet -= 90).bounds(x + 8, y + H - 26, 20, 20).build());
		addRenderableWidget(Button.builder(Component.literal(">"), b -> lacet += 90).bounds(x + W - 28, y + H - 26, 20, 20).build());
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = (width - W) / 2, y = (height - H) / 2;
		g.drawString(font, title, x + 8, y + 6, 0xFFE1BA6E, true);
		g.drawString(font, Component.translatable("airain.carreleur.apercu_taille", nx, ny, nz, etats.size()), x + 8, y + 17, 0xFFBEBEBE, false);
		Component aide = Component.translatable("airain.carreleur.apercu_aide");
		g.drawString(font, aide, x + (W - font.width(aide)) / 2, y + H - 20, 0xFFAAAAAA, false);
		// la zone en 3D, au centre du cadre
		g.enableScissor(x + 9, y + 29, x + W - 9, y + H - 32);
		PoseStack ps = g.pose();
		ps.pushPose();
		ps.translate(x + W / 2f, y + 29 + (H - 61) / 2f, 300);
		float s = zoom * 120f / Math.max(nx, Math.max(ny, nz));
		ps.scale(s, -s, s);
		ps.mulPose(Axis.XP.rotationDegrees(tangage));
		ps.mulPose(Axis.YP.rotationDegrees(lacet));
		ps.translate(-nx / 2f, -ny / 2f, -nz / 2f);
		Lighting.setupFor3DItems();
		var mc = Minecraft.getInstance();
		var buf = g.bufferSource();
		for (int i = 0; i < pos.size(); i++) {
			BlockPos p = pos.get(i);
			ps.pushPose();
			ps.translate(p.getX(), p.getY(), p.getZ());
			mc.getBlockRenderer().renderSingleBlock(etats.get(i), ps, buf, 0xF000F0, OverlayTexture.NO_OVERLAY);
			ps.popPose();
		}
		g.flush();
		ps.popPose();
		Lighting.setupForFlatItems();
		g.disableScissor();
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		super.renderBackground(g, mx, my, pt);
		int x = (width - W) / 2, y = (height - H) / 2;
		// cadre de la table du carreleur : filet rouge, ardoise, creux sombre pour la vue
		g.fill(x, y, x + W, y + H, 0xFF6E0F16);
		g.fill(x + 1, y + 1, x + W - 1, y + H - 1, 0xFFAF1D25);
		g.fill(x + 2, y + 2, x + W - 2, y + H - 2, 0xFF363A44);
		g.fill(x + 8, y + 28, x + W - 8, y + H - 31, 0xFFAF1D25);
		g.fill(x + 9, y + 29, x + W - 9, y + H - 32, 0xFF1E2128);
	}

	@Override
	public boolean mouseDragged(double mx, double my, int bt, double dx, double dy) {
		lacet += (float) dx * 1.5f;
		tangage = Math.max(-80, Math.min(80, tangage + (float) dy * 1.5f));
		return true;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		zoom = Math.max(0.4f, Math.min(3f, zoom * (sy > 0 ? 1.12f : 1 / 1.12f)));
		return true;
	}

	@Override public boolean isPauseScreen() { return false; }
}
