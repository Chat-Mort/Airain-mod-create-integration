package fr.chatmort.airain.gardien;

import java.util.EnumSet;
import java.util.UUID;

import fr.chatmort.airain.fondation.FondationRegistre;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsTargetGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;

/**
 * Gardien d'airain : un golem de l'Empire. On le trouve en panne dans les ruines ;
 * réparé à la clé, il garde la fondation à laquelle il est rattaché (ou suit son escorte).
 */
public class GardienEntity extends IronGolem {
	private static final EntityDataAccessor<Boolean> PANNE = SynchedEntityData.defineId(GardienEntity.class, EntityDataSerializers.BOOLEAN);
	public static final TagKey<EntityType<?>> CIBLES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("airain", "cibles_gardien"));
	public static final ResourceLocation CLE = ResourceLocation.fromNamespaceAndPath("create", "wrench");
	public static final ResourceLocation FERRAILLE = ResourceLocation.fromNamespaceAndPath("kubejs", "ferraille");
	public static final ResourceLocation HUILE = ResourceLocation.fromNamespaceAndPath("kubejs", "huile_machine");
	public static final ResourceLocation ROUAGE = ResourceLocation.fromNamespaceAndPath("kubejs", "rouage_brise");
	public static final int COUT_FERRAILLE = 16, COUT_HUILE = 4, COUT_ROUAGE = 2;

	/** Clé de la fondation gardée (null : sans poste). */
	String fondation;
	/** Joueur escorté (null : pas d'escorte). */
	UUID escorte;
	/** Poste d'un gardien sans fondation. */
	BlockPos poste;

	public GardienEntity(EntityType<? extends IronGolem> type, Level level) {
		super(type, level);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(PANNE, false);
	}

	public boolean enPanne() { return entityData.get(PANNE); }
	public void mettreEnPanne(boolean p) { entityData.set(PANNE, p); }

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0, true));
		goalSelector.addGoal(2, new MoveTowardsTargetGoal(this, 0.9, 32f));
		goalSelector.addGoal(3, new Suivre());
		goalSelector.addGoal(4, new MoveTowardsRestrictionGoal(this, 1.0));
		goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.6));
		goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 6f));
		goalSelector.addGoal(8, new RandomLookAroundGoal(this));
		targetSelector.addGoal(1, new HurtByTargetGoal(this));
		targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Mob.class, 5, false, false, GardienEntity::hostile));
	}

	static boolean hostile(LivingEntity e) {
		if (e instanceof GardienEntity) return false;
		return (e instanceof Enemy && !(e instanceof Creeper)) || e.getType().is(CIBLES) || e.getTags().contains("airain_vague");
	}

	// ---- en panne : immobile, sans IA (un mob immobile ne fait pas tourner ses objectifs)
	@Override
	public boolean isImmobile() { return enPanne() || super.isImmobile(); }

	@Override
	public boolean isPushable() { return !enPanne() && super.isPushable(); }

	@Override
	public void aiStep() {
		super.aiStep();
		if (level().isClientSide && enPanne() && random.nextInt(50) == 0)
			level().addParticle(ParticleTypes.SMOKE, getX() + (random.nextDouble() - 0.5) * 0.8, getY() + 1.4, getZ() + (random.nextDouble() - 0.5) * 0.8, 0, 0.02, 0);
	}

	@Override
	public void tick() {
		super.tick();
		if (!level().isClientSide && !enPanne() && tickCount % 20 == 0) majPoste();
	}

	private void majPoste() {
		ServerLevel sl = (ServerLevel) level();
		Gardiens.renforcer(this);
		if (escorte != null) {
			if (sl.getPlayerByUUID(escorte) != null) { clearRestriction(); return; }
			restrictTo(blockPosition(), 8);
			return;
		}
		if (fondation != null) {
			FondationRegistre.Fondation f = FondationRegistre.de(sl.getServer()).par(fondation);
			if (f != null && f.dim().equals(sl.dimension().location())) {
				restrictTo(f.pos(), Math.min(f.rayon(), 48));
				return;
			}
			Gardiens.de(sl.getServer()).liberer(fondation, getUUID());
			fondation = null;
			poste = blockPosition();
		}
		if (poste == null) poste = blockPosition();
		restrictTo(poste, 10);
	}

	// ---- interactions
	static Item objet(ResourceLocation id) { return BuiltInRegistries.ITEM.get(id); }

	static boolean estCle(ItemStack s) { return BuiltInRegistries.ITEM.getKey(s.getItem()).equals(CLE); }

	@Override
	protected InteractionResult mobInteract(Player p, InteractionHand main) {
		ItemStack s = p.getItemInHand(main);
		boolean cle = estCle(s);
		if (enPanne()) {
			if (level().isClientSide) return InteractionResult.SUCCESS;
			if (!cle) {
				p.displayClientMessage(Component.translatable("airain.gardien.aide", COUT_FERRAILLE, COUT_HUILE, COUT_ROUAGE), true);
				return InteractionResult.CONSUME;
			}
			if (!p.getAbilities().instabuild && !payer(p)) {
				level().playSound(null, blockPosition(), SoundEvents.IRON_GOLEM_HURT, SoundSource.NEUTRAL, 0.6f, 0.6f);
				p.displayClientMessage(Component.translatable("airain.gardien.manque", COUT_FERRAILLE, COUT_HUILE, COUT_ROUAGE), true);
				return InteractionResult.CONSUME;
			}
			reparer(p);
			return InteractionResult.CONSUME;
		}
		if (cle && p.isShiftKeyDown()) {
			if (level().isClientSide) return InteractionResult.SUCCESS;
			if (p.getUUID().equals(escorte)) {
				escorte = null; poste = blockPosition();
				p.displayClientMessage(Component.translatable("airain.gardien.poste_ici"), true);
			} else {
				quitterFondation();
				escorte = p.getUUID();
				p.displayClientMessage(Component.translatable("airain.gardien.escorte"), true);
			}
			level().playSound(null, blockPosition(), SoundEvents.IRON_GOLEM_STEP, SoundSource.NEUTRAL, 1f, 1.4f);
			majPoste();
			return InteractionResult.CONSUME;
		}
		if (s.is(objet(HUILE))) {
			if (getHealth() >= getMaxHealth()) return InteractionResult.PASS;
			if (level().isClientSide) return InteractionResult.SUCCESS;
			heal(25f);
			if (!p.getAbilities().instabuild) s.shrink(1);
			level().playSound(null, blockPosition(), SoundEvents.IRON_GOLEM_REPAIR, SoundSource.NEUTRAL, 1f, 0.9f + random.nextFloat() * 0.2f);
			((ServerLevel) level()).sendParticles(ParticleTypes.WAX_ON, getX(), getY() + 1.5, getZ(), 8, 0.5, 0.6, 0.5, 0.1);
			return InteractionResult.CONSUME;
		}
		if (cle) {
			if (!level().isClientSide) p.displayClientMessage(etat(), true);
			return InteractionResult.sidedSuccess(level().isClientSide);
		}
		return InteractionResult.PASS;
	}

	private Component etat() {
		if (escorte != null) return Component.translatable("airain.gardien.etat_escorte");
		if (fondation != null && level() instanceof ServerLevel sl) {
			FondationRegistre.Fondation f = FondationRegistre.de(sl.getServer()).par(fondation);
			if (f != null) return Component.translatable("airain.gardien.etat_base", f.nom().isEmpty() ? Component.translatable("airain.fondation.sans_nom") : Component.literal(f.nom()));
		}
		return Component.translatable("airain.gardien.etat_libre");
	}

	private static boolean payer(Player p) {
		var inv = p.getInventory();
		Item fe = objet(FERRAILLE), hu = objet(HUILE), ro = objet(ROUAGE);
		if (inv.countItem(fe) < COUT_FERRAILLE || inv.countItem(hu) < COUT_HUILE || inv.countItem(ro) < COUT_ROUAGE) return false;
		var grille = p.inventoryMenu.getCraftSlots();
		inv.clearOrCountMatchingItems(st -> st.is(fe), COUT_FERRAILLE, grille);
		inv.clearOrCountMatchingItems(st -> st.is(hu), COUT_HUILE, grille);
		inv.clearOrCountMatchingItems(st -> st.is(ro), COUT_ROUAGE, grille);
		return true;
	}

	private void reparer(Player p) {
		ServerLevel sl = (ServerLevel) level();
		mettreEnPanne(false);
		setPlayerCreated(true);
		setHealth(getMaxHealth());
		Gardiens.renforcer(this);
		sl.playSound(null, blockPosition(), SoundEvents.ANVIL_USE, SoundSource.NEUTRAL, 0.7f, 0.7f);
		sl.playSound(null, blockPosition(), SoundEvents.IRON_GOLEM_REPAIR, SoundSource.NEUTRAL, 1f, 0.8f);
		sl.playSound(null, blockPosition(), SoundEvents.NOTE_BLOCK_DIDGERIDOO.value(), SoundSource.NEUTRAL, 1f, 1.6f);
		sl.sendParticles(ParticleTypes.CLOUD, getX(), getY() + 2.2, getZ(), 12, 0.3, 0.1, 0.3, 0.05);
		sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY() + 1.4, getZ(), 20, 0.6, 0.8, 0.6, 0.2);
		FondationRegistre reg = FondationRegistre.de(sl.getServer());
		FondationRegistre.Fondation f = reg.zone(sl.dimension().location(), getX(), getZ());
		if (f == null) {
			poste = blockPosition();
			p.displayClientMessage(Component.translatable("airain.gardien.reveil_libre"), true);
		} else if (!affecter(f)) {
			escorte = p.getUUID();
			p.displayClientMessage(Component.translatable("airain.gardien.base_pleine", Gardiens.LIMITE), true);
		} else {
			p.displayClientMessage(Component.translatable("airain.gardien.reveil_base", nom(f)), true);
		}
		majPoste();
	}

	static Component nom(FondationRegistre.Fondation f) {
		return f.nom().isEmpty() ? Component.translatable("airain.fondation.sans_nom") : Component.literal(f.nom());
	}

	/** Rattache le gardien à cette fondation, si elle a encore une place. */
	boolean affecter(FondationRegistre.Fondation f) {
		ServerLevel sl = (ServerLevel) level();
		String k = FondationRegistre.cle(f.dim(), f.pos());
		if (k.equals(fondation)) { escorte = null; return true; }
		if (!Gardiens.de(sl.getServer()).lier(k, getUUID())) return false;
		quitterFondation();
		fondation = k;
		escorte = null;
		majPoste();
		return true;
	}

	private void quitterFondation() {
		if (fondation != null && level() instanceof ServerLevel sl) Gardiens.de(sl.getServer()).liberer(fondation, getUUID());
		fondation = null;
	}

	public boolean escorte(Player p) { return p.getUUID().equals(escorte); }

	@Override
	public void remove(RemovalReason raison) {
		if (!level().isClientSide && raison.shouldDestroy()) quitterFondation();
		super.remove(raison);
	}

	// ---- sauvegarde
	@Override
	public void addAdditionalSaveData(CompoundTag t) {
		super.addAdditionalSaveData(t);
		t.putBoolean("Panne", enPanne());
		if (fondation != null) t.putString("Fondation", fondation);
		if (escorte != null) t.putUUID("Escorte", escorte);
		if (poste != null) t.put("Poste", NbtUtils.writeBlockPos(poste));
	}

	@Override
	public void readAdditionalSaveData(CompoundTag t) {
		super.readAdditionalSaveData(t);
		mettreEnPanne(t.getBoolean("Panne"));
		fondation = t.contains("Fondation") ? t.getString("Fondation") : null;
		escorte = t.hasUUID("Escorte") ? t.getUUID("Escorte") : null;
		poste = NbtUtils.readBlockPos(t, "Poste").orElse(null);
	}

	/** Suit le joueur escorté ; se téléporte s'il est trop loin. */
	private class Suivre extends Goal {
		private Player cible;

		Suivre() { setFlags(EnumSet.of(Flag.MOVE)); }

		@Override
		public boolean canUse() {
			if (escorte == null || getTarget() != null) return false;
			cible = level().getPlayerByUUID(escorte);
			return cible != null && !cible.isSpectator() && distanceToSqr(cible) > 25;
		}

		@Override
		public boolean canContinueToUse() {
			return escorte != null && cible != null && cible.isAlive() && getTarget() == null && distanceToSqr(cible) > 9;
		}

		@Override
		public void tick() {
			getLookControl().setLookAt(cible, 10f, getMaxHeadXRot());
			if (distanceToSqr(cible) > 32 * 32 && cible.onGround()) {
				teleportTo(cible.getX(), cible.getY(), cible.getZ());
				getNavigation().stop();
			} else if (tickCount % 10 == 0) {
				getNavigation().moveTo(cible, 1.0);
			}
		}

		@Override
		public void stop() { getNavigation().stop(); cible = null; }
	}
}
