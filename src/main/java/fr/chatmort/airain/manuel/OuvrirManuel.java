package fr.chatmort.airain.manuel;

import java.util.List;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → client : ouvrir un manuel d'armes (camp) avec la liste des pages dévoilées. */
public record OuvrirManuel(int camp, List<String> pages) implements CustomPacketPayload {
	public static final Type<OuvrirManuel> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "ouvrir_manuel"));
	public static final StreamCodec<RegistryFriendlyByteBuf, OuvrirManuel> CODEC = StreamCodec.composite(
		ByteBufCodecs.VAR_INT, OuvrirManuel::camp,
		ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()), OuvrirManuel::pages,
		OuvrirManuel::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
