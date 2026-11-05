package fr.chatmort.airain.fondation;

import java.util.List;

import fr.chatmort.airain.borne.Catalogue;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Améliorations de capitale (après la fin) : on pose des plans sur l'étendard de la capitale et l'on paie en pièces.
 * Chaque plan monte d'un niveau. Niveaux rangés sur 2 bits chacun dans un entier.
 */
public final class Ameliorations {
	private Ameliorations() {}

	public static final int SOLEIL = 4096;

	public enum Type {
		/** Zone 192 → 224 / 256 / 320 blocs, gardiens 6 → 7 / 8 / 9. */
		AGRANDISSEMENT("expansion", new int[] {4, 8, 16}),
		/** Régénération dans la zone (I puis II, qui chasse aussi poison et flétrissure), soin des gardiens. */
		INFIRMERIE("infirmary", new int[] {3, 8}),
		/** S'accroupir et frapper l'étendard à main nue : beau temps ou pluie (I), orage aussi et attente réduite (II). */
		METEO("weather_station", new int[] {2, 6}),
		/** Répare l'équipement porté (I), plus vite et aussi la barre d'action (II). */
		FORGE("garrison_forge", new int[] {3, 8});

		public final String id;
		/** Prix de chaque niveau, en soleils. */
		public final int[] prix;
		Type(String id, int[] prix) { this.id = id; this.prix = prix; }
		public int max() { return prix.length; }
		public int de(int pack) { return (pack >> (ordinal() * 2)) & 3; }
		public int avec(int pack, int n) { return (pack & ~(3 << (ordinal() * 2))) | (Math.min(3, n) << (ordinal() * 2)); }
		public Component nom() { return Component.translatable("airain.amelioration." + id); }
	}

	public static final int[] RAYONS = {FondationBlockEntity.RAYON_MAX_SACREE, 224, 256, 320};

	public static boolean capitale(FondationBlockEntity f) { return f.arcanique() || f.imperiale(); }
	public static boolean capitale(FondationRegistre.Fondation f) { return f != null && (f.arcanique() || f.imperiale()); }

	/** Poser un plan sur l'étendard d'une capitale. */
	public static void installer(Level level, BlockPos b, FondationBlockEntity f, Player joueur, ItemStack pile, Type t) {
		if (!(level instanceof ServerLevel sl)) return;
		if (!capitale(f)) { joueur.displayClientMessage(Component.translatable("airain.amelioration.capitale").withStyle(ChatFormatting.RED), true); return; }
		int n = f.niveau(t);
		if (n >= t.max()) { joueur.displayClientMessage(Component.translatable("airain.amelioration.max", t.nom()).withStyle(ChatFormatting.GOLD), true); return; }
		int soleils = t.prix[n];
		if (!joueur.getAbilities().instabuild && !Catalogue.payer(joueur, (long) soleils * SOLEIL)) {
			joueur.displayClientMessage(Component.translatable("airain.amelioration.prix", soleils, t.nom(), n + 1).withStyle(ChatFormatting.RED), true);
			return;
		}
		if (!joueur.getAbilities().instabuild) pile.shrink(1);
		f.ameliorer(t);
		boolean arcane = f.arcanique();
		level.playSound(null, b, arcane ? SoundEvents.AMETHYST_BLOCK_RESONATE : SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 1f, 0.8f);
		level.playSound(null, b, SoundEvents.PLAYER_LEVELUP, SoundSource.BLOCKS, 0.7f, 0.7f);
		sl.sendParticles(arcane ? ParticleTypes.WITCH : ParticleTypes.WAX_OFF, b.getX() + 0.5, b.getY() + 1.5, b.getZ() + 0.5, 40, 0.5, 0.8, 0.5, 0.05);
		joueur.displayClientMessage(Component.translatable("airain.amelioration.installee", t.nom(), f.niveau(t)).withStyle(arcane ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.GOLD), false);
		if (t == Type.AGRANDISSEMENT)
			joueur.displayClientMessage(Component.translatable("airain.amelioration.agrandie", f.rayonMax(), 6 + f.niveau(t)).withStyle(ChatFormatting.GRAY), false);
	}

	/** Station météo : s'accroupir et utiliser l'étendard à main nue. */
	public static void meteo(Level level, BlockPos b, FondationBlockEntity f, Player joueur) {
		if (!(level instanceof ServerLevel sl)) return;
		int n = f.niveau(Type.METEO);
		if (level.dimension() != Level.OVERWORLD || !level.dimensionType().hasSkyLight()) {
			joueur.displayClientMessage(Component.translatable("airain.meteo.ciel"), true); return;
		}
		long reste = f.meteoPret() - level.getGameTime();
		if (reste > 0 && !joueur.getAbilities().instabuild) {
			joueur.displayClientMessage(Component.translatable("airain.meteo.attente", (reste + 1199) / 1200), true); return;
		}
		int etat;   // 0 beau, 1 pluie, 2 orage
		if (sl.isThundering()) etat = 0;
		else if (sl.isRaining()) etat = n >= 2 ? 2 : 0;
		else etat = 1;
		switch (etat) {
			case 0 -> sl.setWeatherParameters(24000, 0, false, false);
			case 1 -> sl.setWeatherParameters(0, 12000, true, false);
			default -> sl.setWeatherParameters(0, 6000, true, true);
		}
		f.meteoPret(level.getGameTime() + (n >= 2 ? 6000 : 24000));
		level.playSound(null, b, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 0.8f, etat == 0 ? 1.4f : 0.7f);
		sl.sendParticles(ParticleTypes.CLOUD, b.getX() + 0.5, b.getY() + 2.5, b.getZ() + 0.5, 30, 0.6, 0.6, 0.6, 0.02);
		for (ServerPlayer p : sl.players())
			p.displayClientMessage(Component.translatable("airain.meteo." + etat), true);
	}

	/** Toutes les 5 s, pour chaque joueur dans une capitale améliorée : infirmerie et forge. */
	public static void effets(ServerPlayer p, FondationRegistre.Fondation f) {
		if (!capitale(f) || f.amelio() == 0) return;
		int inf = Type.INFIRMERIE.de(f.amelio()), forge = Type.FORGE.de(f.amelio());
		if (inf > 0) {
			p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 130, inf - 1, true, false, true));
			if (inf >= 2) { p.removeEffect(MobEffects.POISON); p.removeEffect(MobEffects.WITHER); }
			List<fr.chatmort.airain.gardien.GardienEntity> g = p.level().getEntitiesOfClass(fr.chatmort.airain.gardien.GardienEntity.class, p.getBoundingBox().inflate(32));
			for (var e : g) if (e.getHealth() < e.getMaxHealth() && f.contient(f.dim(), e.getX(), e.getZ())) e.heal(inf * 4f);
		}
		if (forge > 0) {
			int pts = forge >= 2 ? 3 : 1;
			for (EquipmentSlot s : EquipmentSlot.values()) {
				if (s == EquipmentSlot.BODY) continue;
				reparer(p.getItemBySlot(s), pts);
			}
			if (forge >= 2) for (int i = 0; i < 9; i++) if (i != p.getInventory().selected) reparer(p.getInventory().getItem(i), pts);
		}
	}

	private static void reparer(ItemStack s, int pts) {
		if (!s.isEmpty() && s.isDamageableItem() && s.isDamaged()) s.setDamageValue(Math.max(0, s.getDamageValue() - pts));
	}
}
