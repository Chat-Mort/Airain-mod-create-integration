package fr.chatmort.airain.gardien;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Loupe de la couronne (1.69.1) : clic gauche pendant le zoom, la cible est marquée 8 s pour tous les joueurs. */
public final class MarqueLoupe {
	private MarqueLoupe() {}

	public static final int DUREE = 160;          // 8 s
	public static final double PORTEE = 160;
	private static final int RECHARGE = 20;       // une marque par seconde au plus
	private static final Map<UUID, Long> DERNIERE = new HashMap<>();

	/** Colonne de lumière qui monte de la cible (suit la créature si c'en est une). */
	private record Colonne(ServerLevel sl, Entity suivie, Vec3 pos, long fin) {}
	private static final List<Colonne> COLONNES = new ArrayList<>();

	/** entite = identifiant réseau de la créature visée, ou -1 pour un bloc (pos). */
	public record Marque(int entite, BlockPos pos) implements CustomPacketPayload {
		public static final Type<Marque> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "loupe_marque"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Marque> CODEC = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, Marque::entite, BlockPos.STREAM_CODEC, Marque::pos, Marque::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Marque m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p) || !Fin.couronne(p)) return;
				ServerLevel sl = p.serverLevel();
				long t = sl.getGameTime();
				Long d = DERNIERE.get(p.getUUID());
				if (d != null && t - d < RECHARGE) return;
				Component nom; Vec3 ou; Entity suivie = null;
				if (m.entite() >= 0) {
					Entity e = sl.getEntity(m.entite());
					if (e == null || e == p || !e.isAlive() || e.distanceToSqr(p) > PORTEE * PORTEE) return;
					if (e instanceof LivingEntity v) v.addEffect(new MobEffectInstance(MobEffects.GLOWING, DUREE, 0, false, false));
					else return;
					nom = e.getDisplayName(); ou = e.position(); suivie = e;
				} else {
					BlockPos b = m.pos();
					if (!sl.isLoaded(b) || sl.getBlockState(b).isAir() || b.distToCenterSqr(p.position()) > PORTEE * PORTEE) return;
					fr.chatmort.airain.armure.Armes.repere(sl, b, "airain_eclo_loupe_" + p.getId() + "_" + t, DUREE);
					nom = sl.getBlockState(b).getBlock().getName(); ou = Vec3.atBottomCenterOf(b).add(0, 1, 0);
				}
				DERNIERE.put(p.getUUID(), t);
				COLONNES.add(new Colonne(sl, suivie, ou, t + DUREE));
				sl.playSound(null, ou.x, ou.y, ou.z, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.2f, 1.4f);
				// message à chacun, avec la distance et la direction vues depuis sa propre position
				for (ServerPlayer q : sl.players()) {
					int dist = (int) Math.round(q.position().distanceTo(ou));
					Component dir = Component.translatable("airain.loupe.dir." + direction(ou.x - q.getX(), ou.z - q.getZ()));
					Component msg = q == p
						? Component.translatable("airain.loupe.marque_soi", nom, dist, dir)
						: Component.translatable("airain.loupe.marque", p.getDisplayName(), nom, dist, dir);
					q.displayClientMessage(msg.copy().withStyle(ChatFormatting.GOLD), true);
					if (q != p) q.playNotifySound(SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.PLAYERS, 0.8f, 1.6f);
				}
			});
		}
	}

	/** Huit directions : nord = -Z, est = +X. */
	static String direction(double dx, double dz) {
		double a = Math.toDegrees(Math.atan2(dx, -dz));
		if (a < 0) a += 360;
		String[] n = { "n", "ne", "e", "se", "s", "sw", "w", "nw" };
		return n[(int) Math.round(a / 45) % 8];
	}

	public static void tick(ServerTickEvent.Post e) {
		if (COLONNES.isEmpty()) return;
		Iterator<Colonne> it = COLONNES.iterator();
		while (it.hasNext()) {
			Colonne c = it.next();
			long t = c.sl().getGameTime();
			if (t >= c.fin() || (c.suivie() != null && !c.suivie().isAlive())) { it.remove(); continue; }
			if (t % 3 != 0) continue;
			Vec3 o = c.suivie() != null ? c.suivie().position().add(0, c.suivie().getBbHeight(), 0) : c.pos();
			// colonne de 12 blocs, particules visibles de loin (force = true)
			for (int k = 0; k < 12; k++)
				for (ServerPlayer q : c.sl().players())
					c.sl().sendParticles(q, ParticleTypes.END_ROD, true, o.x, o.y + k, o.z, 1, 0.05, 0.3, 0.05, 0.01);
		}
	}

	public static void arret(ServerStoppedEvent e) { COLONNES.clear(); DERNIERE.clear(); }
}
