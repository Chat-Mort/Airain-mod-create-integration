package fr.chatmort.airain.fondation;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → client : afficher le nom de la fondation en haut de l'écran. */
public record TitreFondation(String nom) implements CustomPacketPayload {
	public static final Type<TitreFondation> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "titre_fondation"));
	public static final StreamCodec<RegistryFriendlyByteBuf, TitreFondation> CODEC = StreamCodec.composite(
		ByteBufCodecs.stringUtf8(64), TitreFondation::nom, TitreFondation::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
