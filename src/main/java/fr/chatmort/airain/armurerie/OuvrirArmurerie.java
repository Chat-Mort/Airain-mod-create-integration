package fr.chatmort.airain.armurerie;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → client : ouvrir un manuel des armes (echo = Traité de l'Écho), avec la liste des objets déjà vus. */
public record OuvrirArmurerie(boolean echo, CompoundTag vus) implements CustomPacketPayload {
	public static final Type<OuvrirArmurerie> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "ouvrir_armurerie"));
	public static final StreamCodec<RegistryFriendlyByteBuf, OuvrirArmurerie> CODEC = StreamCodec.composite(
		ByteBufCodecs.BOOL, OuvrirArmurerie::echo, ByteBufCodecs.TRUSTED_COMPOUND_TAG, OuvrirArmurerie::vus, OuvrirArmurerie::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
