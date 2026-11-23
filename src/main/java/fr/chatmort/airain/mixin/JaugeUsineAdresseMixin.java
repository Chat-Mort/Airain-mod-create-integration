package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import com.simibubi.create.content.logistics.AddressEditBox;
import com.simibubi.create.content.logistics.factoryBoard.FactoryPanelScreen;

import fr.chatmort.airain.gui.InterfaceHD;

/**
 * Interface HD, jauge d'usine de Create : l'adresse s'écrit sur un ticket de papier clair. Create la laisse dans la couleur
 * par défaut des champs (gris très clair), illisible sur le papier : elle passe à l'encre du titre de Create (0x3D3C48),
 * comme l'adresse de la grenouille-port.
 */
@Mixin(value = FactoryPanelScreen.class, remap = false)
public abstract class JaugeUsineAdresseMixin {
	@Shadow
	private AddressEditBox addressBox;

	@Inject(method = "init", at = @At("TAIL"))
	private void airain$encre(CallbackInfo ci) {
		if (InterfaceHD.actif() && addressBox != null) addressBox.setTextColor(0x3D3C49);   // 0x3D3C49 et non 48 : la teinte des titres, recolorée en airain, ne doit pas toucher l'adresse
	}
}
