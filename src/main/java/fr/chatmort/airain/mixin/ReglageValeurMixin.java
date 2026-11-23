package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import com.simibubi.create.foundation.blockEntity.behaviour.ValueSettingsScreen;

import fr.chatmort.airain.gui.InterfaceHD;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

/**
 * Interface HD, réglage de valeur de Create : Create rogne l'étiquette de chaque ligne à la largeur du texte, son bout droit
 * finissait coupé net. Juste avant d'écrire le texte de l'étiquette (brun 0x442000), on pose un embout arrondi (3 x 11 px,
 * pris en (162, 31) de la planche value_settings.png) sur les 3 derniers pixels de la plaque.
 */
@Mixin(value = ValueSettingsScreen.class, remap = false)
public abstract class ReglageValeurMixin {
	private static final ResourceLocation AIRAIN$PLANCHE = ResourceLocation.fromNamespaceAndPath("create", "textures/gui/value_settings.png");

	@Shadow
	private int maxLabelWidth;

	@Redirect(method = "renderWindow", at = @At(value = "INVOKE", target = "Lnet/minecraft/client/gui/GuiGraphics;drawString(Lnet/minecraft/client/gui/Font;Lnet/minecraft/network/chat/Component;IIIZ)I", ordinal = 2))   // 0 titre, 1 conseil, 2 étiquette, 3-4 texte du curseur
	private int airain$embout(GuiGraphics g, Font font, Component texte, int x, int y, int couleur, boolean ombre) {
		// l'étiquette va de x - 4 à x + maxLabelWidth + 4 ; son texte commence en x, une ligne sous le haut de la plaque
		if (InterfaceHD.actif() && (couleur & 0xFFFFFF) == 0x442000)
			g.blit(AIRAIN$PLANCHE, x + maxLabelWidth + 1, y - 1, 162, 31, 3, 11, 256, 256);
		return g.drawString(font, texte, x, y, couleur, ombre);
	}
}
