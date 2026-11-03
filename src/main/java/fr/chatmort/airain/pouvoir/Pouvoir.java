package fr.chatmort.airain.pouvoir;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;

import fr.chatmort.airain.fondation.FondationRegistre;

/**
 * Le siège du pouvoir (un seul par monde) : trône impérial (fin Empire) ou solium de la Prêtresse (fin Écho).
 * Assis, on promulgue un décret ou on entonne un chant : actif une heure de jeu effective, changeable après 15 minutes.
 */
public class Pouvoir extends SavedData {
	public static final long DUREE = 72000, CHANGEMENT = 18000;
	public static final String[] DECRETS = {"guerre", "forge", "prosperite"};
	public static final String[] CHANTS = {"ames", "croissance", "resonance"};

	ResourceLocation dim;
	BlockPos pos;
	boolean trone;
	String effet = "";
	long debut;

	public static Pouvoir de(MinecraftServer s) {
		return s.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Pouvoir::new, Pouvoir::charger, null), "airain_pouvoir");
	}

	static long maintenant(MinecraftServer s) { return s.overworld().getGameTime(); }

	public boolean present() { return pos != null; }

	/** L'effet donné est-il en cours ? */
	public static boolean actif(MinecraftServer s, String e) {
		if (s == null) return false;
		Pouvoir p = de(s);
		return p.pos != null && p.effet.equals(e) && maintenant(s) < p.debut + DUREE;
	}

	/** Le siège en place se trouve dans cette base ? */
	public static boolean dansBase(MinecraftServer s, boolean trone, ResourceLocation dim, double x, double z) {
		Pouvoir p = de(s);
		if (p.pos == null || p.trone != trone || !p.dim.equals(dim)) return false;
		var reg = FondationRegistre.de(s);
		var f = reg.zone(dim, x, z);
		return f != null && f.equals(reg.zone(p.dim, p.pos.getX() + 0.5, p.pos.getZ() + 0.5));
	}

	/** Base contenant le siège (null s'il n'y en a pas). */
	public FondationRegistre.Fondation base(MinecraftServer s) {
		return pos == null ? null : FondationRegistre.de(s).zone(dim, pos.getX() + 0.5, pos.getZ() + 0.5);
	}

	/** Point d'arrivée devant le siège. */
	public ServerLevel niveau(MinecraftServer s) { return pos == null ? null : s.getLevel(ResourceKey.create(Registries.DIMENSION, dim)); }

	/** Décret de la forge : rendement doublé pour une machine dans une base. */
	public static boolean forge(Level l, BlockPos p) {
		if (l == null || l.isClientSide || !(l instanceof ServerLevel sl) || !actif(sl.getServer(), "forge")) return false;
		return FondationRegistre.de(sl.getServer()).zone(sl.dimension().location(), p.getX() + 0.5, p.getZ() + 0.5) != null;
	}

	/** Chant de résonance : sources d'Ars Nouveau doublées. */
	public static boolean resonance(Level l) {
		return l != null && !l.isClientSide && l instanceof ServerLevel sl && actif(sl.getServer(), "resonance");
	}

	/** Objets dont la transformation n'est jamais doublée (étapes suivantes, boucles de duplication). */
	public static final net.minecraft.tags.TagKey<net.minecraft.world.item.Item> EXCLUS =
		net.minecraft.tags.TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("airain", "forge_exclue"));

	public static boolean exclu(net.minecraft.world.item.ItemStack s) { return s.is(EXCLUS); }
	public static boolean exclu(net.minecraft.world.item.crafting.Recipe<?> r) {
		for (var ing : r.getIngredients()) for (var s : ing.getItems()) if (s.is(EXCLUS)) return true;
		return false;
	}

	/** Ventilateur en cours de traitement (posé par les mixins de Create). */
	public static final ThreadLocal<BlockPos> FAN = new ThreadLocal<>();

	/** Chaque produit en double. */
	public static java.util.List<net.minecraft.world.item.ItemStack> doubler(java.util.List<net.minecraft.world.item.ItemStack> l) {
		if (l == null) return null;
		java.util.List<net.minecraft.world.item.ItemStack> r = new java.util.ArrayList<>(l.size() * 2);
		for (var s : l) { r.add(s); if (!s.isEmpty()) r.add(s.copy()); }
		return r;
	}

	long reste(MinecraftServer s) { return Math.max(0, debut + DUREE - maintenant(s)); }
	long attente(MinecraftServer s) { return effet.isEmpty() || reste(s) == 0 ? 0 : Math.max(0, debut + CHANGEMENT - maintenant(s)); }

	void poser(Level l, BlockPos p, boolean t) { dim = l.dimension().location(); pos = p.immutable(); trone = t; effet = ""; setDirty(); }
	void retirer() { pos = null; dim = null; effet = ""; setDirty(); }
	void choisir(MinecraftServer s, String e) { effet = e; debut = maintenant(s); setDirty(); }

	@Override
	public CompoundTag save(CompoundTag t, HolderLookup.Provider r) {
		if (pos != null) { t.putString("dim", dim.toString()); t.put("pos", NbtUtils.writeBlockPos(pos)); t.putBoolean("trone", trone); }
		t.putString("effet", effet);
		t.putLong("debut", debut);
		return t;
	}

	private static Pouvoir charger(CompoundTag t, HolderLookup.Provider r) {
		Pouvoir p = new Pouvoir();
		if (t.contains("dim")) { p.dim = ResourceLocation.parse(t.getString("dim")); p.pos = NbtUtils.readBlockPos(t, "pos").orElse(null); p.trone = t.getBoolean("trone"); }
		p.effet = t.getString("effet");
		p.debut = t.getLong("debut");
		return p;
	}
}
