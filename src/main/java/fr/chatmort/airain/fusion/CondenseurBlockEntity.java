package fr.chatmort.airain.fusion;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

/** Réservoir de 8 000 mB d'Écho liquide ; {@link #DEBIT} mB (ou de source) par tick dans un sens ou dans l'autre. */
public class CondenseurBlockEntity extends BlockEntity {
	public static final int CAPACITE = 8000, DEBIT = 10, RAYON = 6;
	/** Le réservoir, exposé aux tuyaux de Create (capacité enregistrée dans AirainMod). */
	public final FluidTank reservoir = new FluidTank(CAPACITE, f -> f.getFluid().isSame(EchoLiquide.SOURCE.get())) {
		@Override protected void onContentsChanged() { setChanged(); change = true; }
	};
	/** Le niveau a bougé depuis le dernier envoi aux joueurs (le liquide est dessiné à sa vraie hauteur). */
	private boolean change;

	/** Remplissage de 0 à 1, côté joueur, pour le rendu. */
	public float niveauClient() { return reservoir.getFluidAmount() / (float) CAPACITE; }

	public CondenseurBlockEntity(BlockPos pos, BlockState state) { super(AirainMod.CONDENSEUR_BE.get(), pos, state); }

	void tickServeur() {
		if (level == null) return;
		if (change && level.getGameTime() % 5 == 0) {                                  // envoie le niveau aux joueurs, 4 fois par seconde au plus
			change = false;
			level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
		}
		if (level.getGameTime() % 4 != 0) return;                      // tous les 4 ticks, 4 fois le débit
		int lot = DEBIT * 4;
		if (!getBlockState().getValue(CondenseurBlock.EVAPORE)) {                        // jarres → liquide
			int place = CAPACITE - reservoir.getFluidAmount();
			if (place <= 0) return;
			int pris = Source.prendre(level, worldPosition, RAYON, Math.min(lot, place));
			if (pris > 0) reservoir.fill(new FluidStack(EchoLiquide.SOURCE.get(), pris), IFluidHandler.FluidAction.EXECUTE);
		} else {                                                                          // liquide → jarres (90 %)
			int dispo = Math.min(lot, reservoir.getFluidAmount());
			if (dispo < 10) return;
			int verse = Source.verser(level, worldPosition, RAYON, dispo * 9 / 10);      // jarres pleines : le liquide reste
			if (verse > 0) reservoir.drain(Math.min(dispo, (int) Math.ceil(verse / 0.9)), IFluidHandler.FluidAction.EXECUTE);
		}
	}

	// Synchronisation du contenu avec les joueurs (pour la hauteur du liquide)
	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }

	@Override
	public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getUpdatePacket() {
		return net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(this);
	}

	@Override
	protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); t.put("reservoir", reservoir.writeToNBT(r, new CompoundTag())); }

	@Override
	protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); reservoir.readFromNBT(r, t.getCompound("reservoir")); }
}
