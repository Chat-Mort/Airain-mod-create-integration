package fr.chatmort.airain.trophee;

import java.util.EnumSet;
import java.util.Set;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * Trophées de l'Empire : un trophée posé sur un socle donne son effet à TOUS les joueurs, où qu'ils soient,
 * tant qu'il reste sur son socle. Chaque effet ne compte qu'une fois, même avec plusieurs trophées identiques.
 * Les trophées sont définis par des tags d'objets (airain:trophees/<effet>), que le pack peut compléter.
 */
public final class Trophees {
	public enum Effet {
		FEU("feu", MobEffects.FIRE_RESISTANCE),
		REGENERATION("regeneration", MobEffects.REGENERATION),
		VISION("vision", MobEffects.NIGHT_VISION),
		RESISTANCE("resistance", MobEffects.DAMAGE_RESISTANCE),
		HATE("hate", MobEffects.DIG_SPEED),
		FORCE("force", MobEffects.DAMAGE_BOOST),
		ABSORPTION("absorption", null),     // cœurs dorés qui se reforment (géré à part)
		SATIETE("satiete", MobEffects.SATURATION),
		CHUTE("chute", null);           // pas de dégâts de chute (géré à part)

		public final TagKey<Item> tag;
		public final Holder<MobEffect> effet;

		Effet(String nom, Holder<MobEffect> effet) {
			this.tag = TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("airain", "trophees/" + nom));
			this.effet = effet;
		}
	}

	public static final TagKey<Item> TOUS = TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("airain", "trophees"));
	private static Set<Effet> actifs = EnumSet.noneOf(Effet.class);

	private Trophees() {}

	public static boolean estTrophee(ItemStack pile) {
		return !pile.isEmpty() && pile.is(TOUS);
	}

	public static Set<Effet> effetsDe(ItemStack pile) {
		Set<Effet> s = EnumSet.noneOf(Effet.class);
		for (Effet e : Effet.values())
			if (pile.is(e.tag)) s.add(e);
		return s;
	}

	/** Toutes les 2 secondes : recalcule les effets actifs et les renouvelle sur chaque joueur. */
	public static void tick(ServerTickEvent.Post event) {
		MinecraftServer serveur = event.getServer();
		if (serveur.getTickCount() % 40 != 0)
			return;
		TropheeRegistre reg = TropheeRegistre.de(serveur);
		if (serveur.getTickCount() % 600 == 0)
			reg.nettoyer(serveur);
		Set<Effet> s = EnumSet.noneOf(Effet.class), sac = EnumSet.noneOf(Effet.class);
		for (TropheeRegistre.Entree en : reg.toutes()) {
			Set<Effet> ef = effetsDe(new ItemStack(BuiltInRegistries.ITEM.get(en.objet())));
			s.addAll(ef);
			if (en.sacre()) sac.addAll(ef);
		}
		actifs = s;
		sacres = sac;
		for (ServerPlayer joueur : serveur.getPlayerList().getPlayers()) {
			for (Effet e : s)
				if (e.effet != null)
					joueur.addEffect(new MobEffectInstance(e.effet, 260, sac.contains(e) ? 1 : 0, true, false, true));
			// chute sacrée : insensible au souffle des explosions
			var kb = joueur.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.EXPLOSION_KNOCKBACK_RESISTANCE);
			if (kb != null) {
				boolean veut = sac.contains(Effet.CHUTE);
				if (veut && !kb.hasModifier(SOUFFLE))
					kb.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(SOUFFLE, 1.0,
						net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_VALUE));
				else if (!veut && kb.hasModifier(SOUFFLE)) kb.removeModifier(SOUFFLE);
			}
		}
	}

	/** Trophées posés sur un socle sacré : niveau II, ou un bonus pour les effets sans niveau. */
	private static Set<Effet> sacres = EnumSet.noneOf(Effet.class);
	private static final ResourceLocation SOUFFLE = ResourceLocation.fromNamespaceAndPath("airain", "trophee_souffle");

	/** Feu sacré : les flammes s'éteignent dès la sortie de la lave ; vision sacrée : ni cécité ni obscurité. */
	public static void joueur(net.neoforged.neoforge.event.tick.PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		absorption(p);
		if (sacres.isEmpty()) return;
		if (sacres.contains(Effet.FEU) && p.isOnFire() && !p.isInLava()) p.clearFire();
		if (sacres.contains(Effet.VISION) && p.tickCount % 5 == 0) {
			if (p.hasEffect(net.minecraft.world.effect.MobEffects.BLINDNESS)) p.removeEffect(net.minecraft.world.effect.MobEffects.BLINDNESS);
			if (p.hasEffect(net.minecraft.world.effect.MobEffects.DARKNESS)) p.removeEffect(net.minecraft.world.effect.MobEffects.DARKNESS);
		}
	}

	/** Absorption : jusqu'à 4 cœurs dorés (8 si sacré), un demi-cœur se reforme toutes les 5 s. */
	private static final ResourceLocation BOUCLIER = ResourceLocation.fromNamespaceAndPath("airain", "trophee_absorption");
	private static void absorption(ServerPlayer p) {
		var max = p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_ABSORPTION);
		if (max == null) return;
		boolean actif = actifs.contains(Effet.ABSORPTION);
		double v = actif ? (sacres.contains(Effet.ABSORPTION) ? 16 : 8) : 0;
		var mod = max.getModifier(BOUCLIER);
		if (mod == null || mod.amount() != v) {
			max.removeModifier(BOUCLIER);
			if (v > 0) max.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(BOUCLIER, v,
				net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_VALUE));
		}
		if (actif && p.tickCount % 100 == 0 && p.getAbsorptionAmount() < p.getMaxAbsorption())
			p.setAbsorptionAmount(Math.min(p.getMaxAbsorption(), p.getAbsorptionAmount() + 1f));
	}

	/** Les boss avancés laissent leur trophée à chaque joueur présent (64 blocs), sinon au sol. */
	public static void boss(net.neoforged.neoforge.event.entity.living.LivingDeathEvent e) {
		var mort = e.getEntity();
		if (!(mort.level() instanceof net.minecraft.server.level.ServerLevel sl)) return;
		var item = fr.chatmort.airain.AirainMod.TROPHEES_BOSS.get(BuiltInRegistries.ENTITY_TYPE.getKey(mort.getType()).toString());
		if (item == null) return;
		var joueurs = sl.getEntitiesOfClass(ServerPlayer.class, mort.getBoundingBox().inflate(64), p -> !p.isSpectator());
		if (joueurs.isEmpty()) { mort.spawnAtLocation(new ItemStack(item.get())); return; }
		for (ServerPlayer p : joueurs) {
			ItemStack t = new ItemStack(item.get());
			if (!p.getInventory().add(t)) p.drop(t, false);
			p.sendSystemMessage(net.minecraft.network.chat.Component.translatable("airain.trophee.obtenu", t.getHoverName()).withStyle(net.minecraft.ChatFormatting.GOLD));
		}
	}

	public static void chute(LivingIncomingDamageEvent event) {
		if (event.getEntity() instanceof ServerPlayer && event.getSource().is(DamageTypeTags.IS_FALL) && actifs.contains(Effet.CHUTE))
			event.setCanceled(true);
	}
}
