package fr.chatmort.airain.reliure;

import java.util.List;

import com.mojang.blaze3d.platform.InputConstants;

import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import org.lwjgl.glfw.GLFW;

/** Côté client : ouvrir un livre de la Reliure, puis revenir à l'écran d'origine quand on le ferme. */
public final class LectureClient {
	private LectureClient() {}

	public static final KeyMapping TOUCHE = new KeyMapping("key.airain.reliure", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_B, "key.categories.airain");
	private static Screen retour;
	private static int attente;          // ticks pendant lesquels on attend que le livre s'ouvre
	private static boolean ouvert;

	public static void touches(RegisterKeyMappingsEvent e) { e.register(TOUCHE); }

	public static void ouvrir(Paquets.Ouvrir m) {
		Minecraft.getInstance().setScreen(new ReliureScreen(m.ou(), m.slot(), m.livres()));
	}

	/** Lire le livre n° index : on l'utilise côté client (livres qui s'ouvrent seuls) et côté serveur (registre, codex…). */
	public static void lire(int ou, int slot, int index, List<ItemStack> livres) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || index < 0 || index >= livres.size()) return;
		retour = mc.screen;
		attente = 40; ouvert = false;
		mc.setScreen(null);
		Reliure.lire(mc.player, livres.get(index));
		PacketDistributor.sendToServer(new Paquets.Lire(ou, slot, index));
	}

	public static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		while (TOUCHE.consumeClick()) if (mc.screen == null && mc.player != null) PacketDistributor.sendToServer(new Paquets.Chercher());
		if (retour == null) return;
		if (!ouvert) {
			if (mc.screen != null && mc.screen != retour) ouvert = true;
			else if (--attente <= 0) { reprendre(mc); }
			return;
		}
		if (mc.screen == null) reprendre(mc);
	}

	private static void reprendre(Minecraft mc) {
		Screen s = retour;
		retour = null; ouvert = false;
		if (s != null && mc.player != null) mc.setScreen(s);
	}
}
