package fr.chatmort.airain.affichage;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client → serveur : les réglages du tableau émaillé, envoyés par le menu à chaque changement. */
public record PaquetEmail(BlockPos pos, CompoundTag reglages) implements CustomPacketPayload {
	public static final Type<PaquetEmail> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "configurer_tableau_emaille"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PaquetEmail> CODEC = StreamCodec.composite(
		BlockPos.STREAM_CODEC, PaquetEmail::pos, ByteBufCodecs.COMPOUND_TAG, PaquetEmail::reglages, PaquetEmail::new);
	@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

	public static void traiter(PaquetEmail m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> {
			if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.pos().getCenter()) > 32 * 32) return;
			if (p.level().getBlockEntity(m.pos()) instanceof EmailBlockEntity e && e.estControleur()) e.appliquer(Reglages.lire(m.reglages()));
		});
	}
}
