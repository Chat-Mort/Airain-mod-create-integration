package fr.chatmort.airain.atlas;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → client : ouvrir l'atlas impérial. */
public record OuvrirAtlas(CompoundTag donnees) implements CustomPacketPayload {
	public static final Type<OuvrirAtlas> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "ouvrir_atlas"));
	public static final StreamCodec<RegistryFriendlyByteBuf, OuvrirAtlas> CODEC =
		StreamCodec.composite(ByteBufCodecs.TRUSTED_COMPOUND_TAG, OuvrirAtlas::donnees, OuvrirAtlas::new);
	@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
