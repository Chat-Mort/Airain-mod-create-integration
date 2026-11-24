package fr.chatmort.airain.gardien;

import com.mojang.blaze3d.platform.InputConstants;

import fr.chatmort.airain.AirainMod;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.client.event.RenderGuiEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ComputeFovModifierEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import org.lwjgl.glfw.GLFW;

/** La loupe de la couronne : maintenir la touche (H par défaut) pour zoomer comme à la longue-vue. */
public final class Loupe {
	private Loupe() {}

	public static final KeyMapping TOUCHE = new KeyMapping("key.airain.loupe", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_H, "key.categories.airain");
	private static boolean active;

	public static boolean porte(Player p) {
		return p != null && Fin.couronne(p);
	}

	public static void touches(RegisterKeyMappingsEvent e) { e.register(TOUCHE); }

	public static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		boolean v = mc.player != null && mc.screen == null && TOUCHE.isDown() && porte(mc.player);
		if (v != active && mc.player != null)
			mc.player.playSound(v ? SoundEvents.SPYGLASS_USE : SoundEvents.SPYGLASS_STOP_USING, 1f, 1.2f);
		active = v;
		// 1.69.1 : la cible visée est recalculée à chaque tick pendant le zoom
		cible = active ? viser(mc) : null;
		attaqueTenue = mc.options.keyAttack.isDown();
	}

	// ------------------------------------------------------------ 1.69.1 : plaque d'information et marque
	private static HitResult cible;
	private static boolean attaqueTenue;

	/** Créature visée en priorité, sinon bloc, jusqu'à la portée de la marque. */
	private static HitResult viser(Minecraft mc) {
		Entity cam = mc.getCameraEntity();
		if (cam == null || mc.level == null) return null;
		Vec3 o = cam.getEyePosition(), dir = cam.getViewVector(1f), fin = o.add(dir.scale(MarqueLoupe.PORTEE));
		BlockHitResult bloc = mc.level.clip(new ClipContext(o, fin, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, cam));
		double max = bloc.getLocation().distanceToSqr(o);
		AABB zone = cam.getBoundingBox().expandTowards(dir.scale(MarqueLoupe.PORTEE)).inflate(1);
		EntityHitResult ent = ProjectileUtil.getEntityHitResult(cam, o, bloc.getLocation(), zone,
			e -> e instanceof LivingEntity && !e.isSpectator() && e.isPickable() && e != mc.player, max);
		if (ent != null) return ent;
		return bloc.getType() == HitResult.Type.BLOCK ? bloc : null;
	}

	/** Plaque d'ardoise à filet d'airain, en bas de l'écran : nom · distance · hauteur · vie. */
	public static void plaque(RenderGuiEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (!active || cible == null || mc.player == null || mc.options.hideGui) return;
		Component nom; Vec3 ou; String vie = null;
		if (cible instanceof EntityHitResult eh) {
			Entity c = eh.getEntity();
			nom = c.getDisplayName(); ou = c.position();
			if (c instanceof LivingEntity l) vie = Math.round(l.getHealth()) + " / " + Math.round(l.getMaxHealth());
		} else {
			var b = ((BlockHitResult) cible).getBlockPos();
			nom = mc.level.getBlockState(b).getBlock().getName(); ou = Vec3.atBottomCenterOf(b);
		}
		int dist = (int) Math.round(mc.player.getEyePosition().distanceTo(cible.getLocation()));
		int haut = (int) Math.floor(ou.y) - mc.player.getBlockY();
		String sep = "  \u00b7  ";
		String txt = nom.getString() + sep + dist + " m" + sep + (haut > 0 ? "+" : "") + haut + " m" + (vie != null ? sep + vie : "");
		GuiGraphics g = e.getGuiGraphics();
		int w = mc.font.width(txt) + 12, h = 13;
		int x = (g.guiWidth() - w) / 2, y = g.guiHeight() - 62;
		g.fill(x, y, x + w, y + h, 0xFF6A2C1C);                 // trait
		g.fill(x + 1, y + 1, x + w - 1, y + h - 1, 0xFFDA955B); // filet d'airain
		g.fill(x + 2, y + 2, x + w - 2, y + h - 2, 0xFF363A44); // ardoise
		g.drawString(mc.font, txt, x + 6, y + 3, 0xFFFFFFFF, true);
	}

	/** Clic gauche pendant le zoom : pas de coup, la cible est marquée (une fois par appui). */
	public static void clic(InputEvent.InteractionKeyMappingTriggered e) {
		if (!active || !e.isAttack()) return;
		e.setCanceled(true);
		e.setSwingHand(false);
		if (attaqueTenue || cible == null) return;
		attaqueTenue = true;
		if (cible instanceof EntityHitResult eh) PacketDistributor.sendToServer(new MarqueLoupe.Marque(eh.getEntity().getId(), net.minecraft.core.BlockPos.ZERO));
		else PacketDistributor.sendToServer(new MarqueLoupe.Marque(-1, ((BlockHitResult) cible).getBlockPos()));
	}

	public static void champ(ComputeFovModifierEvent e) {
		if (active) e.setNewFovModifier(e.getNewFovModifier() * 0.2f);
	}
}
