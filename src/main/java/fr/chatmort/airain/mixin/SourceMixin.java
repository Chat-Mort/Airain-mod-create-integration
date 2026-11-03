package fr.chatmort.airain.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

import net.minecraft.world.level.block.entity.BlockEntity;

import fr.chatmort.airain.pouvoir.Pouvoir;

/** Chant de résonance : ce que produisent les sourcelinks d'Ars Nouveau est doublé. */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.api.source.AbstractSourceMachine", remap = false)
public abstract class SourceMixin {
	@Unique
	private static final String SOURCELINK = "com.hollingsworth.arsnouveau.common.block.tile.SourcelinkTile";

	@ModifyVariable(method = "addSource(I)I", at = @At("HEAD"), argsOnly = true)
	private int airain$resonance(int source) {
		if (source <= 0) return source;
		Object o = this;
		boolean lien = false;
		for (Class<?> c = o.getClass(); c != null; c = c.getSuperclass()) if (c.getName().equals(SOURCELINK)) { lien = true; break; }
		return lien && o instanceof BlockEntity be && Pouvoir.resonance(be.getLevel()) ? source * 2 : source;
	}
}
