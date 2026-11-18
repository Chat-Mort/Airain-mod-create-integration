package fr.chatmort.airain.affichage;

import com.simibubi.create.api.behaviour.display.DisplayTarget;
import com.simibubi.create.content.redstone.displayLink.DisplayLinkContext;
import com.simibubi.create.content.redstone.displayLink.target.DisplayTargetStats;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.phys.AABB;

import java.util.List;

/** Le tableau émaillé comme cible de la liaison d'affichage de Create : une liaison par ligne. */
public class CibleEmail extends DisplayTarget {
	@Override
	public void acceptText(int ligne, List<MutableComponent> texte, DisplayLinkContext ctx) {
		EmailBlockEntity e = EmailBlockEntity.de(ctx.getTargetBlockEntity());
		if (e == null) return;
		// la première ligne reçue va sur la ligne choisie ; les suivantes (listes) sur les lignes d'après, si elles ne sont pas déjà prises
		for (int i = 0; i < texte.size() && ligne + i < e.lignesLiables(); i++) {
			if (i == 0) reserve(ligne, e, ctx);
			else if (isReserved(ligne + i, e, ctx)) break;
			// les listes de Create (stock, etc.) complètent chaque ligne d'espaces pour caler les nombres à droite d'un
			// panneau de 32 colonnes : on les retire, l'alignement choisi pour la ligne du tableau s'applique alors
			e.recevoir(ligne + i, texte.get(i).getString().strip().replaceAll(" {2,}", " "));
		}
	}
	@Override
	public DisplayTargetStats provideStats(DisplayLinkContext ctx) {
		EmailBlockEntity e = EmailBlockEntity.de(ctx.getTargetBlockEntity());
		return new DisplayTargetStats(e == null ? 1 : e.lignesLiables(), 32, this);
	}
	@Override
	public AABB getMultiblockBounds(LevelAccessor l, BlockPos p) {
		EmailBlockEntity e = EmailBlockEntity.de(l.getBlockEntity(p));
		return e == null ? super.getMultiblockBounds(l, p) : e.getRenderBoundingBox().deflate(1);
	}
	@Override
	public Component getLineOptionText(int ligne) {
		return Component.translatable("airain.email.ligne", ligne + 1);
	}
}
