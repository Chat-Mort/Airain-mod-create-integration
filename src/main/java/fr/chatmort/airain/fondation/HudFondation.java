package fr.chatmort.airain.fondation;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Bandeau discret en haut de l'écran : nom de la fondation, apparition et disparition en fondu. */
public final class HudFondation {
	private static final long ENTREE = 400, TENUE = 3200, SORTIE = 900;
	private static String nom;
	private static long debut;

	private HudFondation() {}

	public static void recevoir(TitreFondation m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> { nom = m.nom(); debut = System.currentTimeMillis(); });
	}

	public static void rendre(GuiGraphics g, DeltaTracker dt) {
		if (nom == null) return;
		long t = System.currentTimeMillis() - debut;
		if (t > ENTREE + TENUE + SORTIE) { nom = null; return; }
		float a = t < ENTREE ? t / (float) ENTREE : t < ENTREE + TENUE ? 1f : 1f - (t - ENTREE - TENUE) / (float) SORTIE;
		int alpha = Math.max(8, (int) (a * 255));
		Minecraft mc = Minecraft.getInstance();
		if (mc.options.hideGui) return;
		Font f = mc.font;
		int cx = g.guiWidth() / 2, y = 10;
		String texte = nom.isEmpty() ? Component.translatable("airain.fondation.sans_nom").getString() : nom;
		int larg = (int) (f.width(texte) * 1.5f);
		g.fill(cx - larg / 2 - 10, y - 4, cx + larg / 2 + 10, y + 26, (int) (a * 0x70) << 24);
		g.fill(cx - larg / 2 - 10, y + 26, cx + larg / 2 + 10, y + 27, (alpha << 24) | 0xC89A3C);
		g.pose().pushPose();
		g.pose().translate(cx, y, 0);
		g.pose().scale(1.5f, 1.5f, 1f);
		g.drawCenteredString(f, texte, 0, 0, (alpha << 24) | 0xF2C75C);
		g.pose().popPose();
		g.pose().pushPose();
		g.pose().translate(cx, y + 16, 0);
		g.pose().scale(0.75f, 0.75f, 1f);
		g.drawCenteredString(f, Component.translatable("airain.fondation.sous_titre"), 0, 0, (alpha << 24) | 0xB8B0A0);
		g.pose().popPose();
	}
}
