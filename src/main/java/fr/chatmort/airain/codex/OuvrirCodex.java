package fr.chatmort.airain.codex;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Serveur → client : ouvrir le codex, avec les victoires et les jours du joueur. */
public record OuvrirCodex(CompoundTag donnees) implements CustomPacketPayload {
	public static final Type<OuvrirCodex> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "ouvrir_codex"));
	public static final StreamCodec<RegistryFriendlyByteBuf, OuvrirCodex> CODEC =
		StreamCodec.composite(ByteBufCodecs.COMPOUND_TAG, OuvrirCodex::donnees, OuvrirCodex::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
