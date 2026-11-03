package fr.chatmort.airain.armure;

import java.util.HashMap;
import java.util.Map;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.RenderPlayerEvent;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;

/** Le tourbillon des twinblades : le joueur tourne sur lui-même (troisième personne), la lame tournoie (première personne). */
public final class TourbillonClient {
	private TourbillonClient() {}
	private static final float DUREE = 10f;
	private static final Map<Integer, Long> DEBUTS = new HashMap<>();

	public static void demarrer(TourbillonPaquet m) {
		var mc = Minecraft.getInstance();
		if (mc.level != null) DEBUTS.put(m.entite(), mc.level.getGameTime());
	}

	/** Angle du tour en cours (0 à 360), ou -1. */
	static float angle(int id, float pt) {
		Long d = DEBUTS.get(id);
		var mc = Minecraft.getInstance();
		if (d == null || mc.level == null) return -1;
		float t = (mc.level.getGameTime() - d + pt) / DUREE;
		if (t >= 1f || t < 0f) { DEBUTS.remove(id); return -1; }
		float e = 1f - (1f - t) * (1f - t);              // démarre vite, ralentit
		return e * 360f;
	}

	private static final java.util.Set<Integer> TOURNE = new java.util.HashSet<>();

	public static void avant(RenderPlayerEvent.Pre e) {
		float a = angle(e.getEntity().getId(), e.getPartialTick());
		if (a < 0) return;
		e.getPoseStack().pushPose();
		e.getPoseStack().mulPose(Axis.YP.rotationDegrees(-a));
		TOURNE.add(e.getEntity().getId());
	}

	public static void apres(RenderPlayerEvent.Post e) { if (TOURNE.remove(e.getEntity().getId())) e.getPoseStack().popPose(); }

	/** Première personne : la twinblade tourne comme une hélice devant soi. */
	public static final IClientItemExtensions MAIN = new IClientItemExtensions() {
		@Override
		public boolean applyForgeHandTransform(PoseStack pose, LocalPlayer p, HumanoidArm bras, ItemStack pile, float pt, float equipe, float coup) {
			float a = angle(p.getId(), pt);
			if (a < 0) return false;
			int i = bras == HumanoidArm.RIGHT ? 1 : -1;
			pose.translate(i * 0.56F, -0.52F + equipe * -0.6F, -0.72F);
			pose.translate(-i * 0.25F, 0.15F, 0F);
			pose.mulPose(Axis.ZP.rotationDegrees(-i * a * 2f));
			return true;
		}
	};
}
