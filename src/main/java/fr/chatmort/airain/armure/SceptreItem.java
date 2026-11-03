package fr.chatmort.airain.armure;

import java.util.List;

import fr.chatmort.airain.gardien.GardienEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Sceptre impérial (rappel et charge des gardiens) ou sceptre arcanique (onde sonique, sorts renforcés en main). */
public class SceptreItem extends Item {
	public final Lignee lignee;

	public SceptreItem(Lignee lignee, Properties p) { super(p); this.lignee = lignee; }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.lignee." + lignee.cle()).withStyle(ChatFormatting.DARK_RED, ChatFormatting.ITALIC));
		String k = "airain.sceptre." + lignee.cle();
		l.add(Component.translatable(k + ".l1").withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable(k + ".l2").withStyle(ChatFormatting.GRAY));
	}

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack s = p.getItemInHand(main);
		if (level.isClientSide) return InteractionResultHolder.success(s);
		if (!Armes.autorise(p, lignee) || p.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(s);
		ServerPlayer sp = (ServerPlayer) p;
		if (lignee == Lignee.EMPIRE) {
			if (p.isShiftKeyDown()) charge(sp); else rappel(sp);
		} else onde(sp);
		return InteractionResultHolder.consume(s);
	}

	/** Rappel : tous les gardiens chargés rattachés au joueur (escorte) ou proches de lui accourent. */
	private void rappel(ServerPlayer p) {
		ServerLevel sl = p.serverLevel();
		int n = 0;
		for (GardienEntity g : sl.getEntitiesOfClass(GardienEntity.class, new AABB(p.blockPosition()).inflate(256), g -> !g.enPanne())) {
			g.teleportTo(p.getX() + (sl.random.nextDouble() - 0.5) * 4, p.getY(), p.getZ() + (sl.random.nextDouble() - 0.5) * 4);
			g.getNavigation().stop();
			sl.sendParticles(ParticleTypes.END_ROD, g.getX(), g.getY() + 1.4, g.getZ(), 12, 0.4, 0.8, 0.4, 0.05);
			n++;
		}
		sl.playSound(null, p.blockPosition(), SoundEvents.BELL_BLOCK, SoundSource.PLAYERS, 1.2f, 1.2f);
		p.displayClientMessage(Component.translatable("airain.sceptre.empire.rappel", n), true);
		p.getCooldowns().addCooldown(this, 200);
	}

	/** Ordre de charge : Force II et Vitesse II aux gardiens proches pendant 30 s. */
	private void charge(ServerPlayer p) {
		ServerLevel sl = p.serverLevel();
		int n = 0;
		for (GardienEntity g : sl.getEntitiesOfClass(GardienEntity.class, new AABB(p.blockPosition()).inflate(32), g -> !g.enPanne())) {
			g.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 600, 1));
			g.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 600, 1));
			sl.sendParticles(ParticleTypes.FLAME, g.getX(), g.getY() + 2.2, g.getZ(), 8, 0.3, 0.2, 0.3, 0.02);
			n++;
		}
		sl.playSound(null, p.blockPosition(), SoundEvents.RAID_HORN.value(), SoundSource.PLAYERS, 2f, 1.1f);
		p.displayClientMessage(Component.translatable("airain.sceptre.empire.charge", n), true);
		p.getCooldowns().addCooldown(this, 2400);
	}

	/** Onde sonique lancée droit devant : 16 blocs, 10 dégâts, traverse les armures. */
	private void onde(ServerPlayer p) {
		ServerLevel sl = p.serverLevel();
		Vec3 de = p.getEyePosition(), dir = p.getLookAngle();
		for (int i = 1; i <= 16; i++) {
			Vec3 q = de.add(dir.scale(i));
			sl.sendParticles(ParticleTypes.SONIC_BOOM, q.x, q.y, q.z, 1, 0, 0, 0, 0);
		}
		for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, new AABB(de, de.add(dir.scale(16))).inflate(1.5), e -> Armes.ennemi(p, e))) {
			if (Armes.centre(e).subtract(de).cross(dir).length() > 1.5) continue;
			e.invulnerableTime = 0;
			e.hurt(sl.damageSources().sonicBoom(p), 10f);
		}
		sl.playSound(null, p.blockPosition(), SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 1f, 1.1f);
		p.getCooldowns().addCooldown(this, 60);
	}
}
