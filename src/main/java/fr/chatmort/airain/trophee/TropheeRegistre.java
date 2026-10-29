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

/** Liste persistante des trophées exposés (dimension + position → objet, plaque gravée), indépendante des chunks chargés. */
public class TropheeRegistre extends SavedData {
	public record Entree(ResourceLocation objet, String plaque, int jour) {}
	private final Map<String, Entree> socles = new HashMap<>();

	public static TropheeRegistre de(MinecraftServer serveur) {
		return serveur.overworld().getDataStorage().computeIfAbsent(
			new SavedData.Factory<>(TropheeRegistre::new, TropheeRegistre::charger, null), "airain_trophees");
	}

	private static String cle(Level level, BlockPos pos) {
		return level.dimension().location() + "|" + pos.asLong();
	}

	public void poser(Level level, BlockPos pos, ResourceLocation objet, String plaque, int jour) {
		socles.put(cle(level, pos), new Entree(objet, plaque, jour)); setDirty();
	}

	/** Toutes les entrées, avec leur dimension et leur position. */
	public java.util.List<java.util.Map.Entry<net.minecraft.core.GlobalPos, Entree>> entrees() {
		java.util.List<java.util.Map.Entry<net.minecraft.core.GlobalPos, Entree>> l = new java.util.ArrayList<>();
		socles.forEach((k, v) -> {
			String[] p = k.split("\\|");
			l.add(java.util.Map.entry(net.minecraft.core.GlobalPos.of(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(p[0])),
				BlockPos.of(Long.parseLong(p[1]))), v));
		});
		return l;
	}

	/** Y a-t-il au moins un trophée exposé dans la zone de cette fondation ? */
	public boolean dansZone(fr.chatmort.airain.fondation.FondationRegistre.Fondation f) {
		for (var e : entrees())
			if (f.contient(e.getKey().dimension().location(), e.getKey().pos().getX() + 0.5, e.getKey().pos().getZ() + 0.5)) return true;
		return false;
	}

	public void retirer(Level level, BlockPos pos) {
		if (socles.remove(cle(level, pos)) != null) setDirty();
	}

	public Collection<ResourceLocation> objets() {
		return socles.values().stream().map(Entree::objet).toList();
	}

	/** Retire les entrées dont le socle (chargé) n'existe plus ou est vide. */
	public void nettoyer(MinecraftServer serveur) {
		Iterator<Map.Entry<String, Entree>> it = socles.entrySet().iterator();
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
		socles.forEach((k, v) -> {
			CompoundTag e = new CompoundTag();
			e.putString("objet", v.objet().toString()); e.putString("plaque", v.plaque()); e.putInt("jour", v.jour());
			l.put(k, e);
		});
		tag.put("socles", l);
		return tag;
	}

	private static TropheeRegistre charger(CompoundTag tag, HolderLookup.Provider registres) {
		TropheeRegistre r = new TropheeRegistre();
		CompoundTag l = tag.getCompound("socles");
		for (String k : l.getAllKeys()) {
			if (l.get(k) instanceof CompoundTag e)
				r.socles.put(k, new Entree(ResourceLocation.parse(e.getString("objet")), e.getString("plaque"), e.getInt("jour")));
			else r.socles.put(k, new Entree(ResourceLocation.parse(l.getString(k)), "", 0));   // ancien format
		}
		return r;
	}
}
