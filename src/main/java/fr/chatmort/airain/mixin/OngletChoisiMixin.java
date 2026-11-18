package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.TabButton;

import fr.chatmort.airain.gui.InterfaceHD;

/** Interface HD : l'onglet choisi garde ses rivets et ses coins arrondis (le jeu repeignait le fond des menus par-dessus). */
@Mixin(TabButton.class)
public abstract class OngletChoisiMixin {
	// l'onglet choisi a déjà son fond clair dans sa texture : pas de fond de menu posé dessus
	@Inject(method = "renderMenuBackground", at = @At("HEAD"), cancellable = true)
	private void airain$sansFond(GuiGraphics g, int x0, int y0, int x1, int y1, CallbackInfo ci) {
		if (InterfaceHD.actif()) ci.cancel();
	}
}
