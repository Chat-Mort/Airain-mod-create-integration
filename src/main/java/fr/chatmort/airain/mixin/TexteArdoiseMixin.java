package fr.chatmort.airain.mixin;

import org.jetbrains.annotations.Nullable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.util.FormattedCharSequence;

import fr.chatmort.airain.gui.InterfaceHD;

/** Interface HD : les titres gris foncé des écrans de conteneur (vanilla et autres mods) s'écrivent en airain, avec ombre. */
@Mixin(GuiGraphics.class)
public abstract class TexteArdoiseMixin {
	@Shadow
	public abstract int drawString(Font font, @Nullable String text, int x, int y, int color, boolean dropShadow);

	@Shadow
	public abstract int drawString(Font font, FormattedCharSequence text, int x, int y, int color, boolean dropShadow);

	// texte simple (String) : redessiné en airain, l'appel d'origine est annulé
	@Inject(method = "drawString(Lnet/minecraft/client/gui/Font;Ljava/lang/String;IIIZ)I", at = @At("HEAD"), cancellable = true)
	private void airain$chaine(Font font, @Nullable String text, int x, int y, int color, boolean ombre, CallbackInfoReturnable<Integer> cir) {
		if (!ombre && InterfaceHD.texteSurArdoise(color))
			cir.setReturnValue(drawString(font, text, x, y, InterfaceHD.AIRAIN, true));
	}

	// texte composé (Component, passe par FormattedCharSequence) : même traitement
	@Inject(method = "drawString(Lnet/minecraft/client/gui/Font;Lnet/minecraft/util/FormattedCharSequence;IIIZ)I", at = @At("HEAD"), cancellable = true)
	private void airain$sequence(Font font, FormattedCharSequence text, int x, int y, int color, boolean ombre, CallbackInfoReturnable<Integer> cir) {
		if (!ombre && InterfaceHD.texteSurArdoise(color))
			cir.setReturnValue(drawString(font, text, x, y, InterfaceHD.AIRAIN, true));
	}
}
