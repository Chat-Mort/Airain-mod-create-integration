package fr.chatmort.airain.atlas;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import fr.chatmort.airain.fondation.FondationRegistre;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.LongArrayTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/** L'atlas impérial : chunks parcourus, lieux visités et morts, partagés par toute l'équipe. */
public class Atlas extends SavedData {
	public record Lieu(String dim, int x, int z, String id, String type, int jour) {}
	public record Mort(String dim, int x, int z, String nom, int jour) {}

	private final Map<String, LongOpenHashSet> parcourus = new HashMap<>();
	private final Map<String, Lieu> lieux = new LinkedHashMap<>();
	private final List<Mort> morts = new ArrayList<>();

	public static Atlas de(MinecraftServer s) {
		return s.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Atlas::new, Atlas::charger, null), "airain_atlas");
	}

	static int jour(MinecraftServer s) { return (int) (s.overworld().getDayTime() / 24000L) + 1; }

	/** Catégorie d'icône d'une structure. */
	static String type(String id) {
		if (id.startsWith("kubejs:avant_poste") || id.equals("kubejs:cite_mecanique")) return id.contains("refractaire") ? "camp" : "poste";
		if (id.contains("refractaire") || id.equals("kubejs:abri_nether") || id.equals("kubejs:sanctuaire_refractaire")) return "camp";
		if (id.equals("kubejs:relais_brise") || id.equals("kubejs:grand_relais")) return "relais";
		if (id.startsWith("kubejs:station")) return "station";
		if (id.startsWith("kubejs:ruine") || id.equals("kubejs:champ_bataille") || id.contains("ruin")) return "ruine";
		return "lieu";
	}

	/** Toutes les deux secondes : le chunk du joueur est parcouru ; la structure où il se trouve est notée. */
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 40 != 13 || p.isSpectator()) return;
		ServerLevel sl = p.serverLevel();
		Atlas a = de(p.server);
		String dim = sl.dimension().location().toString();
		if (a.parcourus.computeIfAbsent(dim, k -> new LongOpenHashSet()).add(p.chunkPosition().toLong())) a.setDirty();
		var reg = sl.registryAccess().registryOrThrow(Registries.STRUCTURE);
		for (var s : sl.structureManager().getAllStructuresAt(p.blockPosition()).keySet()) {
			StructureStart st = sl.structureManager().getStructureAt(p.blockPosition(), s);
			if (!st.isValid()) continue;
			ResourceLocation id = reg.getKey(s);
			if (id == null) continue;
			String cle = dim + "|" + st.getChunkPos().toLong();
			if (a.lieux.containsKey(cle)) continue;
			var c = st.getBoundingBox().getCenter();
			a.lieux.put(cle, new Lieu(dim, c.getX(), c.getZ(), id.toString(), type(id.toString()), jour(p.server)));
			a.setDirty();
		}
	}

	public static void mort(LivingDeathEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		Atlas a = de(p.server);
		a.morts.add(new Mort(p.level().dimension().location().toString(), p.getBlockX(), p.getBlockZ(), p.getGameProfile().getName(), jour(p.server)));
		a.setDirty();
	}

	/** Ce qu'il faut au livre, pour la dimension du joueur. */
	public CompoundTag paquet(ServerPlayer p) {
		String dim = p.level().dimension().location().toString();
		CompoundTag t = new CompoundTag();
		t.putString("dim", dim);
		LongOpenHashSet ch = parcourus.get(dim);
		t.put("chunks", new LongArrayTag(ch == null ? new long[0] : ch.toLongArray()));
		ListTag l = new ListTag();
		for (Lieu x : lieux.values()) if (x.dim().equals(dim)) {
			CompoundTag c = new CompoundTag();
			c.putInt("x", x.x()); c.putInt("z", x.z()); c.putString("id", x.id()); c.putString("type", x.type()); c.putInt("jour", x.jour());
			l.add(c);
		}
		t.put("lieux", l);
		ListTag m = new ListTag();
		for (Mort x : morts) if (x.dim().equals(dim)) {
			CompoundTag c = new CompoundTag();
			c.putInt("x", x.x()); c.putInt("z", x.z()); c.putString("nom", x.nom()); c.putInt("jour", x.jour());
			m.add(c);
		}
		t.put("morts", m);
		ListTag f = new ListTag();
		for (FondationRegistre.Fondation x : FondationRegistre.de(p.server).toutes()) {
			if (x.decorative() || !x.dim().toString().equals(dim)) continue;
			CompoundTag c = new CompoundTag();
			c.putInt("x", x.pos().getX()); c.putInt("z", x.pos().getZ()); c.putString("nom", x.nom()); c.putInt("rayon", x.rayon());
			c.putInt("apparence", x.apparence()); c.putInt("ext", x.ext());
			f.add(c);
		}
		t.put("fondations", f);
		return t;
	}

	@Override
	public CompoundTag save(CompoundTag t, HolderLookup.Provider r) {
		CompoundTag p = new CompoundTag();
		parcourus.forEach((d, s) -> p.put(d, new LongArrayTag(s.toLongArray())));
		t.put("parcourus", p);
		ListTag l = new ListTag();
		lieux.forEach((k, x) -> {
			CompoundTag c = new CompoundTag();
			c.putString("cle", k); c.putString("dim", x.dim()); c.putInt("x", x.x()); c.putInt("z", x.z());
			c.putString("id", x.id()); c.putString("type", x.type()); c.putInt("jour", x.jour());
			l.add(c);
		});
		t.put("lieux", l);
		ListTag m = new ListTag();
		for (Mort x : morts) {
			CompoundTag c = new CompoundTag();
			c.putString("dim", x.dim()); c.putInt("x", x.x()); c.putInt("z", x.z()); c.putString("nom", x.nom()); c.putInt("jour", x.jour());
			m.add(c);
		}
		t.put("morts", m);
		return t;
	}

	private static Atlas charger(CompoundTag t, HolderLookup.Provider r) {
		Atlas a = new Atlas();
		CompoundTag p = t.getCompound("parcourus");
		for (String d : p.getAllKeys()) a.parcourus.put(d, new LongOpenHashSet(p.getLongArray(d)));
		for (Tag x : t.getList("lieux", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) x;
			a.lieux.put(c.getString("cle"), new Lieu(c.getString("dim"), c.getInt("x"), c.getInt("z"), c.getString("id"), c.getString("type"), c.getInt("jour")));
		}
		for (Tag x : t.getList("morts", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) x;
			a.morts.add(new Mort(c.getString("dim"), c.getInt("x"), c.getInt("z"), c.getString("nom"), c.getInt("jour")));
		}
		return a;
	}

	static ChunkPos chunk(long l) { return new ChunkPos(l); }
}
