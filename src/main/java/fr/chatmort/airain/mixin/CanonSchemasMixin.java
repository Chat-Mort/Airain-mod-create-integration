package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

import com.simibubi.create.content.schematics.cannon.SchematicannonScreen;

import fr.chatmort.airain.gui.InterfaceHD;

/** Interface HD, canon à schémas de Create : le titre (écrit à y + 2, contre le cadre) descend de 2 px. */
@Mixin(value = SchematicannonScreen.class, remap = false)
public abstract class CanonSchemasMixin {
	@ModifyArg(method = "renderBg", at = @At(value = "INVOKE", target = "Lnet/minecraft/client/gui/GuiGraphics;drawString(Lnet/minecraft/client/gui/Font;Lnet/minecraft/network/chat/Component;IIIZ)I", ordinal = 0), index = 3)
	private int airain$titre(int y) {
		return InterfaceHD.actif() ? y + 2 : y;
	}
}
