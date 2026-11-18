package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import dev.ftb.mods.ftblibrary.icon.Color4I;
import dev.ftb.mods.ftblibrary.ui.Theme;
import dev.ftb.mods.ftbquests.client.ClientQuestFile;
import dev.ftb.mods.ftbquests.quest.Chapter;
import net.minecraft.client.gui.GuiGraphics;

import fr.chatmort.airain.gui.InterfaceHD;

/**
 * Interface HD, liste des chapitres de FTB Quests : chaque chapitre sur sa plaque d'ardoise, titre lisible selon son état
 * (le jeu l'assombrissait jusqu'au brun illisible), jauge d'avancement gravée sous le titre.
 */
@Mixin(targets = "dev.ftb.mods.ftbquests.client.gui.quests.ChapterPanel$ChapterButton", remap = false)
public abstract class ChapitresQuetesMixin {
	@Shadow @Final private Chapter chapter;

	// plaque du chapitre, posée sous le surlignage et le titre du jeu
	@Inject(method = "draw", at = @At("HEAD"))
	private void airain$plaque(GuiGraphics g, Theme theme, int x, int y, int w, int h, CallbackInfo ci) {
		if (!InterfaceHD.actif()) return;
		g.fill(x + 1, y, x + w - 1, y + h, 0xFF30343D);
		g.fill(x + 1, y, x + w - 1, y + 1, 0xFF454A56);            // arête claire en haut
		g.fill(x + 1, y + h - 1, x + w - 1, y + h, 0xFF1F2228);    // joint sombre en bas
		g.fill(x + 1, y + 1, x + 3, y + h - 1, 0xFFA8763C);        // tranche d'airain à gauche
		g.fill(x + 1, y + 1, x + 2, y + h - 1, 0xFFE1BA6E);
	}

	// couleur du titre : airain si terminé, airain sombre si commencé, gris clair sinon ; à peine assombri hors survol
	@ModifyVariable(method = "draw", at = @At("STORE"), ordinal = 0)
	private Color4I airain$titre(Color4I c) {
		if (!InterfaceHD.actif()) return c;
		var f = ClientQuestFile.INSTANCE;
		if (f == null || f.selfTeamData == null) return c;
		int rgb = f.selfTeamData.isCompleted(chapter) ? InterfaceHD.AIRAIN
			: f.selfTeamData.isStarted(chapter) ? InterfaceHD.AIRAIN_SOMBRE : 0xC8CCD4;
		return Color4I.rgb(rgb);
	}

	// jauge d'avancement : fente gravée qui se remplit (or poli une fois le chapitre fini, cuivre en cours)
	@Inject(method = "draw", at = @At("TAIL"))
	private void airain$jauge(GuiGraphics g, Theme theme, int x, int y, int w, int h, CallbackInfo ci) {
		if (!InterfaceHD.actif()) return;
		var f = ClientQuestFile.INSTANCE;
		if (f == null || f.selfTeamData == null) return;
		int x0 = x + 16 + (chapter.getGroup().isDefaultGroup() ? 0 : 7), x1 = x + w - 15, yb = y + h - 3;
		if (x1 - x0 < 10) return;
		g.fill(x0, yb, x1, yb + 1, 0xFF121418);
		g.fill(x0, yb + 1, x1, yb + 2, 0xFF3A3E48);
		int p = f.selfTeamData.getRelativeProgress(chapter);
		if (p > 0) g.fill(x0, yb, x0 + (x1 - x0) * Math.min(100, p) / 100, yb + 1, p >= 100 ? 0xFFF3D694 : 0xFFC2703E);
	}
}
