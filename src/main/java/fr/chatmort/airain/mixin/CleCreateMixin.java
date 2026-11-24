package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import com.tterrag.registrate.util.entry.ItemProviderEntry;

import net.minecraft.world.item.Item;

/**
 * 1.69.1 : Create vérifie presque partout « est-ce exactement ma clé ? » (AllItems.WRENCH.isIn / is). La clé à molette
 * d'airain, son amélioration, doit répondre oui : trains, tapis, poutres, entonnoirs, bras mécaniques, réglages…
 */
@Mixin(value = ItemProviderEntry.class, remap = false)
public abstract class CleCreateMixin {
	@Inject(method = "is(Lnet/minecraft/world/item/Item;)Z", at = @At("HEAD"), cancellable = true)
	private void airain$cleAirain(Item item, CallbackInfoReturnable<Boolean> cir) {
		if (item != null && (Object) this == com.simibubi.create.AllItems.WRENCH && fr.chatmort.airain.fonderie.CleAirain.CLE.isBound()
			&& item == fr.chatmort.airain.fonderie.CleAirain.CLE.get()) cir.setReturnValue(true);
	}
}
