package fr.chatmort.airain.affichage;

import com.simibubi.create.content.redstone.displayLink.DisplayLinkContext;
import com.simibubi.create.content.redstone.displayLink.source.PercentOrProgressBarDisplaySource;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntity;

/**
 * Source de la liaison d'affichage pour le moule de Create Big Cannons (lu sans dépendre du mod) : pendant le
 * remplissage, la part de métal versée ; pendant le refroidissement, la part du temps écoulée.
 */
public class SourceMoulage extends PercentOrProgressBarDisplaySource {
	@Override
	protected Float getProgress(DisplayLinkContext ctx) {
		BlockEntity be = ctx.getSourceBlockEntity();
		if (be == null || ctx.level() == null) return null;
		try {
			Object c = be.getClass().getMethod("getControllerBE").invoke(be);
			BlockEntity moule = c instanceof BlockEntity b ? b : be;
			CompoundTag t = moule.saveWithoutMetadata(ctx.level().registryAccess());
			int reste = t.getInt("CastingTime"), total = t.getInt("StartCastingTime");
			if (reste > 0 && total > 1) return 1f - reste / (float) total;
			Object f = moule.getClass().getMethod("getFillState").invoke(moule);
			return f instanceof Float v ? Math.max(0, Math.min(1, v)) : null;
		} catch (ReflectiveOperationException | RuntimeException e) {
			return null;
		}
	}
	@Override protected boolean progressBarActive(DisplayLinkContext ctx) { return false; }
	@Override protected String getTranslationKey() { return "cannon_casting"; }
	@Override protected boolean allowsLabeling(DisplayLinkContext ctx) { return true; }
}
