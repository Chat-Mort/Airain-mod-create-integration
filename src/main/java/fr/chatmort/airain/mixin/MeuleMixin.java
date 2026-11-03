package fr.chatmort.airain.mixin;

import java.util.List;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.simibubi.create.content.kinetics.millstone.MillingRecipe;
import com.simibubi.create.content.kinetics.millstone.MillstoneBlockEntity;

import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

import fr.chatmort.airain.pouvoir.Pouvoir;

/** Décret de la forge : la meule d'une base rend le double. */
@Mixin(value = MillstoneBlockEntity.class, remap = false)
public abstract class MeuleMixin {
	@WrapOperation(method = "process", at = @At(value = "INVOKE", target = "rollResults(Lnet/minecraft/util/RandomSource;)Ljava/util/List;"))
	private List<ItemStack> airain$forge(MillingRecipe r, RandomSource rnd, Operation<List<ItemStack>> op) {
		List<ItemStack> l = op.call(r, rnd);
		BlockEntity be = (BlockEntity) (Object) this;
		return Pouvoir.forge(be.getLevel(), be.getBlockPos()) && !Pouvoir.exclu(r) ? Pouvoir.doubler(l) : l;
	}
}
