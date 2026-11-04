package fr.chatmort.airain.borne;

import java.util.ArrayList;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** La caisse livrée sur la zone d'arrivage : descend en parachute (Empire) ou se matérialise (Écho). Clic droit : on la vide. */
public class CaisseEntity extends Entity {
	private static final EntityDataAccessor<Boolean> EMPIRE = SynchedEntityData.defineId(CaisseEntity.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<Boolean> POSEE = SynchedEntityData.defineId(CaisseEntity.class, EntityDataSerializers.BOOLEAN);
	public static final int APPARITION = 30;
	private final List<ItemStack> contenu = new ArrayList<>();
	private double sol;
	public int age;

	public CaisseEntity(EntityType<?> t, Level l) { super(t, l); noPhysics = true; setNoGravity(true); }

	public static CaisseEntity creer(ServerLevel l, Vec3 pos, double sol, boolean empire, List<ItemStack> contenu) {
		CaisseEntity e = new CaisseEntity(AirainMod.CAISSE.get(), l);
		e.setPos(pos);
		e.sol = sol;
		e.entityData.set(EMPIRE, empire);
		e.entityData.set(POSEE, !empire);
		e.contenu.addAll(contenu);
		return e;
	}

	public boolean empire() { return entityData.get(EMPIRE); }
	public boolean posee() { return entityData.get(POSEE); }

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) { b.define(EMPIRE, true); b.define(POSEE, false); }

	@Override
	public void tick() {
		super.tick();
		age++;
		if (!posee()) {
			if (!level().isClientSide) {
				double y = getY() - 0.2;
				if (y <= sol) {
					setPos(getX(), sol, getZ());
					entityData.set(POSEE, true);
					((ServerLevel) level()).sendParticles(ParticleTypes.CLOUD, getX(), sol + 0.1, getZ(), 24, 0.6, 0.05, 0.6, 0.03);
					level().playSound(null, blockPosition(), SoundEvents.WOOD_PLACE, SoundSource.BLOCKS, 1f, 0.7f);
					level().playSound(null, blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.BLOCKS, 0.3f, 1.6f);
				} else setPos(getX(), y, getZ());
			}
		} else if (!empire() && level().isClientSide && age % 6 == 0) {
			level().addParticle(ParticleTypes.REVERSE_PORTAL, getX() + (random.nextDouble() - 0.5), getY() + random.nextDouble(), getZ() + (random.nextDouble() - 0.5), 0, 0.02, 0);
		}
	}

	/** Facteur d'apparition côté Écho (0 → 1). */
	public float echelle(float pt) { return empire() ? 1f : Math.min(1f, (age + pt) / APPARITION); }

	@Override
	public InteractionResult interact(Player p, InteractionHand main) {
		if (level().isClientSide) return InteractionResult.SUCCESS;
		if (!posee()) return InteractionResult.PASS;
		vider(p);
		return InteractionResult.CONSUME;
	}

	private void vider(Player p) {
		for (ItemStack s : contenu) if (!p.getInventory().add(s.copy())) p.drop(s.copy(), false);
		contenu.clear();
		ServerLevel sl = (ServerLevel) level();
		sl.sendParticles(empire() ? ParticleTypes.CRIT : ParticleTypes.WITCH, getX(), getY() + 0.5, getZ(), 20, 0.3, 0.3, 0.3, 0.1);
		sl.playSound(null, blockPosition(), empire() ? SoundEvents.BARREL_OPEN : SoundEvents.AMETHYST_CLUSTER_BREAK, SoundSource.BLOCKS, 1f, 1f);
		discard();
	}

	@Override
	public boolean hurt(DamageSource d, float a) {
		if (!level().isClientSide && posee() && d.getEntity() instanceof Player p && !isRemoved()) vider(p);
		return false;
	}

	@Override
	public boolean isPickable() { return !isRemoved(); }

	@Override
	public boolean isAttackable() { return true; }

	@Override
	public boolean ignoreExplosion(net.minecraft.world.level.Explosion e) { return true; }

	@Override
	protected void readAdditionalSaveData(CompoundTag t) {
		entityData.set(EMPIRE, t.getBoolean("empire"));
		entityData.set(POSEE, t.getBoolean("posee"));
		sol = t.getDouble("sol");
		age = APPARITION;
		contenu.clear();
		for (Tag e : t.getList("contenu", Tag.TAG_COMPOUND)) ItemStack.parse(registryAccess(), e).ifPresent(contenu::add);
	}

	@Override
	protected void addAdditionalSaveData(CompoundTag t) {
		t.putBoolean("empire", empire());
		t.putBoolean("posee", posee());
		t.putDouble("sol", sol);
		ListTag l = new ListTag();
		for (ItemStack s : contenu) if (!s.isEmpty()) l.add(s.save(registryAccess()));
		t.put("contenu", l);
	}
}
