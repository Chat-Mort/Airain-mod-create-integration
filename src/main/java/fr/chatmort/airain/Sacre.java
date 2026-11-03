package fr.chatmort.airain;

import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import org.joml.Vector3f;

/** Netherite sacrée : la plaque, et la marque « sacrée » portée par les objets améliorés (couronne, casque couronné). */
public final class Sacre {
	private Sacre() {}
	public static final String CLE = "airain_sacree";

	public static boolean plaque(ItemStack s) { return s.is(AirainMod.PLAQUE_SACREE.get()); }

	public static boolean sacree(ItemStack s) {
		if (s.is(AirainMod.CASQUE_COURONNE_SACREE.get())) return true;
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d != null && d.copyTag().getBoolean(CLE);
	}

	public static void marquer(ItemStack s, boolean oui) {
		CompoundTag t = s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
		if (oui) t.putBoolean(CLE, true); else t.remove(CLE);
		if (t.isEmpty()) s.remove(DataComponents.CUSTOM_DATA); else s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
	}

	/** Consomme une plaque et joue la cérémonie (son, étincelles d'or et éclat d'étoile) au-dessus du bloc. */
	public static void consacrer(ServerLevel sl, BlockPos pos, Player p, ItemStack pile, String message) {
		if (!p.getAbilities().instabuild) pile.shrink(1);
		double x = pos.getX() + 0.5, y = pos.getY() + 1.2, z = pos.getZ() + 0.5;
		sl.playSound(null, pos, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 1f, 0.7f);
		sl.playSound(null, pos, SoundEvents.BEACON_POWER_SELECT, SoundSource.BLOCKS, 0.8f, 1.4f);
		sl.sendParticles(ParticleTypes.END_ROD, x, y, z, 30, 0.4, 0.6, 0.4, 0.08);
		sl.sendParticles(new DustParticleOptions(new Vector3f(1f, 0.84f, 0.43f), 1.2f), x, y, z, 40, 0.6, 0.8, 0.6, 0);
		p.displayClientMessage(Component.translatable(message), true);
	}

	public static void deja(Player p) { p.displayClientMessage(Component.translatable("airain.sacre.deja"), true); }
}
