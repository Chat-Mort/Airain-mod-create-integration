package fr.chatmort.airain.fondation;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;

/** Toutes les fondations posées : dimension, position, nom, rayon. Persistant, indépendant des chunks chargés. */
public class FondationRegistre extends SavedData {
	public record Fondation(ResourceLocation dim, BlockPos pos, String nom, int rayon, String devise, int apparence) {
		public boolean contient(ResourceLocation d, double x, double z) {
			return dim.equals(d) && distance(x, z) <= rayon;
		}

		public double distance(double x, double z) {
			double dx = x - (pos.getX() + 0.5), dz = z - (pos.getZ() + 0.5);
			return Math.sqrt(dx * dx + dz * dz);
		}
	}

	private final Map<String, Fondation> fondations = new LinkedHashMap<>();

	public static FondationRegistre de(MinecraftServer serveur) {
		return serveur.overworld().getDataStorage().computeIfAbsent(
			new SavedData.Factory<>(FondationRegistre::new, FondationRegistre::charger, null), "airain_fondations");
	}

	private static String cle(ResourceLocation dim, BlockPos pos) {
		return dim + "|" + pos.asLong();
	}

	public void mettre(Level level, BlockPos pos, String nom, int rayon, String devise, int apparence) {
		ResourceLocation d = level.dimension().location();
		fondations.put(cle(d, pos), new Fondation(d, pos.immutable(), nom, rayon, devise, apparence)); setDirty();
	}

	public void retirer(Level level, BlockPos pos) {
		if (fondations.remove(cle(level.dimension().location(), pos)) != null) setDirty();
	}

	public List<Fondation> toutes() {
		return new ArrayList<>(fondations.values());
	}

	/** La fondation dont la zone contient ce point (la plus proche si plusieurs se chevauchent). */
	public Fondation zone(ResourceLocation dim, double x, double z) {
		Fondation meilleure = null;
		for (Fondation f : fondations.values())
			if (f.contient(dim, x, z) && (meilleure == null || f.distance(x, z) < meilleure.distance(x, z)))
				meilleure = f;
		return meilleure;
	}

	@Override
	public CompoundTag save(CompoundTag tag, HolderLookup.Provider registres) {
		ListTag l = new ListTag();
		for (Fondation f : fondations.values()) {
			CompoundTag c = new CompoundTag();
			c.putString("dim", f.dim().toString()); c.putLong("pos", f.pos().asLong());
			c.putString("nom", f.nom()); c.putInt("rayon", f.rayon()); c.putString("devise", f.devise()); c.putInt("apparence", f.apparence());
			l.add(c);
		}
		tag.put("fondations", l);
		return tag;
	}

	private static FondationRegistre charger(CompoundTag tag, HolderLookup.Provider registres) {
		FondationRegistre r = new FondationRegistre();
		for (Tag t : tag.getList("fondations", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) t;
			ResourceLocation d = ResourceLocation.parse(c.getString("dim"));
			BlockPos p = BlockPos.of(c.getLong("pos"));
			r.fondations.put(cle(d, p), new Fondation(d, p, c.getString("nom"), c.getInt("rayon"), c.getString("devise"), c.getInt("apparence")));
		}
		return r;
	}
}
