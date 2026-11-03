package fr.chatmort.airain.pouvoir;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;

/** Siège invisible sur lequel s'assoit le joueur (même placement que les sièges de Create). */
public class Assise extends Entity {
	public Assise(EntityType<?> t, Level l) { super(t, l); noPhysics = true; }

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {}
	@Override
	protected void readAdditionalSaveData(CompoundTag t) {}
	@Override
	protected void addAdditionalSaveData(CompoundTag t) {}

	@Override
	public void tick() {
		super.tick();
		if (!level().isClientSide && (getPassengers().isEmpty() || !(level().getBlockState(blockPosition()).getBlock() instanceof SiegeBlock))) discard();
	}

	@Override
	protected void positionRider(Entity e, MoveFunction f) {
		if (!hasPassenger(e)) return;
		double h = getPassengerRidingPosition(e).y - e.getVehicleAttachmentPoint(this).y;
		f.accept(e, getX(), 2.0 / 16.0 + h, getZ());
	}
}
