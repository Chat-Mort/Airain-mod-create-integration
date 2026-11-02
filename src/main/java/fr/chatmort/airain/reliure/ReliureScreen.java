package fr.chatmort.airain.reliure;

import java.util.List;

import com.mojang.blaze3d.systems.RenderSystem;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;

/** L'écran de la Reliure : les livres en onglets à gauche du livre ouvert ; un clic ouvre le livre. */
public class ReliureScreen extends Screen {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/registre.png");
	private static final int W = 300, LARGE = 118;
	private static final int ENCRE = 0x3A1A0A, SEPIA = 0x6E5034, ROUGE = 0x8A1A14;
	private final int ou, slot;
	private final List<ItemStack> livres;

	public ReliureScreen(int ou, int slot, List<ItemStack> livres) {
		super(Component.translatable("item.airain.reliure"));
		this.ou = ou; this.slot = slot; this.livres = livres;
	}

	private int bx() { return (width - W) / 2 + 14; }
	private int by() { return (height - 196) / 2; }

	private int survol(double mx, double my) {
		for (int i = 0; i < Reliure.CASES; i++) {
			int x = bx() - 26, y = by() + 14 + i * 21;
			if (mx >= x && mx < x + 28 && my >= y && my < y + 19) return i;
		}
		return -1;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int b) {
		int i = survol(mx, my);
		if (i >= 0 && i < livres.size()) {
			if (minecraft != null) minecraft.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, 1f));
			LectureClient.lire(ou, slot, i, livres);
			return true;
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
		int h = survol(mx, my);
		for (int i = 0; i < Reliure.CASES; i++) {
			int x = bx() - 24, y = by() + 14 + i * 21;
			boolean plein = i < livres.size(), sur = plein && i == h;
			int dx = sur ? -4 : 0;
			g.fill(x + dx - 1, y - 1, x + 27, y + 20, 0xFF1E120A);
			g.fill(x + dx, y, x + 26, y + 19, sur ? 0xFF962020 : plein ? 0xFF6E3E1E : 0xFF3A2414);
			g.fill(x + dx, y, x + 26, y + 1, 0x40FFFFFF);
			if (plein) g.renderItem(livres.get(i), x + dx + 5, y + 2);
		}
		int gx = bx() + 20, dx = bx() + 162, y = by() + 18;
		g.drawString(font, Component.translatable("item.airain.reliure").withStyle(ChatFormatting.BOLD), gx, y, ROUGE, false);
		int yy = y + 16;
		for (FormattedCharSequence l : font.split(Component.translatable("airain.reliure.ecran"), LARGE)) { g.drawString(font, l, gx, yy, ENCRE, false); yy += 10; }
		if (h >= 0 && h < livres.size()) {
			ItemStack s = livres.get(h);
			g.drawString(font, s.getHoverName().copy().withStyle(ChatFormatting.BOLD), dx, y, ROUGE, false);
			yy = y + 16;
			for (FormattedCharSequence l : font.split(Component.translatable("airain.reliure.ouvrir"), LARGE)) { g.drawString(font, l, dx, yy, SEPIA, false); yy += 10; }
		} else if (livres.isEmpty()) {
			yy = y + 16;
			for (FormattedCharSequence l : font.split(Component.translatable("airain.reliure.vide_ecran"), LARGE)) { g.drawString(font, l, dx, yy, SEPIA, false); yy += 10; }
		}
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
