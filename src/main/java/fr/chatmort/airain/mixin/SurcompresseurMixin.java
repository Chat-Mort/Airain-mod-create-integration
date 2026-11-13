package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.content.kinetics.steamEngine.PoweredShaftBlockEntity;

import fr.chatmort.airain.fonderie.Mecanique;

/** Surcompresseur impérial : +50 % de capacité de stress pour le générateur qu'il alimente (roues, moulins, moteur à vapeur…). */
@Mixin(value = {KineticBlockEntity.class, PoweredShaftBlockEntity.class}, remap = false)
public abstract class SurcompresseurMixin {
	@Inject(method = "calculateAddedStressCapacity", at = @At("RETURN"), cancellable = true)
	private void airain$surcompression(CallbackInfoReturnable<Float> cir) {
		float f = Mecanique.facteur((KineticBlockEntity) (Object) this);
		if (f != 1f) cir.setReturnValue(cir.getReturnValue() * f);
	}
}
