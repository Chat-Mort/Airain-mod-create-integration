package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

import net.minecraft.client.Minecraft;
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
		AbstractWidget b = (AbstractWidget) (Object) this;
		if (!InterfaceHD.actif() || b.getWidth() < 60) return marge;
		// un texte un peu trop long mord sur la couronne des pignons plutôt que de défiler (jamais sur leur trou)
		int place = (b.getWidth() - Minecraft.getInstance().font.width(b.getMessage())) / 2;
		return Math.max(InterfaceHD.MARGE_PIGNONS_MIN, Math.min(InterfaceHD.MARGE_PIGNONS, place));
	}
}
