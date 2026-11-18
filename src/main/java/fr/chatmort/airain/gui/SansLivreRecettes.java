package fr.chatmort.airain.gui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.ImageButton;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.recipebook.RecipeBookComponent;
import net.minecraft.client.gui.screens.recipebook.RecipeUpdateListener;
import net.minecraft.world.inventory.RecipeBookType;
import net.neoforged.neoforge.client.event.ScreenEvent;

import fr.chatmort.airain.mixin.BoutonImageAccesseur;

/**
 * Le livre de recettes vanilla n'est pas utilisé (EMI le remplace) : son bouton est retiré de l'inventaire, de l'établi
 * et des fours, où il se posait sur les gravures. Le livre est refermé avant l'ouverture de l'écran (sinon un livre resté
 * ouvert décalerait l'écran sans moyen de le refermer).
 */
public final class SansLivreRecettes {
	private SansLivreRecettes() {}

	public static void avant(ScreenEvent.Init.Pre e) {
		if (!(e.getScreen() instanceof RecipeUpdateListener)) return;
		var j = Minecraft.getInstance().player;
		if (j == null) return;
		for (RecipeBookType t : RecipeBookType.values()) j.getRecipeBook().setOpen(t, false);
	}

	public static void apres(ScreenEvent.Init.Post e) {
		if (!(e.getScreen() instanceof AbstractContainerScreen<?>) || !(e.getScreen() instanceof RecipeUpdateListener)) return;
		for (var w : java.util.List.copyOf(e.getListenersList()))
			if (w instanceof ImageButton b && ((BoutonImageAccesseur) b).airain$images() == RecipeBookComponent.RECIPE_BUTTON_SPRITES)
				e.removeListener(b);
	}
}
