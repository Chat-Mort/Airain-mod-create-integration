package fr.chatmort.airain.fondation;

import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client → serveur : le nouveau nom d'une fondation. */
public record NommerFondation(BlockPos pos, String nom) implements CustomPacketPayload {
	public static final Type<NommerFondation> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "nommer_fondation"));
	public static final StreamCodec<RegistryFriendlyByteBuf, NommerFondation> CODEC = StreamCodec.composite(
		BlockPos.STREAM_CODEC, NommerFondation::pos, ByteBufCodecs.stringUtf8(32), NommerFondation::nom, NommerFondation::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }

	public static void traiter(NommerFondation m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> {
			if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.pos().getCenter()) > 64) return;
			if (p.level().getBlockEntity(m.pos()) instanceof FondationBlockEntity f) {
				String n = m.nom().trim();
				if (!n.isEmpty() && n.length() <= 32) f.nommer(n);
			}
		});
	}
}
