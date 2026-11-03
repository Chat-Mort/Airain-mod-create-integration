package fr.chatmort.airain.mixin;

import java.util.List;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.simibubi.create.content.kinetics.crusher.CrushingWheelControllerBlockEntity;
import com.simibubi.create.content.processing.recipe.StandardProcessingRecipe;

import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

import fr.chatmort.airain.pouvoir.Pouvoir;

/** Décret de la forge : les concasseurs d'une base rendent le double. */
@Mixin(value = CrushingWheelControllerBlockEntity.class, remap = false)
public abstract class ConcasseurMixin {
	@WrapOperation(method = "applyRecipe", at = @At(value = "INVOKE", target = "rollResults(Lnet/minecraft/util/RandomSource;)Ljava/util/List;"))
	private List<ItemStack> airain$forge(StandardProcessingRecipe<?> r, RandomSource rnd, Operation<List<ItemStack>> op) {
		List<ItemStack> l = op.call(r, rnd);
		BlockEntity be = (BlockEntity) (Object) this;
		return Pouvoir.forge(be.getLevel(), be.getBlockPos()) && !Pouvoir.exclu(r) ? Pouvoir.doubler(l) : l;
	}
}
