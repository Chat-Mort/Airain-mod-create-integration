package fr.chatmort.airain.chronique;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → client : ouvrir les Chroniques oubliées. */
public record OuvrirChroniques(CompoundTag donnees) implements CustomPacketPayload {
	public static final Type<OuvrirChroniques> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "ouvrir_chroniques"));
	public static final StreamCodec<RegistryFriendlyByteBuf, OuvrirChroniques> CODEC =
		StreamCodec.composite(ByteBufCodecs.TRUSTED_COMPOUND_TAG, OuvrirChroniques::donnees, OuvrirChroniques::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
