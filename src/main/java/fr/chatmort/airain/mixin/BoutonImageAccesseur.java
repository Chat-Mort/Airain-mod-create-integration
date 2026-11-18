package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import net.minecraft.client.gui.components.ImageButton;
import net.minecraft.client.gui.components.WidgetSprites;

/** Lecture des images d'un bouton : sert à reconnaître le bouton du livre de recettes. */
@Mixin(ImageButton.class)
public interface BoutonImageAccesseur {
	@Accessor("sprites")
	WidgetSprites airain$images();
}
