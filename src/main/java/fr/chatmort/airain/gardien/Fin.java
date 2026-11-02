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
		for (int i = 1; i <= 4; i++) pages.add(net.minecraft.server.network.Filterable.passThrough(Component.translatable("airain.epilogue." + v + ".p" + i)));
		net.minecraft.world.item.ItemStack livre = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.WRITTEN_BOOK);
		livre.set(net.minecraft.core.component.DataComponents.WRITTEN_BOOK_CONTENT, new net.minecraft.world.item.component.WrittenBookContent(
			net.minecraft.server.network.Filterable.passThrough(v.equals("empire") ? "L'Empire renaissant" : "Le dernier chant"), "Elias Vael", 0, pages, true));
		livre.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.translatable("airain.epilogue." + v + ".titre")
			.withStyle(s -> s.withItalic(false).withColor(net.minecraft.ChatFormatting.GOLD)));
		if (v.equals("empire")) p.getInventory().placeItemBackInInventory(new net.minecraft.world.item.ItemStack(fr.chatmort.airain.AirainMod.COURONNE.get()));
		p.getInventory().placeItemBackInInventory(livre);
		p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket(Component.translatable("airain.epilogue." + v + ".titre").withStyle(net.minecraft.ChatFormatting.GOLD)));
		p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket(Component.translatable("airain.fin." + v)));
		p.level().playSound(null, p.blockPosition(), v.equals("empire") ? net.minecraft.sounds.SoundEvents.BEACON_ACTIVATE : net.minecraft.sounds.SoundEvents.AMETHYST_BLOCK_RESONATE,
			net.minecraft.sounds.SoundSource.PLAYERS, 1f, v.equals("empire") ? 0.7f : 0.6f);
		if (v.equals("echo")) p.sendSystemMessage(Component.translatable("airain.fin.benediction").withStyle(net.minecraft.ChatFormatting.DARK_AQUA));
	}

	static boolean couronne(LivingEntity e) {
		return e.getItemBySlot(EquipmentSlot.HEAD).is(fr.chatmort.airain.AirainMod.COURONNE.get());
	}

	/** Autorité : les automates de l'Empire ne prennent plus le porteur de la couronne pour cible, sauf s'il frappe le premier ou pendant un assaut. */
	public static void cible(LivingChangeTargetEvent e) {
		if (!(e.getNewAboutToBeSetTarget() instanceof Player p) || !couronne(p)) return;
		LivingEntity m = e.getEntity();
		if (!m.getType().is(AUTOMATES) || m.getTags().contains("airain_vague")) return;
		if (m.getLastHurtByMob() == p) return;
		e.setCanceled(true);
	}

	/** Commandement (couronne) et bénédiction de l'Écho, toutes les deux secondes. */
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 40 != 0) return;
		if (couronne(p)) {
			for (GardienEntity g : p.level().getEntitiesOfClass(GardienEntity.class, new AABB(p.blockPosition()).inflate(16), g -> !g.enPanne())) {
				g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 80, 0, true, true));
				g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 80, 0, true, true));
			}
		}
		if (de(p.server).echo()) {
			if (!p.hasEffect(MobEffects.NIGHT_VISION) || p.getEffect(MobEffects.NIGHT_VISION).getDuration() < 300)
				p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false, true));
			p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 80, 0, true, false, true));
		}
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
