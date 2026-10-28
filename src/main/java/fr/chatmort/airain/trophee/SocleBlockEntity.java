package fr.chatmort.airain.trophee;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class SocleBlockEntity extends BlockEntity {
	private ItemStack trophee = ItemStack.EMPTY;

	public SocleBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.SOCLE_BE.get(), pos, state);
	}

	public ItemStack trophee() {
		return trophee;
	}

	public void exposer(ItemStack pile) {
		trophee = pile.copyWithCount(1);
		if (level instanceof ServerLevel sl)
			TropheeRegistre.de(sl.getServer()).poser(level, worldPosition, BuiltInRegistries.ITEM.getKey(trophee.getItem()));
		maj();
	}

	public ItemStack reprendre() {
		ItemStack p = trophee;
		trophee = ItemStack.EMPTY;
		if (level instanceof ServerLevel sl)
			TropheeRegistre.de(sl.getServer()).retirer(level, worldPosition);
		maj();
		return p;
	}

	@Override
	public void onLoad() {
		super.onLoad();
		if (level instanceof ServerLevel sl && !trophee.isEmpty())   // au cas où le registre aurait été perdu
			TropheeRegistre.de(sl.getServer()).poser(level, worldPosition, BuiltInRegistries.ITEM.getKey(trophee.getItem()));
	}

	private void maj() {
		setChanged();
		if (level != null)
			level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registres) {
		super.saveAdditional(tag, registres);
		if (!trophee.isEmpty())
			tag.put("trophee", trophee.save(registres));
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registres) {
		super.loadAdditional(tag, registres);
		trophee = tag.contains("trophee") ? ItemStack.parseOptional(registres, tag.getCompound("trophee")) : ItemStack.EMPTY;
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider registres) {
		return saveWithoutMetadata(registres);
	}

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() {
		return ClientboundBlockEntityDataPacket.create(this);
	}
}
