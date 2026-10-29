package fr.chatmort.airain.trophee;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;

/**
 * Infobulle du piédestal : en visant un piédestal garni, une petite plaque de laiton près du viseur rappelle
 * le trophée, ses effets et la plaque gravée.
 */
public final class HudSocle {
	private HudSocle() {}

	public static void rendre(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || mc.options.hideGui || mc.screen != null || !(mc.hitResult instanceof BlockHitResult h) || h.getType() != HitResult.Type.BLOCK) return;
		SocleBlockEntity s = SocleBlock.socle(mc.level, h.getBlockPos());
		if (s == null || s.trophee().isEmpty()) return;
		List<Component> l = new ArrayList<>();
		l.add(s.trophee().getHoverName());
		for (Trophees.Effet e : Trophees.effetsDe(s.trophee()))
			l.add(Component.translatable("airain.trophee.effet." + e.name().toLowerCase()));
		if (!s.plaque().isEmpty()) l.add(Component.translatable("airain.socle.grave", s.plaque(), s.jour()));
		var f = mc.font;
		int w = 0;
		for (Component c : l) w = Math.max(w, f.width(c));
		int x = g.guiWidth() / 2 + 12, y = g.guiHeight() / 2 - 6, hh = l.size() * 10 + 6;
		g.fill(x, y, x + w + 10, y + hh, 0xE0281A0C);                         // plaque sombre bordée de laiton
		g.renderOutline(x, y, w + 10, hh, 0xFFC8962E);
		g.fill(x + 2, y + 2, x + 4, y + 4, 0xFFE8BE5A); g.fill(x + w + 6, y + 2, x + w + 8, y + 4, 0xFFE8BE5A);
		for (int i = 0; i < l.size(); i++)
			g.drawString(f, l.get(i), x + 5, y + 4 + i * 10, i == 0 ? 0xFFD45A : i == l.size() - 1 && !s.plaque().isEmpty() ? 0xB8A070 : 0xEDE3C8, i == 0);
	}
}
