package fr.chatmort.airain.gardien;

import com.mojang.blaze3d.platform.InputConstants;

import fr.chatmort.airain.AirainMod;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ComputeFovModifierEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import org.lwjgl.glfw.GLFW;

/** La loupe de la couronne : maintenir la touche (Z par défaut) pour zoomer comme à la longue-vue. */
public final class Loupe {
	private Loupe() {}

	public static final KeyMapping TOUCHE = new KeyMapping("key.airain.loupe", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_Z, "key.categories.airain");
	private static boolean active;

	public static boolean porte(Player p) {
		return p != null && p.getItemBySlot(EquipmentSlot.HEAD).is(AirainMod.COURONNE.get());
	}

	public static void touches(RegisterKeyMappingsEvent e) { e.register(TOUCHE); }

	public static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		boolean v = mc.player != null && mc.screen == null && TOUCHE.isDown() && porte(mc.player);
		if (v != active && mc.player != null)
			mc.player.playSound(v ? SoundEvents.SPYGLASS_USE : SoundEvents.SPYGLASS_STOP_USING, 1f, 1.2f);
		active = v;
	}

	public static void champ(ComputeFovModifierEvent e) {
		if (active) e.setNewFovModifier(e.getNewFovModifier() * 0.2f);
	}
}
