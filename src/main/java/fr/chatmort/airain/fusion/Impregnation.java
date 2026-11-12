package fr.chatmort.airain.fusion;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.jetbrains.annotations.Nullable;

import com.simibubi.create.content.kinetics.fan.processing.FanProcessingType;

import fr.chatmort.airain.AirainMod;
import net.createmod.catnip.theme.Color;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * La brume d'Écho : traitement au ventilateur de Create à travers un diffuseur d'Écho allumé.
 * Les recettes (objet → résultat, chance par objet) sont dans {@link #RECETTES}. Une créature prise dans le souffle luit.
 */
public class Impregnation implements FanProcessingType {
	/** Recette : résultat et chance d'obtenir le résultat pour chaque objet traité (1 = toujours). */
	private record Recette(String resultat, int nombre, float chance) {}

	private static final Map<String, Recette> RECETTES = new LinkedHashMap<>();
	static {
		RECETTES.put("minecraft:amethyst_shard", new Recette("ars_nouveau:source_gem", 1, 1f));          // comme la chambre d'imprégnation
		RECETTES.put("minecraft:lapis_lazuli", new Recette("ars_nouveau:source_gem", 1, 1f));
		RECETTES.put("minecraft:amethyst_block", new Recette("ars_nouveau:source_gem_block", 1, 1f));
		RECETTES.put("minecraft:sculk", new Recette("minecraft:echo_shard", 1, 0.25f));                  // un éclat pour quatre sculks en moyenne
	}

	private static String id(ItemStack s) { return BuiltInRegistries.ITEM.getKey(s.getItem()).toString(); }
	private static Item objet(String id) { return BuiltInRegistries.ITEM.get(ResourceLocation.parse(id)); }

	@Override
	public boolean isValidAt(Level level, BlockPos pos) {
		var s = level.getBlockState(pos);
		return s.is(AirainMod.DIFFUSEUR_ECHO.get()) && s.getValue(DiffuseurEchoBlock.ALLUME);
	}

	@Override
	public int getPriority() { return 350; }   // avant la hantise (300) si les deux se croisent

	@Override
	public boolean canProcess(ItemStack stack, Level level) { return RECETTES.containsKey(id(stack)); }

	@Override
	@Nullable
	public List<ItemStack> process(ItemStack stack, Level level) {
		Recette r = RECETTES.get(id(stack));
		if (r == null) return null;
		int n = 0;
		for (int i = 0; i < stack.getCount(); i++) if (r.chance() >= 1 || level.random.nextFloat() < r.chance()) n += r.nombre();
		List<ItemStack> sortie = new ArrayList<>();
		Item it = objet(r.resultat());
		while (n > 0) { int k = Math.min(n, it.getDefaultMaxStackSize()); sortie.add(new ItemStack(it, k)); n -= k; }
		return sortie;
	}

	@Override
	public void spawnProcessingParticles(Level level, Vec3 pos) {
		if (level.random.nextInt(6) == 0) level.addParticle(ParticleTypes.WITCH, pos.x, pos.y + .45f, pos.z, 0, 0, 0);
	}

	@Override
	public void morphAirFlow(AirFlowParticleAccess a, RandomSource random) {
		a.setColor(Color.mixColors(0x6A2FB0, 0xC9A6FF, random.nextFloat()));
		a.setAlpha(0.9f);
		if (random.nextFloat() < 1 / 64f) a.spawnExtraParticle(ParticleTypes.WITCH, .125f);
	}

	@Override
	public void affectEntity(Entity e, Level level) {
		if (!level.isClientSide && e instanceof LivingEntity l) l.addEffect(new MobEffectInstance(MobEffects.GLOWING, 60, 0, false, false));
	}
}
