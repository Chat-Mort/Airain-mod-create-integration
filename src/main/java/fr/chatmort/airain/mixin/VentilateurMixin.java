package fr.chatmort.airain.mixin;

import java.util.List;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.simibubi.create.content.kinetics.fan.processing.AllFanProcessingTypes;
import com.simibubi.create.content.kinetics.fan.processing.FanProcessing;
import com.simibubi.create.content.kinetics.fan.processing.FanProcessingType;

import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import fr.chatmort.airain.pouvoir.Pouvoir;

/** Décret de la forge : lavage et cuisson au ventilateur doublés dans les bases (pas la hantise). */
@Mixin(value = FanProcessing.class, remap = false)
public abstract class VentilateurMixin {
	@WrapOperation(method = "applyProcessing", at = @At(value = "INVOKE",
		target = "Lcom/simibubi/create/content/kinetics/fan/processing/FanProcessingType;process(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/level/Level;)Ljava/util/List;"))
	private static List<ItemStack> airain$forge(FanProcessingType type, ItemStack stack, Level level, Operation<List<ItemStack>> op) {
		boolean exclu = Pouvoir.exclu(stack);
		List<ItemStack> l = op.call(type, stack, level);
		BlockPos fan = Pouvoir.FAN.get();
		if (fan == null || exclu || l == null || l.isEmpty()) return l;
		if (type != AllFanProcessingTypes.SPLASHING && type != AllFanProcessingTypes.BLASTING && type != AllFanProcessingTypes.SMOKING) return l;
		return Pouvoir.forge(level, fan) ? Pouvoir.doubler(l) : l;
	}
}
