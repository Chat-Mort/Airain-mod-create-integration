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
		Set<Effet> s = EnumSet.noneOf(Effet.class);
		for (ResourceLocation id : reg.objets())
			s.addAll(effetsDe(new ItemStack(BuiltInRegistries.ITEM.get(id))));
		actifs = s;
		for (ServerPlayer joueur : serveur.getPlayerList().getPlayers())
			for (Effet e : s)
				if (e.effet != null)
					joueur.addEffect(new MobEffectInstance(e.effet, 260, 0, true, false, true));
	}

	public static void chute(LivingIncomingDamageEvent event) {
		if (event.getEntity() instanceof ServerPlayer && event.getSource().is(DamageTypeTags.IS_FALL) && actifs.contains(Effet.CHUTE))
			event.setCanceled(true);
	}
}
