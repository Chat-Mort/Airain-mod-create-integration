package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

import com.simibubi.create.content.schematics.table.SchematicTableScreen;

import fr.chatmort.airain.gui.InterfaceHD;

/** Interface HD, table à schémas de Create : titre et bouton « valider » remis en place sur la nouvelle texture. */
@Mixin(value = SchematicTableScreen.class, remap = false)
public abstract class TableSchemasMixin {
	// le bouton « valider » (premier IconButton de init) descend de 2 px pour être centré sur la ligne des cases (y 59)
	@ModifyArg(method = "init", at = @At(value = "INVOKE", target = "Lcom/simibubi/create/foundation/gui/widget/IconButton;<init>(IILnet/createmod/catnip/gui/element/ScreenElement;)V", ordinal = 0), index = 1)
	private int airain$valider(int y) {
		return InterfaceHD.actif() ? y + 2 : y;
	}

	// le titre (écrit à y + 4) descend de 2 px pour ne plus toucher le cadre
	@ModifyArg(method = "renderBg", at = @At(value = "INVOKE", target = "Lnet/minecraft/client/gui/GuiGraphics;drawString(Lnet/minecraft/client/gui/Font;Lnet/minecraft/network/chat/Component;IIIZ)I", ordinal = 0), index = 3)
	private int airain$titre(int y) {
		return InterfaceHD.actif() ? y + 2 : y;
	}
}
