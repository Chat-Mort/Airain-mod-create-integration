package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import com.simibubi.create.content.kinetics.fan.AirCurrent;
import com.simibubi.create.content.kinetics.fan.IAirCurrentSource;

/** Retient la position du ventilateur pendant qu'il traite les objets (pour le décret de la forge). */
@Mixin(value = AirCurrent.class, remap = false)
public abstract class CourantMixin {
	@Shadow @Final public IAirCurrentSource source;

	@Inject(method = {"tickAffectedEntities", "tickAffectedHandlers"}, at = @At("HEAD"))
	private void airain$debut(CallbackInfo ci) { fr.chatmort.airain.pouvoir.Pouvoir.FAN.set(source.getAirCurrentPos()); }

	@Inject(method = {"tickAffectedEntities", "tickAffectedHandlers"}, at = @At("RETURN"))
	private void airain$fin(CallbackInfo ci) { fr.chatmort.airain.pouvoir.Pouvoir.FAN.remove(); }
}
