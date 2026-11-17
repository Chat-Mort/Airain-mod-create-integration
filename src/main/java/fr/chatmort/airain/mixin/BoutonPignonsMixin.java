package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.components.AbstractWidget;

import fr.chatmort.airain.gui.InterfaceHD;

/** Interface HD : sur les boutons à chaîne, le texte (et son défilement s'il est long) reste entre les deux pignons. */
@Mixin(AbstractButton.class)
public abstract class BoutonPignonsMixin {
	// marge de 2 px du jeu portée à la largeur d'un pignon, sur les boutons assez larges pour en avoir deux
	@ModifyArg(method = "renderString", at = @At(value = "INVOKE",
		target = "Lnet/minecraft/client/gui/components/AbstractButton;renderScrollingString(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/client/gui/Font;II)V"), index = 2)
	private int airain$entrePignons(int marge) {
		return InterfaceHD.actif() && ((AbstractWidget) (Object) this).getWidth() >= 60 ? InterfaceHD.MARGE_PIGNONS : marge;
	}
}
