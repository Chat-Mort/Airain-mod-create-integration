package fr.chatmort.airain.trophee;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.level.material.FogType;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 1.71.3 : gravure du trophée de feu. Un effet caché (sans icône ni particules) porte l'information jusqu'au client :
 * dans la lave on y voit clair (brouillard repoussé) et on y nage plus vite.
 */
public final class Lave {
	private Lave() {}

	public static final DeferredRegister<MobEffect> EFFETS = DeferredRegister.create(Registries.MOB_EFFECT, "airain");
	public static final DeferredHolder<MobEffect, MobEffect> AISANCE = EFFETS.register("lava_ease", () -> new MobEffect(MobEffectCategory.BENEFICIAL, 0xE0602A) {});

	/** Côté client : nage plus rapide dans la lave (le mouvement du joueur est calculé par son client). */
	public static void nage(PlayerTickEvent.Pre e) {
		var p = e.getEntity();
		if (!p.level().isClientSide || !p.isInLava() || !p.hasEffect(AISANCE)) return;
		p.moveRelative(0.025f, new net.minecraft.world.phys.Vec3(p.xxa, 0, p.zza));
	}

	/** Côté client : brouillard de lave repoussé (on voit à une vingtaine de blocs). */
	public static void brouillard(ViewportEvent.RenderFog e) {
		if (e.getType() != FogType.LAVA) return;
		var p = net.minecraft.client.Minecraft.getInstance().player;
		if (p == null || !p.hasEffect(AISANCE)) return;
		e.setNearPlaneDistance(0f);
		e.setFarPlaneDistance(20f);
		e.setCanceled(true);
	}
}
