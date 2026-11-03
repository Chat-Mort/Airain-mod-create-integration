package fr.chatmort.airain.pouvoir;

import java.util.Arrays;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.tick.LevelTickEvent;

import fr.chatmort.airain.fondation.FondationRegistre;
import fr.chatmort.airain.gardien.GardienEntity;

/** Décrets et chants : choix depuis le siège, et leurs effets. */
public final class Siege {
	private Siege() {}

	// ------------------------------------------------------------------ réapparition et menu
	/** Le joueur réapparaît devant le siège. */
	static void reapparition(ServerPlayer p, ServerLevel l, BlockPos pos, BlockState s) {
		BlockPos devant = pos.relative(s.getValue(SiegeBlock.FACING));
		p.setRespawnPosition(l.dimension(), devant, s.getValue(SiegeBlock.FACING).getOpposite().toYRot(), true, false);
	}

	static void menu(ServerPlayer p, boolean trone) {
		MinecraftServer s = p.server;
		Pouvoir pv = Pouvoir.de(s);
		ChatFormatting c = trone ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE;
		p.sendSystemMessage(Component.translatable(trone ? "airain.siege.menu_trone" : "airain.siege.menu_solium").withStyle(c, ChatFormatting.BOLD));
		if (!pv.effet.isEmpty() && pv.reste(s) > 0)
			p.sendSystemMessage(Component.translatable("airain.siege.en_cours", Component.translatable("airain.pouvoir." + pv.effet), minutes(pv.reste(s))).withStyle(ChatFormatting.GRAY));
		long att = pv.attente(s);
		if (att > 0) p.sendSystemMessage(Component.translatable("airain.siege.attente", minutes(att)).withStyle(ChatFormatting.DARK_GRAY));
		for (String e : trone ? Pouvoir.DECRETS : Pouvoir.CHANTS)             // un décret (ou un chant) par ligne
			p.sendSystemMessage(Component.literal(" [").append(Component.translatable("airain.pouvoir." + e)).append("]")
				.withStyle(st -> st.withColor(att > 0 ? ChatFormatting.DARK_GRAY : c)
					.withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/pouvoir choisir " + e))
					.withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.translatable("airain.pouvoir." + e + ".desc")))));
	}

	static String minutes(long ticks) { return String.valueOf((ticks + 1199) / 1200); }

	// ------------------------------------------------------------------ commandes
	public static void commandes(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("pouvoir")
			.then(Commands.literal("choisir").then(Commands.argument("effet", StringArgumentType.word()).executes(c -> {
				ServerPlayer p = c.getSource().getPlayerOrException();
				return choisir(p, StringArgumentType.getString(c, "effet")) ? 1 : 0;
			})))
			.then(Commands.literal("prime").requires(s -> s.hasPermission(2))
				.then(Commands.argument("piece", StringArgumentType.word()).then(Commands.argument("nombre", IntegerArgumentType.integer(1)).executes(c -> {
					prime(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "piece"), IntegerArgumentType.getInteger(c, "nombre"));
					return 1;
				})))));
	}

	private static boolean choisir(ServerPlayer p, String e) {
		MinecraftServer s = p.server;
		Pouvoir pv = Pouvoir.de(s);
		if (!pv.present() || !(p.getVehicle() instanceof Assise a) || !a.blockPosition().equals(pv.pos)) {
			p.displayClientMessage(Component.translatable("airain.siege.pas_assis"), true);
			return false;
		}
		if (!Arrays.asList(pv.trone ? Pouvoir.DECRETS : Pouvoir.CHANTS).contains(e)) return false;
		if (pv.attente(s) > 0) {
			p.displayClientMessage(Component.translatable("airain.siege.attente", minutes(pv.attente(s))), true);
			return false;
		}
		pv.choisir(s, e);
		ServerLevel l = (ServerLevel) p.level();
		l.playSound(null, pv.pos, pv.trone ? SoundEvents.RAID_HORN.value() : SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, pv.trone ? 0.6f : 2f, pv.trone ? 1.2f : 0.5f);
		l.sendParticles(pv.trone ? ParticleTypes.END_ROD : ParticleTypes.SCULK_SOUL, pv.pos.getX() + 0.5, pv.pos.getY() + 1.8, pv.pos.getZ() + 0.5, 30, 0.6, 0.8, 0.6, 0.05);
		Component annonce = Component.translatable(pv.trone ? "airain.siege.promulgue" : "airain.siege.entonne", p.getDisplayName(),
			Component.translatable("airain.pouvoir." + e)).withStyle(pv.trone ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE);
		for (ServerPlayer o : s.getPlayerList().getPlayers()) o.sendSystemMessage(annonce);
		return true;
	}

	/** Décret de prospérité : +50 % sur une commande de l'Empire, rendu en pièces. */
	private static final String[] PIECES = {"spur", "bevel", "sprocket", "cog", "crown", "sun"};
	private static final int[] VALEURS = {1, 8, 16, 64, 512, 4096};
	private static void prime(ServerPlayer p, String piece, int n) {
		if (!Pouvoir.actif(p.server, "prosperite")) return;
		String nom = piece.contains(":") ? piece.substring(piece.indexOf(':') + 1) : piece;
		int i = Arrays.asList(PIECES).indexOf(nom);
		if (i < 0) return;
		int reste = VALEURS[i] * n / 2;
		if (reste <= 0) return;
		for (int k = PIECES.length - 1; k >= 0 && reste > 0; k--) {
			int q = reste / VALEURS[k];
			if (q == 0) continue;
			reste -= q * VALEURS[k];
			ItemStack st = new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("numismatics", PIECES[k])), q);
			if (!p.getInventory().add(st)) p.drop(st, false);
		}
		p.displayClientMessage(Component.translatable("airain.siege.prime").withStyle(ChatFormatting.GOLD), true);
	}

	// ------------------------------------------------------------------ décret de guerre
	/** Au lieu de mourir, le joueur est ramené au trône (une fois par minute). */
	public static void mort(LivingDeathEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY) && !e.getSource().is(net.minecraft.world.damagesource.DamageTypes.FELL_OUT_OF_WORLD)) return;
		MinecraftServer s = p.server;
		if (!Pouvoir.actif(s, "guerre")) return;
		Pouvoir pv = Pouvoir.de(s);
		ServerLevel l = pv.niveau(s);
		if (l == null) return;
		long t = Pouvoir.maintenant(s);
		var d = p.getPersistentData();
		if (t < d.getLong("airain_sauve") + 1200) return;
		d.putLong("airain_sauve", t);
		e.setCanceled(true);
		p.setHealth(p.getMaxHealth() / 2);
		p.clearFire();
		p.fallDistance = 0;
		p.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
		for (MobEffectInstance m : p.getActiveEffects().stream().filter(m -> m.getEffect().value().getCategory() == MobEffectCategory.HARMFUL).toList())
			p.removeEffect(m.getEffect());
		BlockState st = l.getBlockState(pv.pos);
		BlockPos devant = st.getBlock() instanceof SiegeBlock ? pv.pos.relative(st.getValue(SiegeBlock.FACING)) : pv.pos.above();
		p.teleportTo(l, devant.getX() + 0.5, devant.getY(), devant.getZ() + 0.5, p.getYRot(), p.getXRot());
		p.invulnerableTime = 60;
		l.playSound(null, devant, SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 0.8f, 1.3f);
		l.sendParticles(ParticleTypes.END_ROD, devant.getX() + 0.5, devant.getY() + 1, devant.getZ() + 0.5, 30, 0.4, 0.8, 0.4, 0.05);
		p.sendSystemMessage(Component.translatable("airain.siege.sauve").withStyle(ChatFormatting.GOLD));
	}

	/** Décret de guerre : tous les gardiens frappent plus fort et encaissent mieux. */
	public static void gardien(GardienEntity g) {
		if (g.tickCount % 20 != 0 || !(g.level() instanceof ServerLevel sl) || !Pouvoir.actif(sl.getServer(), "guerre")) return;
		g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 60, 1, true, false));
		g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 1, true, false));
	}

	// ------------------------------------------------------------------ chant de croissance
	/** Les plantes des bases poussent trois fois plus vite : deux fois plus de ticks aléatoires (6 de plus par section). */
	public static void croissance(LevelTickEvent.Post e) {
		if (!(e.getLevel() instanceof ServerLevel l) || !Pouvoir.actif(l.getServer(), "croissance")) return;
		int n = 2 * l.getGameRules().getInt(net.minecraft.world.level.GameRules.RULE_RANDOMTICKING);
		if (n <= 0) return;
		var dim = l.dimension().location();
		for (FondationRegistre.Fondation f : FondationRegistre.de(l.getServer()).toutes()) {
			if (!f.dim().equals(dim)) continue;
			int r = f.rayon(), cx0 = SectionPos.blockToSectionCoord(f.pos().getX() - r), cx1 = SectionPos.blockToSectionCoord(f.pos().getX() + r);
			int cz0 = SectionPos.blockToSectionCoord(f.pos().getZ() - r), cz1 = SectionPos.blockToSectionCoord(f.pos().getZ() + r);
			for (int cx = cx0; cx <= cx1; cx++)
				for (int cz = cz0; cz <= cz1; cz++) {
					if (!l.shouldTickBlocksAt(ChunkPos.asLong(cx, cz))) continue;
					LevelChunk ch = l.getChunkSource().getChunkNow(cx, cz);
					if (ch == null) continue;
					LevelChunkSection[] secs = ch.getSections();
					for (int i = 0; i < secs.length; i++) {
						LevelChunkSection sec = secs[i];
						if (!sec.isRandomlyTicking()) continue;
						int y0 = SectionPos.sectionToBlockCoord(ch.getSectionYFromSectionIndex(i));
						for (int k = 0; k < n; k++) {
							BlockPos p = new BlockPos((cx << 4) + l.random.nextInt(16), y0 + l.random.nextInt(16), (cz << 4) + l.random.nextInt(16));
							BlockState s = sec.getBlockState(p.getX() & 15, p.getY() & 15, p.getZ() & 15);
							if (s.isRandomlyTicking() && plante(s.getBlock())) s.randomTick(l, p, l.random);
						}
					}
				}
		}
	}

	private static boolean plante(Block b) {
		return b instanceof BushBlock || b instanceof SugarCaneBlock || b instanceof CactusBlock || b instanceof BambooStalkBlock
			|| b instanceof CocoaBlock || b instanceof GrowingPlantHeadBlock || b instanceof ChorusFlowerBlock;
	}

	// ------------------------------------------------------------------ chant des âmes
	public static float experience(MinecraftServer s) { return Pouvoir.actif(s, "ames") ? 2f : 1f; }
}
