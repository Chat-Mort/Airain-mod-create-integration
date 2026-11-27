package fr.chatmort.airain.pouvoir;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

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
		// 1.71 : on reste assis aussi sur les chaises, le fauteuil et le banc du mobilier impérial
		BlockState sous = level().getBlockState(blockPosition());
		if (!level().isClientSide && (getPassengers().isEmpty() || !(sous.getBlock() instanceof SiegeBlock || fr.chatmort.airain.fonderie.Mobilier.assisable(sous)))) discard();
	}

	@Override
	protected void positionRider(Entity e, MoveFunction f) {
		if (!hasPassenger(e)) return;
		double h = getPassengerRidingPosition(e).y - e.getVehicleAttachmentPoint(this).y;
		f.accept(e, getX(), 2.0 / 16.0 + h, getZ());
	}
}
