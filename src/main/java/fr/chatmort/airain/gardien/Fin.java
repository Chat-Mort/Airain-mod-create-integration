package fr.chatmort.airain.gardien;

import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.commands.Commands;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.VanillaGameEvent;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Le choix final : « Rallumer le Cœur » (empire) ou « Libérer les âmes » (echo). Un seul choix par monde.
 * Les quêtes l'enregistrent avec la commande /airain fin empire|echo.
 */
public class Fin extends SavedData {
	public static final TagKey<EntityType<?>> AUTOMATES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("airain", "automates_empire"));
	public static final TagKey<EntityType<?>> AMES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("airain", "ames_sans_repos"));

	private String choix = "";

	public static Fin de(MinecraftServer serveur) {
		return serveur.overworld().getDataStorage().computeIfAbsent(
			new SavedData.Factory<>(Fin::new, Fin::charger, null), "airain_fin");
	}

	public boolean empire() { return choix.equals("empire"); }
	public boolean echo() { return choix.equals("echo"); }

	public static void commandes(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("airain").requires(s -> s.hasPermission(2))
			.then(fr.chatmort.airain.chronique.Chronique.commande())
			.then(Commands.literal("fin")
				.then(Commands.argument("choix", StringArgumentType.word())
					.suggests((c, b) -> { b.suggest("empire"); b.suggest("echo"); b.suggest("aucun"); return b.buildFuture(); })
					.executes(c -> {
						String v = StringArgumentType.getString(c, "choix");
						if (!v.equals("empire") && !v.equals("echo") && !v.equals("aucun")) return 0;
						Fin f = de(c.getSource().getServer());
						if (!f.choix.isEmpty() && !v.equals("aucun") && !f.choix.equals(v)) {
							c.getSource().sendFailure(Component.translatable("airain.fin.deja", Component.translatable("airain.fin." + f.choix)));
							return 0;
						}
						f.choix = v.equals("aucun") ? "" : v;
						f.setDirty();
						if (c.getSource().getEntity() instanceof ServerPlayer p && !v.equals("aucun")) recompenser(p, v);
						else c.getSource().sendSuccess(() -> Component.translatable("airain.fin.enregistre", Component.translatable("airain.fin." + v)), true);
						return 1;
					}))));
	}

	/** Le livre d'épilogue (pages traduites) et, pour l'Empire, la couronne. */
	private static void recompenser(ServerPlayer p, String v) {
		java.util.List<net.minecraft.server.network.Filterable<Component>> pages = new java.util.ArrayList<>();
		for (int i = 1; i <= 5; i++) pages.add(net.minecraft.server.network.Filterable.passThrough(Component.translatable("airain.epilogue." + v + ".p" + i)));
		net.minecraft.world.item.ItemStack livre = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.WRITTEN_BOOK);
		livre.set(net.minecraft.core.component.DataComponents.WRITTEN_BOOK_CONTENT, new net.minecraft.world.item.component.WrittenBookContent(
			net.minecraft.server.network.Filterable.passThrough(v.equals("empire") ? "L'Empire renaissant" : "Le dernier chant"), "Elias Vael", 0, pages, true));
		livre.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.translatable("airain.epilogue." + v + ".titre")
			.withStyle(s -> s.withItalic(false).withColor(net.minecraft.ChatFormatting.GOLD)));
		if (v.equals("empire")) p.getInventory().placeItemBackInInventory(new net.minecraft.world.item.ItemStack(fr.chatmort.airain.AirainMod.COURONNE.get()));
		if (v.equals("echo")) p.getInventory().placeItemBackInInventory(new net.minecraft.world.item.ItemStack(fr.chatmort.airain.AirainMod.DIADEME.get()));
		p.getInventory().placeItemBackInInventory(livre);
		if (v.equals("empire")) {                                              // le testament d'Auguste, glissé avec la couronne
			net.minecraft.world.item.ItemStack t = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.WRITTEN_BOOK);
			t.set(net.minecraft.core.component.DataComponents.WRITTEN_BOOK_CONTENT, new net.minecraft.world.item.component.WrittenBookContent(
				net.minecraft.server.network.Filterable.passThrough("Testament"), "Auguste Ferrand", 0,
				java.util.List.of(net.minecraft.server.network.Filterable.passThrough(Component.translatable("airain.testament.p1")),
					net.minecraft.server.network.Filterable.passThrough(Component.translatable("airain.testament.p2"))), true));
			t.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.translatable("airain.testament.titre")
				.withStyle(s -> s.withItalic(false).withColor(net.minecraft.ChatFormatting.GOLD)));
			net.minecraft.nbt.CompoundTag cd = new net.minecraft.nbt.CompoundTag();
			cd.putString("airain_doc", "testament_ferrand");
			t.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.of(cd));
			p.getInventory().placeItemBackInInventory(t);
		}
		if (v.equals("echo")) {                                                // le mot de Morgana, glissé avec le diadème
			net.minecraft.world.item.ItemStack note = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.WRITTEN_BOOK);
			note.set(net.minecraft.core.component.DataComponents.WRITTEN_BOOK_CONTENT, new net.minecraft.world.item.component.WrittenBookContent(
				net.minecraft.server.network.Filterable.passThrough("Note de Morgana"), "Morgana Dalmont", 0,
				java.util.List.of(net.minecraft.server.network.Filterable.passThrough(Component.translatable("airain.morgana.note.p1"))), true));
			note.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.translatable("airain.morgana.note.titre")
				.withStyle(s -> s.withItalic(false).withColor(net.minecraft.ChatFormatting.LIGHT_PURPLE)));
			net.minecraft.nbt.CompoundTag cd = new net.minecraft.nbt.CompoundTag();
			cd.putString("airain_doc", "morgana_note");
			note.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.of(cd));
			p.getInventory().placeItemBackInInventory(note);
		}
		p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket(Component.translatable("airain.epilogue." + v + ".titre").withStyle(net.minecraft.ChatFormatting.GOLD)));
		p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket(Component.translatable("airain.fin." + v)));
		p.level().playSound(null, p.blockPosition(), v.equals("empire") ? net.minecraft.sounds.SoundEvents.BEACON_ACTIVATE : net.minecraft.sounds.SoundEvents.AMETHYST_BLOCK_RESONATE,
			net.minecraft.sounds.SoundSource.PLAYERS, 1f, v.equals("empire") ? 0.7f : 0.6f);
		fr.chatmort.airain.chronique.Theme.jouer(p.server, fr.chatmort.airain.chronique.Theme.ADA_ELIAS);
		fr.chatmort.airain.chronique.Chronique.premiere(p.server, "fin", "airain.chronique.j.fin_" + v, p.getGameProfile().getName());
		fr.chatmort.airain.chronique.Chronique.de(p.server).debloquer(p.server, "fin_" + v);
		if (v.equals("echo")) p.sendSystemMessage(Component.translatable("airain.fin.benediction").withStyle(net.minecraft.ChatFormatting.DARK_AQUA));
	}

	public static boolean couronne(LivingEntity e) {
		var t = e.getItemBySlot(EquipmentSlot.HEAD);
		return t.getItem() instanceof CouronneItem || fr.chatmort.airain.armure.ArmureItem.casqueImperial(t);   // le casque impérial porte la couronne
	}

	/** Autorité : les automates de l'Empire ne prennent plus le porteur de la couronne pour cible, sauf s'il frappe le premier ou pendant un assaut. */
	public static void cible(LivingChangeTargetEvent e) {
		if (!(e.getNewAboutToBeSetTarget() instanceof Player p) || !couronne(p)) return;
		LivingEntity m = e.getEntity();
		if (!m.getType().is(AUTOMATES) || m.getTags().contains("airain_vague")) return;
		if (m.getLastHurtByMob() == p && fr.chatmort.airain.armure.Armures.ensemble(p) < 2) return;   // l'Empereur est toujours obéi
		e.setCanceled(true);
	}

	private static final java.util.Map<java.util.UUID, Integer> ACCROUPI = new java.util.HashMap<>();
	private static final java.util.Map<java.util.UUID, Long> RECHARGE = new java.util.HashMap<>();
	public static final int SONAR_ATTENTE = 30, SONAR_RECHARGE = 300, SONAR_RAYON = 24, SONAR_DUREE = 120;

	/** Commandement (couronne) toutes les deux secondes ; sonar de l'Écho à chaque tick. */
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		if (p.tickCount % 40 == 0 && couronne(p)) {
			var tete = p.getItemBySlot(EquipmentSlot.HEAD);
			boolean sacree = fr.chatmort.airain.Sacre.sacree(tete) || fr.chatmort.airain.armure.ArmureItem.casqueImperial(tete);   // couronne sacrée : 32 blocs, niveau II
			for (GardienEntity g : p.level().getEntitiesOfClass(GardienEntity.class, new AABB(p.blockPosition()).inflate(sacree ? 32 : 16), g -> !g.enPanne())) {
				g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 80, sacree ? 1 : 0, true, true));
				g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 80, sacree ? 1 : 0, true, true));
			}
			// trône impérial : dans sa base, la couronne commande tous les gardiens
			if (fr.chatmort.airain.pouvoir.Pouvoir.dansBase(p.server, true, p.level().dimension().location(), p.getX(), p.getZ())) {
				var f = fr.chatmort.airain.pouvoir.Pouvoir.de(p.server).base(p.server);
				for (GardienEntity g : p.level().getEntitiesOfClass(GardienEntity.class, new AABB(f.pos()).inflate(f.rayon(), 64, f.rayon()), g -> !g.enPanne())) {
					g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 80, sacree ? 1 : 0, true, true));
					g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 80, sacree ? 1 : 0, true, true));
				}
			}
		}
		if (!de(p.server).echo()) return;
		if (p.tickCount % 40 == 0 && (!p.hasEffect(MobEffects.NIGHT_VISION) || p.getEffect(MobEffects.NIGHT_VISION).getDuration() < 300))
			p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false, true));
		sonar(p);
	}

	/** Sonar : accroupi et immobile une seconde et demie, une onde révèle les créatures proches à travers les murs. */
	private static void sonar(ServerPlayer p) {
		boolean pioche = p.getMainHandItem().getItem() instanceof fr.chatmort.airain.armure.PiocheItem;   // la pioche a son propre écho
		boolean immobile = !pioche && p.isShiftKeyDown() && p.onGround() && p.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4;
		int n = immobile ? ACCROUPI.getOrDefault(p.getUUID(), 0) + 1 : 0;
		ACCROUPI.put(p.getUUID(), n);
		if (n != SONAR_ATTENTE) return;
		long maintenant = p.level().getGameTime();
		if (maintenant < RECHARGE.getOrDefault(p.getUUID(), 0L)) {
			p.displayClientMessage(Component.translatable("airain.fin.sonar_recharge", (RECHARGE.get(p.getUUID()) - maintenant + 19) / 20), true);
			return;
		}
		boolean diademe = fr.chatmort.airain.armure.ArmureItem.diademe(p.getItemBySlot(EquipmentSlot.HEAD));   // le diadème porte l'onde plus loin
		int rayon = diademe ? 40 : SONAR_RAYON;
		RECHARGE.put(p.getUUID(), maintenant + (diademe ? SONAR_RECHARGE / 2 : SONAR_RECHARGE));
		ServerLevel sl = p.serverLevel();
		int nb = 0;
		for (LivingEntity c : sl.getEntitiesOfClass(LivingEntity.class, new AABB(p.blockPosition()).inflate(rayon),
				c -> c != p && !(c instanceof net.minecraft.world.entity.decoration.ArmorStand) && c.distanceToSqr(p) <= rayon * rayon)) {
			c.addEffect(new MobEffectInstance(MobEffects.GLOWING, SONAR_DUREE, 0, true, false));
			nb++;
		}
		sl.playSound(null, p.blockPosition(), net.minecraft.sounds.SoundEvents.SCULK_SHRIEKER_SHRIEK, net.minecraft.sounds.SoundSource.PLAYERS, 0.5f, 1.6f);
		sl.playSound(null, p.blockPosition(), net.minecraft.sounds.SoundEvents.WARDEN_HEARTBEAT, net.minecraft.sounds.SoundSource.PLAYERS, 1f, 1f);
		for (int i = 0; i < 48; i++) {
			double a = i * Math.PI * 2 / 48;
			sl.sendParticles(net.minecraft.core.particles.ParticleTypes.SCULK_SOUL, p.getX(), p.getY() + 0.3, p.getZ(), 0,
				Math.cos(a), 0.02, Math.sin(a), 0.35);
		}
		p.displayClientMessage(Component.translatable("airain.fin.sonar", nb), true);
	}

	/** Moisson d'âmes : l'expérience, ce sont des éclats d'Écho ; après la libération, on en récolte moitié plus. */
	public static void experience(net.neoforged.neoforge.event.entity.player.PlayerXpEvent.XpChange e) {
		if (e.getAmount() <= 0 || !(e.getEntity() instanceof ServerPlayer p) || !de(p.server).echo()) return;
		float v = e.getAmount() * 1.5f * fr.chatmort.airain.pouvoir.Siege.experience(p.server);   // chant des âmes : ×2 en plus (×3)
		int n = (int) v;
		if (p.getRandom().nextFloat() < v - n) n++;
		e.setAmount(n);
	}

	/** Bénédiction : le sculk n'entend plus les joueurs (plus d'appel du Warden). */
	public static void vibration(VanillaGameEvent e) {
		if (e.getCause() instanceof ServerPlayer p && de(p.server).echo()) e.setCanceled(true);
	}

	/** Les âmes sans repos ne reviennent plus une fois libérées. */
	public static void apparition(FinalizeSpawnEvent e) {
		if (e.getSpawnType() != MobSpawnType.NATURAL || !(e.getLevel().getLevel() instanceof ServerLevel sl)) return;
		if (e.getEntity().getType().is(AMES) && de(sl.getServer()).echo()) e.setSpawnCancelled(true);
	}

	@Override
	public CompoundTag save(CompoundTag tag, HolderLookup.Provider registres) {
		tag.putString("choix", choix);
		return tag;
	}

	private static Fin charger(CompoundTag tag, HolderLookup.Provider registres) {
		Fin f = new Fin();
		f.choix = tag.getString("choix");
		return f;
	}
}
