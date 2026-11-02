package fr.chatmort.airain.suite;

import java.util.ArrayList;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.fondation.Apparence;
import fr.chatmort.airain.fondation.FondationBlockEntity;
import fr.chatmort.airain.fondation.FondationRegistre;
import fr.chatmort.airain.gardien.Fin;
import fr.chatmort.airain.gardien.GardienEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Après la fin : rebâtir l'Empire (avant-postes rallumés) ou apaiser l'Écho (relais apaisés).
 * Une zone rallumée ou apaisée ne voit plus apparaître de monstres.
 */
public class Suites extends SavedData {
	public record Zone(String dim, int x0, int z0, int x1, int z1, String type, int jour) {
		boolean contient(String d, double x, double z) { return dim.equals(d) && x >= x0 && x <= x1 && z >= z0 && z <= z1; }
		int cx() { return (x0 + x1) / 2; }
		int cz() { return (z0 + z1) / 2; }
	}
	public static final int[] PALIERS = {1, 3, 5, 10};
	static final ResourceLocation DIAPASON = ResourceLocation.fromNamespaceAndPath("kubejs", "diapason_echo");
	static final ResourceLocation FRAGMENT = ResourceLocation.fromNamespaceAndPath("kubejs", "fragment_resonance");
	static final int COUT_FRAGMENTS = 8, RAYON_RELAIS = 64;

	private final List<Zone> zones = new ArrayList<>();

	public static Suites de(MinecraftServer s) {
		return s.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Suites::new, Suites::charger, null), "airain_suites");
	}

	int nombre(String type) { return (int) zones.stream().filter(z -> z.type().equals(type)).count(); }

	static int jour(MinecraftServer s) { return (int) (s.overworld().getDayTime() / 24000L) + 1; }

	/** La structure de ce type où se tient le joueur (null : aucune). */
	static StructureStart structure(ServerPlayer p, java.util.function.Predicate<String> filtre) {
		ServerLevel sl = p.serverLevel();
		var reg = sl.registryAccess().registryOrThrow(Registries.STRUCTURE);
		for (var s : sl.structureManager().getAllStructuresAt(p.blockPosition()).keySet()) {
			ResourceLocation id = reg.getKey(s);
			if (id == null || !filtre.test(id.toString())) continue;
			StructureStart st = sl.structureManager().getStructureAt(p.blockPosition(), s);
			if (st.isValid()) return st;
		}
		return null;
	}

	boolean deja(String dim, int x, int z) { return zones.stream().anyMatch(zo -> zo.contient(dim, x, z)); }

	// ---- Rebâtir : la charte impériale, couronne sur la tête, dans un avant-poste
	public static InteractionResult charte(ServerPlayer p, ItemStack pile) {
		if (!Fin.de(p.server).empire()) { p.displayClientMessage(Component.translatable("airain.suite.pas_empire"), true); return InteractionResult.FAIL; }
		if (!Fin.couronne(p)) { p.displayClientMessage(Component.translatable("airain.suite.couronne"), true); return InteractionResult.FAIL; }
		StructureStart st = structure(p, id -> (id.startsWith("kubejs:avant_poste_") && !id.contains("refractaire")) || id.equals("kubejs:cite_mecanique"));
		if (st == null) { p.displayClientMessage(Component.translatable("airain.suite.hors_poste"), true); return InteractionResult.FAIL; }
		Suites s = de(p.server);
		String dim = p.level().dimension().location().toString();
		BoundingBox bb = st.getBoundingBox();
		if (s.deja(dim, bb.getCenter().getX(), bb.getCenter().getZ())) { p.displayClientMessage(Component.translatable("airain.suite.deja_poste"), true); return InteractionResult.FAIL; }
		s.zones.add(new Zone(dim, bb.minX(), bb.minZ(), bb.maxX(), bb.maxZ(), "poste", jour(p.server)));
		s.setDirty();
		if (!p.getAbilities().instabuild) pile.shrink(1);
		ServerLevel sl = p.serverLevel();
		int bannieres = recolorer(sl, bb, p), comptoirs = remise(sl, bb);
		// un gardien réparé monte la garde au centre
		BlockPos c = sl.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, bb.getCenter());
		GardienEntity g = AirainMod.GARDIEN.get().create(sl);
		if (g != null) {
			g.moveTo(c.getX() + 0.5, c.getY(), c.getZ() + 0.5, 0, 0);
			g.setPlayerCreated(true);
			g.setPersistenceRequired();
			sl.addFreshEntity(g);
		}
		sl.playSound(null, p.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1f, 0.8f);
		sl.playSound(null, p.blockPosition(), SoundEvents.NOTE_BLOCK_DIDGERIDOO.value(), SoundSource.PLAYERS, 1.5f, 1.2f);
		sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, p.getX(), p.getY() + 1, p.getZ(), 40, 3, 2, 3, 0.2);
		p.displayClientMessage(Component.translatable("airain.suite.poste_ok", s.nombre("poste"), bannieres, comptoirs).withStyle(net.minecraft.ChatFormatting.GOLD), false);
		fr.chatmort.airain.chronique.Chronique.noter(p.server, "airain.chronique.j.rallume", p.getGameProfile().getName(), String.valueOf(s.nombre("poste")));
		paliers(p.server);
		return InteractionResult.CONSUME;
	}

	/** Les bannières de l'avant-poste prennent les couleurs de la base la plus proche (taille, forme et usure gardées). */
	static int recolorer(ServerLevel sl, BoundingBox bb, ServerPlayer p) {
		FondationRegistre.Fondation base = null;
		for (FondationRegistre.Fondation f : FondationRegistre.de(sl.getServer()).toutes())
			if (!f.decorative() && (base == null || f.distance(p.getX(), p.getZ()) < base.distance(p.getX(), p.getZ()))) base = f;
		if (base == null) return 0;
		int[] couleurs = Apparence.unpack(base.apparence(), base.ext()).valeurs();
		int n = 0;
		for (int cx = bb.minX() >> 4; cx <= bb.maxX() >> 4; cx++)
			for (int cz = bb.minZ() >> 4; cz <= bb.maxZ() >> 4; cz++) {
				if (!sl.hasChunk(cx, cz)) continue;
				for (var be : sl.getChunk(cx, cz).getBlockEntities().values())
					if (be instanceof FondationBlockEntity f) {
						int[] v = f.apparence().valeurs();
						for (int k : new int[] {1, 2, 3, 13, 14, 15}) v[k] = couleurs[k];
						f.configurer(f.nom(), f.devise(), Apparence.depuis(v));
						n++;
					}
			}
		return n;
	}

	/** Les distributeurs de l'avant-poste baissent leurs prix d'un quart. */
	static int remise(ServerLevel sl, BoundingBox bb) {
		String[] pieces = {"spur", "bevel", "sprocket", "cog", "crown", "sun"};
		int[] valeurs = {1, 8, 16, 64, 512, 4096};
		int n = 0;
		for (int cx = bb.minX() >> 4; cx <= bb.maxX() >> 4; cx++)
			for (int cz = bb.minZ() >> 4; cz <= bb.maxZ() >> 4; cz++) {
				if (!sl.hasChunk(cx, cz)) continue;
				for (var be : new ArrayList<>(sl.getChunk(cx, cz).getBlockEntities().values())) {
					ResourceLocation id = BuiltInRegistries.BLOCK_ENTITY_TYPE.getKey(be.getType());
					if (id == null || !id.getNamespace().equals("numismatics") || !id.getPath().contains("vendor")) continue;
					CompoundTag t = be.saveCustomOnly(sl.registryAccess());
					if (!t.contains("Prices")) continue;
					CompoundTag pr = t.getCompound("Prices");
					int total = 0;
					for (int k = 0; k < pieces.length; k++) total += pr.getInt(pieces[k]) * valeurs[k];
					if (total <= 1) continue;
					int reste = Math.max(1, Math.round(total * 0.75f));
					for (int k = pieces.length - 1; k >= 0; k--) { pr.putInt(pieces[k], reste / valeurs[k]); reste %= valeurs[k]; }
					t.put("Prices", pr);
					be.loadCustomOnly(t, sl.registryAccess());
					be.setChanged();
					sl.sendBlockUpdated(be.getBlockPos(), be.getBlockState(), be.getBlockState(), 3);
					n++;
				}
			}
		return n;
	}

	// ---- Apaiser : accroupi, clic droit avec le diapason dans un relais brisé (8 fragments de résonance)
	public static void diapason(PlayerInteractEvent.RightClickItem e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || !p.isShiftKeyDown()) return;
		if (!BuiltInRegistries.ITEM.getKey(e.getItemStack().getItem()).equals(DIAPASON)) return;
		if (!Fin.de(p.server).echo()) return;
		StructureStart st = structure(p, id -> id.equals("kubejs:relais_brise") || id.equals("kubejs:grand_relais"));
		if (st == null) return;
		e.setCanceled(true);
		e.setCancellationResult(InteractionResult.CONSUME);
		Suites s = de(p.server);
		String dim = p.level().dimension().location().toString();
		BlockPos c = st.getBoundingBox().getCenter();
		if (s.deja(dim, c.getX(), c.getZ())) { p.displayClientMessage(Component.translatable("airain.suite.deja_relais"), true); return; }
		var frag = BuiltInRegistries.ITEM.get(FRAGMENT);
		if (!p.getAbilities().instabuild) {
			if (p.getInventory().countItem(frag) < COUT_FRAGMENTS) {
				p.displayClientMessage(Component.translatable("airain.suite.fragments", COUT_FRAGMENTS), true);
				return;
			}
			p.getInventory().clearOrCountMatchingItems(x -> x.is(frag), COUT_FRAGMENTS, p.inventoryMenu.getCraftSlots());
		}
		s.zones.add(new Zone(dim, c.getX() - RAYON_RELAIS, c.getZ() - RAYON_RELAIS, c.getX() + RAYON_RELAIS, c.getZ() + RAYON_RELAIS, "relais", jour(p.server)));
		s.setDirty();
		ServerLevel sl = p.serverLevel();
		sl.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 2f, 0.5f);
		sl.playSound(null, p.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1f, 1.6f);
		sl.sendParticles(ParticleTypes.SCULK_SOUL, p.getX(), p.getY() + 1, p.getZ(), 60, 4, 3, 4, 0.05);
		p.displayClientMessage(Component.translatable("airain.suite.relais_ok", s.nombre("relais")).withStyle(net.minecraft.ChatFormatting.DARK_AQUA), false);
		fr.chatmort.airain.chronique.Chronique.noter(p.server, "airain.chronique.j.apaise", p.getGameProfile().getName(), String.valueOf(s.nombre("relais")));
		paliers(p.server);
	}

	// ---- effets des zones
	public static void apparition(FinalizeSpawnEvent e) {
		if (e.getSpawnType() != MobSpawnType.NATURAL || !(e.getEntity() instanceof Enemy)) return;
		if (!(e.getLevel().getLevel() instanceof ServerLevel sl)) return;
		Suites s = de(sl.getServer());
		if (s.zones.isEmpty()) return;
		String dim = sl.dimension().location().toString();
		if (s.zones.stream().anyMatch(z -> z.contient(dim, e.getX(), e.getZ()))) e.setSpawnCancelled(true);
	}

	/** Un peu d'Écho apaisé qui flotte autour des relais, quand un joueur est près. */
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 30 != 3) return;
		Suites s = de(p.server);
		String dim = p.level().dimension().location().toString();
		for (Zone z : s.zones)
			if (z.type().equals("relais") && z.dim().equals(dim) && Math.abs(p.getX() - z.cx()) < 48 && Math.abs(p.getZ() - z.cz()) < 48)
				p.serverLevel().sendParticles(p, ParticleTypes.END_ROD, true, p.getX(), p.getY() + 2, p.getZ(), 6, 6, 3, 6, 0.01);
	}

	/** Les étapes de quête (KubeJS stages) selon le nombre de zones, pour tous les joueurs. */
	static void paliers(MinecraftServer srv) {
		Suites s = de(srv);
		for (ServerPlayer p : srv.getPlayerList().getPlayers()) donner(srv, p, s);
	}

	static void donner(MinecraftServer srv, ServerPlayer p, Suites s) {
		var src = srv.createCommandSourceStack().withSuppressedOutput().withPermission(4);
		for (String type : new String[] {"poste", "relais"})
			for (int pal : PALIERS)
				if (s.nombre(type) >= pal)
					srv.getCommands().performPrefixedCommand(src, "kubejs stages add " + p.getGameProfile().getName() + " airain_" + type + "_" + pal);
	}

	public static void connexion(PlayerEvent.PlayerLoggedInEvent e) {
		if (e.getEntity() instanceof ServerPlayer p) donner(p.server, p, de(p.server));
	}

	@Override
	public CompoundTag save(CompoundTag t, HolderLookup.Provider r) {
		ListTag l = new ListTag();
		for (Zone z : zones) {
			CompoundTag c = new CompoundTag();
			c.putString("dim", z.dim()); c.putInt("x0", z.x0()); c.putInt("z0", z.z0()); c.putInt("x1", z.x1()); c.putInt("z1", z.z1());
			c.putString("type", z.type()); c.putInt("jour", z.jour());
			l.add(c);
		}
		t.put("zones", l);
		return t;
	}

	private static Suites charger(CompoundTag t, HolderLookup.Provider r) {
		Suites s = new Suites();
		for (Tag x : t.getList("zones", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) x;
			s.zones.add(new Zone(c.getString("dim"), c.getInt("x0"), c.getInt("z0"), c.getInt("x1"), c.getInt("z1"), c.getString("type"), c.getInt("jour")));
		}
		return s;
	}
}
