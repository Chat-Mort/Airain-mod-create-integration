package fr.chatmort.airain.armure;

import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → clients : ce joueur lance le tourbillon (animation de rotation). */
public record TourbillonPaquet(int entite) implements CustomPacketPayload {
	public static final Type<TourbillonPaquet> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "tourbillon"));
	public static final StreamCodec<ByteBuf, TourbillonPaquet> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, TourbillonPaquet::entite, TourbillonPaquet::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
