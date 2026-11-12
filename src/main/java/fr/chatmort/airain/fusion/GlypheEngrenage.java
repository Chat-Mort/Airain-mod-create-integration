package fr.chatmort.airain.fusion;

import com.hollingsworth.arsnouveau.api.spell.*;
import com.hollingsworth.arsnouveau.api.util.SpellUtil;
import com.hollingsworth.arsnouveau.common.spell.augment.*;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import fr.chatmort.airain.gardien.GardienEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.neoforged.neoforge.event.tick.LevelTickEvent;
import org.jetbrains.annotations.NotNull;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

// Glyphe de l'engrenage : le pont entre la magie d'Ars et les machines de Create.
// - sur une machine de Create : elle tourne plus vite quelques secondes (des ticks en plus) ;
// - sur un automate (tag airain:automatons) : ses rouages se grippent ;
// - sur un gardien d'airain : il est huilé (soin).
public class GlypheEngrenage extends AbstractEffect {
	public static final GlypheEngrenage INSTANCE = new GlypheEngrenage();
	public static final TagKey<EntityType<?>> AUTOMATES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("airain", "automatons"));

	// Machines accélérées : position → [ticks restants, ticks en plus par tick]
	private static final Map<GlobalPos, int[]> ACCELEREES = new HashMap<>();

	private GlypheEngrenage() { super(ResourceLocation.fromNamespaceAndPath("airain", "glyph_gear"), "Gear"); }

	@Override
	public void onResolveBlock(BlockHitResult hit, Level level, @NotNull LivingEntity lanceur, SpellStats stats, SpellContext ctx, SpellResolver res) {
		// Durée : 5 s, +3 s par prolongation. Vitesse : 1 tick en plus, +1 par amplification (4 au plus).
		int duree = (int) (100 + 60 * stats.getDurationMultiplier());
		int bonus = (int) Math.max(1, Math.min(4, 1 + stats.getAmpMultiplier()));
		for (BlockPos p : SpellUtil.calcAOEBlocks(lanceur, hit.getBlockPos(), hit, stats.getAoeMultiplier())) {
			if (!(level.getBlockEntity(p) instanceof KineticBlockEntity)) continue;
			ACCELEREES.put(GlobalPos.of(level.dimension(), p.immutable()), new int[]{duree, bonus});
			if (level instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, p.getX() + .5, p.getY() + .5, p.getZ() + .5, 12, .4, .4, .4, .05);
		}
	}

	@Override
	public void onResolveEntity(EntityHitResult hit, Level level, @NotNull LivingEntity lanceur, SpellStats stats, SpellContext ctx, SpellResolver res) {
		if (!(hit.getEntity() instanceof LivingEntity cible)) return;
		int duree = (int) (100 + 60 * stats.getDurationMultiplier());
		if (cible instanceof GardienEntity g) {   // un gardien : coup d'huile magique
			g.heal(6 + 3 * (float) stats.getAmpMultiplier());
			if (level instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.HAPPY_VILLAGER, g.getX(), g.getY() + 1.5, g.getZ(), 8, .4, .5, .4, 0);
			return;
		}
		if (!cible.getType().is(AUTOMATES)) return;
		// Les grands automates (boss) résistent : moitié moins longtemps, grippage plus léger.
		boolean boss = cible.getMaxHealth() > 150;
		int t = boss ? duree / 2 : duree;
		int amp = (int) Math.max(0, stats.getAmpMultiplier());
		cible.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, t, boss ? 1 + amp : 5 + amp));
		cible.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, t, boss ? 0 : 1));
		cible.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, t, boss ? 1 : 3));
		if (!boss && cible instanceof Mob m) m.setTarget(null);   // il perd sa cible le temps de se dégripper
		if (level instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.LARGE_SMOKE, cible.getX(), cible.getY() + cible.getBbHeight() * .7, cible.getZ(), 10, .3, .3, .3, .01);
	}

	// Chaque tick du monde : les machines accélérées reçoivent leurs ticks en plus.
	@SuppressWarnings({"unchecked", "rawtypes"})
	public static void tickMonde(LevelTickEvent.Post e) {
		if (!(e.getLevel() instanceof ServerLevel sl) || ACCELEREES.isEmpty()) return;
		Iterator<Map.Entry<GlobalPos, int[]>> it = ACCELEREES.entrySet().iterator();
		while (it.hasNext()) {
			var en = it.next();
			if (!en.getKey().dimension().equals(sl.dimension())) continue;
			BlockPos p = en.getKey().pos();
			int[] v = en.getValue();
			BlockEntity be = sl.isLoaded(p) ? sl.getBlockEntity(p) : null;
			if (!(be instanceof KineticBlockEntity) || --v[0] <= 0) { it.remove(); continue; }
			BlockEntityTicker tk = be.getBlockState().getTicker(sl, (net.minecraft.world.level.block.entity.BlockEntityType) be.getType());
			if (tk == null) continue;
			for (int i = 0; i < v[1]; i++) tk.tick(sl, p, be.getBlockState(), be);
			if (v[0] % 10 == 0) sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, p.getX() + .5, p.getY() + .9, p.getZ() + .5, 2, .3, .2, .3, .02);
		}
	}

	@Override public int getDefaultManaCost() { return 40; }
	@Override public SpellTier defaultTier() { return SpellTier.TWO; }

	@Override public @NotNull Set<AbstractAugment> getCompatibleAugments() {
		return augmentSetOf(AugmentAmplify.INSTANCE, AugmentExtendTime.INSTANCE, AugmentDurationDown.INSTANCE, AugmentAOE.INSTANCE);
	}

	@Override public void addAugmentDescriptions(Map<AbstractAugment, String> map) {
		super.addAugmentDescriptions(map);
		map.put(AugmentAmplify.INSTANCE, "Machines: one more extra tick per tick (up to 4). Automatons: stronger jam.");
		map.put(AugmentExtendTime.INSTANCE, "Lasts 3 more seconds.");
		map.put(AugmentDurationDown.INSTANCE, "Lasts 3 fewer seconds.");
		map.put(AugmentAOE.INSTANCE, "Speeds up the machines around the target.");
	}

	@Override public String getBookDescription() {
		return "Speeds up a Create machine for a few seconds. Jams the gears of automatons and oils brass guardians.";
	}

	@Override public @NotNull Set<SpellSchool> getSchools() { return setOf(SpellSchools.MANIPULATION); }
}
