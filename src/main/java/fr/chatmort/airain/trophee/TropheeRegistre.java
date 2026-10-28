package fr.chatmort.airain.trophee;

import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;

/** Liste persistante des trophées exposés (dimension + position → objet), indépendante des chunks chargés. */
public class TropheeRegistre extends SavedData {
	private final Map<String, ResourceLocation> socles = new HashMap<>();

	public static TropheeRegistre de(MinecraftServer serveur) {
		return serveur.overworld().getDataStorage().computeIfAbsent(
			new SavedData.Factory<>(TropheeRegistre::new, TropheeRegistre::charger, null), "airain_trophees");
	}

	private static String cle(Level level, BlockPos pos) {
		return level.dimension().location() + "|" + pos.asLong();
	}

	public void poser(Level level, BlockPos pos, ResourceLocation objet) {
		socles.put(cle(level, pos), objet); setDirty();
	}

	public void retirer(Level level, BlockPos pos) {
		if (socles.remove(cle(level, pos)) != null) setDirty();
	}

	public Collection<ResourceLocation> objets() {
		return socles.values();
	}

	/** Retire les entrées dont le socle (chargé) n'existe plus ou est vide. */
	public void nettoyer(MinecraftServer serveur) {
		Iterator<Map.Entry<String, ResourceLocation>> it = socles.entrySet().iterator();
		while (it.hasNext()) {
			String[] p = it.next().getKey().split("\\|");
			ServerLevel level = serveur.getLevel(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(p[0])));
			BlockPos pos = BlockPos.of(Long.parseLong(p[1]));
			if (level == null) { it.remove(); setDirty(); continue; }
			if (!level.isLoaded(pos)) continue;
			if (!(level.getBlockEntity(pos) instanceof SocleBlockEntity s) || s.trophee().isEmpty()) { it.remove(); setDirty(); }
		}
	}

	@Override
	public CompoundTag save(CompoundTag tag, HolderLookup.Provider registres) {
		CompoundTag l = new CompoundTag();
		socles.forEach((k, v) -> l.putString(k, v.toString()));
		tag.put("socles", l);
		return tag;
	}

	private static TropheeRegistre charger(CompoundTag tag, HolderLookup.Provider registres) {
		TropheeRegistre r = new TropheeRegistre();
		CompoundTag l = tag.getCompound("socles");
		for (String k : l.getAllKeys()) r.socles.put(k, ResourceLocation.parse(l.getString(k)));
		return r;
	}
}
