package fr.chatmort.airain.gardien;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import fr.chatmort.airain.fondation.FondationBlock;
import fr.chatmort.airain.fondation.FondationRegistre;
import fr.chatmort.airain.fondation.GrandEtendardBlock;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

/** Les gardiens rattachés à chaque fondation (quatre au plus), et le rattachement par l'étendard. */
public class Gardiens extends SavedData {
	public static final int LIMITE = 4;
	private static final ResourceLocation EMPIRE_PV = ResourceLocation.fromNamespaceAndPath("airain", "gardien_empire_pv");
	private static final ResourceLocation EMPIRE_FORCE = ResourceLocation.fromNamespaceAndPath("airain", "gardien_empire_force");

	private final Map<String, Set<UUID>> parBase = new HashMap<>();

	public static Gardiens de(MinecraftServer serveur) {
		return serveur.overworld().getDataStorage().computeIfAbsent(
			new SavedData.Factory<>(Gardiens::new, Gardiens::charger, null), "airain_gardiens");
	}

	public int nombre(String cle) {
		Set<UUID> s = parBase.get(cle);
		return s == null ? 0 : s.size();
	}

	public boolean lier(String cle, UUID g) {
		Set<UUID> s = parBase.computeIfAbsent(cle, k -> new HashSet<>());
		if (s.contains(g)) return true;
		if (s.size() >= LIMITE) return false;
		s.add(g); setDirty();
		return true;
	}

	public void liberer(String cle, UUID g) {
		Set<UUID> s = parBase.get(cle);
		if (s != null && s.remove(g)) {
			if (s.isEmpty()) parBase.remove(cle);
			setDirty();
		}
	}

	/** Après le choix « Rallumer le Cœur », les gardiens réparés sont plus robustes et frappent plus fort. */
	public static void renforcer(GardienEntity g) {
		if (!(g.level() instanceof ServerLevel sl) || g.enPanne()) return;
		if (!Fin.de(sl.getServer()).empire()) return;
		var pv = g.getAttribute(Attributes.MAX_HEALTH);
		if (pv != null && !pv.hasModifier(EMPIRE_PV))
			pv.addPermanentModifier(new AttributeModifier(EMPIRE_PV, 50, AttributeModifier.Operation.ADD_VALUE));
		var force = g.getAttribute(Attributes.ATTACK_DAMAGE);
		if (force != null && !force.hasModifier(EMPIRE_FORCE))
			force.addPermanentModifier(new AttributeModifier(EMPIRE_FORCE, 0.5, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
	}

	/** Clé de Create sur un étendard : les gardiens en escorte du joueur s'y rattachent. */
	public static void etendard(PlayerInteractEvent.RightClickBlock e) {
		if (!GardienEntity.estCle(e.getItemStack())) return;
		Block b = e.getLevel().getBlockState(e.getPos()).getBlock();
		if (!(b instanceof FondationBlock) && !(b instanceof GrandEtendardBlock)) return;
		var joueur = e.getEntity();
		var proches = e.getLevel().getEntitiesOfClass(GardienEntity.class, new AABB(joueur.blockPosition()).inflate(32),
			g -> !g.enPanne() && g.escorte(joueur));
		if (proches.isEmpty()) return;
		e.setCanceled(true);
		e.setCancellationResult(InteractionResult.SUCCESS);
		if (!(e.getLevel() instanceof ServerLevel sl)) return;
		FondationRegistre.Fondation f = FondationRegistre.de(sl.getServer()).zone(sl.dimension().location(), e.getPos().getX() + 0.5, e.getPos().getZ() + 0.5);
		if (f == null) {
			joueur.displayClientMessage(Component.translatable("airain.gardien.pas_de_base"), true);
			return;
		}
		int ok = 0, refus = 0;
		for (GardienEntity g : proches) if (g.affecter(f)) ok++; else refus++;
		String cle = FondationRegistre.cle(f.dim(), f.pos());
		sl.playSound(null, e.getPos(), SoundEvents.IRON_GOLEM_REPAIR, SoundSource.NEUTRAL, 1f, 1.2f);
		joueur.displayClientMessage(refus == 0
			? Component.translatable("airain.gardien.affectes", ok, GardienEntity.nom(f), de(sl.getServer()).nombre(cle), LIMITE)
			: Component.translatable("airain.gardien.affectes_plein", ok, GardienEntity.nom(f), refus, LIMITE), true);
	}

	@Override
	public CompoundTag save(CompoundTag tag, HolderLookup.Provider registres) {
		ListTag l = new ListTag();
		parBase.forEach((cle, s) -> {
			CompoundTag c = new CompoundTag();
			c.putString("base", cle);
			ListTag u = new ListTag();
			for (UUID id : s) u.add(NbtUtils.createUUID(id));
			c.put("gardiens", u);
			l.add(c);
		});
		tag.put("bases", l);
		return tag;
	}

	private static Gardiens charger(CompoundTag tag, HolderLookup.Provider registres) {
		Gardiens g = new Gardiens();
		for (Tag t : tag.getList("bases", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) t;
			Set<UUID> s = new HashSet<>();
			for (Tag u : c.getList("gardiens", Tag.TAG_INT_ARRAY)) s.add(NbtUtils.loadUUID(u));
			g.parBase.put(c.getString("base"), s);
		}
		return g;
	}
}
