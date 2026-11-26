package fr.chatmort.airain.fonderie;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.tooltip.ClientTooltipComponent;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.world.level.block.state.BlockState;

/** 1.70 : aperçu miniature d'un carton dans sa bulle d'aide (12 x 12 cases de 4 pixels, bordure comprise). */
public class MotifApercu implements ClientTooltipComponent {
	private static final int N = 12, C = 4;
	private final BlockState[][] vue;
	public MotifApercu(Motif.Apercu a) {
		Motif.Grille g = Motif.grille(a.carton(), Minecraft.getInstance().level);
		vue = g == null ? null : Motif.vue2D(g, Motif.rot(a.carton()), N);
	}
	@Override public int getHeight() { return vue == null ? 0 : N * C + 6; }
	@Override public int getWidth(Font f) { return vue == null ? 0 : N * C + 2; }
	@Override
	public void renderImage(Font f, int x, int y, GuiGraphics g) {
		if (vue == null) return;
		g.fill(x, y + 2, x + N * C + 2, y + N * C + 4, 0xFF1E2128);
		var br = Minecraft.getInstance().getBlockRenderer();
		for (int r = 0; r < N; r++)
			for (int c = 0; c < N; c++) {
				BlockState s = vue[r][c];
				if (s == null) continue;
				TextureAtlasSprite sp = br.getBlockModel(s).getParticleIcon();
				g.blit(x + 1 + c * C, y + 3 + r * C, 0, C, C, sp);
			}
	}
}
