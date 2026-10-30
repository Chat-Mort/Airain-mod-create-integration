package fr.chatmort.airain.codex;

import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Codex de l'Empire : une page par créature, rangées par force. Les victoires de chaque joueur sont gardées dans ses
 * données persistantes (elles survivent à la mort). Première victoire : la page s'ouvre ; dix : la note d'ingénieur ;
 * un boss se dévoile entièrement dès la première. Une force complète rapporte son emblème (un tableau).
 */
public final class Codex {
	public enum Force { EMPIRE, ECHO, REFRACTAIRES }
	public record Entree(String id, Force force, String dim, boolean boss) {
		public String cle() { return id.replace(':', '.'); }
	}
	public static final List<Entree> ENTREES = new ArrayList<>();
	private static void e(Force f, String dim, boolean boss, String... ids) { for (String i : ids) ENTREES.add(new Entree(i, f, dim, boss)); }
	static {
		e(Force.EMPIRE, "overworld", false, "minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:skeleton", "minecraft:stray",
			"minecraft:bogged", "minecraft:creeper", "minecraft:spider", "minecraft:cave_spider", "minecraft:silverfish", "minecraft:slime",
			"minecraft:guardian", "mebahelcreaturesdwarven:dwarven_spider", "mebahelcreaturesdwarven:dwarven_sphere",
			"mebahelcreaturesdwarven:dwarven_spider_guardian", "mebahelcreaturesdwarven:dwarven_centurion", "cataclysm:the_watcher");
		e(Force.EMPIRE, "overworld", true, "minecraft:breeze", "minecraft:elder_guardian", "mowziesmobs:ferrous_wroughtnaut",
			"cataclysm:the_prowler", "cataclysm:the_harbinger");
		e(Force.EMPIRE, "the_nether", false, "minecraft:wither_skeleton", "minecraft:blaze", "minecraft:magma_cube", "minecraft:hoglin", "minecraft:zoglin");
		e(Force.EMPIRE, "the_nether", true, "cataclysm:netherite_monstrosity", "minecraft:wither");
		e(Force.ECHO, "the_nether", false, "minecraft:piglin", "minecraft:piglin_brute", "minecraft:zombified_piglin", "minecraft:ghast");
		e(Force.ECHO, "overworld", false, "minecraft:phantom", "minecraft:enderman");
		e(Force.ECHO, "overworld", true, "minecraft:warden", "ars_nouveau:wilden_boss");
		e(Force.ECHO, "the_end", false, "minecraft:endermite", "cataclysm:ender_golem");
		e(Force.ECHO, "the_end", true, "cataclysm:ender_guardian");
		e(Force.REFRACTAIRES, "the_end", false, "minecraft:shulker");
		e(Force.REFRACTAIRES, "the_end", true, "minecraft:ender_dragon");
	}

	private Codex() {}

	public static Entree de(String id) {
		for (Entree e : ENTREES) if (e.id.equals(id)) return e;
		return null;
	}

	/** Données du joueur : {victoires:{id:n}, jours:{id:j}, emblemes:{force:1b}}. */
	public static CompoundTag donnees(Player p) {
		CompoundTag pers = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
		CompoundTag c = pers.getCompound("airain_codex");
		pers.put("airain_codex", c);
		p.getPersistentData().put(Player.PERSISTED_NBT_TAG, pers);
		return c;
	}

	public static void mort(LivingDeathEvent ev) {
		if (!(ev.getSource().getEntity() instanceof ServerPlayer p)) return;
		String id = BuiltInRegistries.ENTITY_TYPE.getKey(ev.getEntity().getType()).toString();
		Entree e = de(id);
		if (e == null) return;
		CompoundTag c = donnees(p);
		CompoundTag v = c.getCompound("victoires"), j = c.getCompound("jours");
		int n = v.getInt(id) + 1;
		v.putInt(id, n);
		if (!j.contains(id)) j.putInt(id, (int) (p.level().getDayTime() / 24000L) + 1);
		c.put("victoires", v); c.put("jours", j);
		if (n == 1 || (n == 10 && !e.boss))
			p.displayClientMessage(Component.translatable(n == 1 ? "airain.codex.nouvelle" : "airain.codex.note",
				ev.getEntity().getType().getDescription()).withStyle(net.minecraft.ChatFormatting.GOLD), true);
		if (n == 1) emblemes(p, c, v, e.force);
	}

	/** Toutes les pages d'une force ouvertes : son emblème, une seule fois. */
	private static void emblemes(ServerPlayer p, CompoundTag c, CompoundTag v, Force f) {
		CompoundTag em = c.getCompound("emblemes");
		String k = f.name().toLowerCase();
		if (em.getBoolean(k)) return;
		for (Entree e : ENTREES) if (e.force == f && v.getInt(e.id) == 0) return;
		em.putBoolean(k, true); c.put("emblemes", em);
		ItemStack t = new ItemStack(Items.PAINTING);
		CompoundTag d = new CompoundTag();
		d.putString("id", "minecraft:painting");
		d.putString("variant", "airain:embleme_" + k);
		t.set(DataComponents.ENTITY_DATA, CustomData.of(d));
		if (!p.getInventory().add(t)) p.drop(t, false);
		p.displayClientMessage(Component.translatable("airain.codex.embleme", Component.translatable("airain.codex.force." + k))
			.withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE), false);
	}

	public static ResourceLocation rl(String id) { return ResourceLocation.parse(id); }
}
