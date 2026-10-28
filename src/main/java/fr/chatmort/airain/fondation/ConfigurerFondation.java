package fr.chatmort.airain.fondation;

import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client → serveur : nom et apparence d'un étendard de fondation. */
public record ConfigurerFondation(BlockPos pos, String nom, String devise, int apparence) implements CustomPacketPayload {
	public static final Type<ConfigurerFondation> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "configurer_fondation"));
	public static final StreamCodec<RegistryFriendlyByteBuf, ConfigurerFondation> CODEC = StreamCodec.composite(
		BlockPos.STREAM_CODEC, ConfigurerFondation::pos, ByteBufCodecs.stringUtf8(32), ConfigurerFondation::nom,
		ByteBufCodecs.stringUtf8(48), ConfigurerFondation::devise, ByteBufCodecs.VAR_INT, ConfigurerFondation::apparence, ConfigurerFondation::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }

	public static void traiter(ConfigurerFondation m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> {
			if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.pos().getCenter()) > 100) return;
			if (p.level().getBlockEntity(m.pos()) instanceof FondationBlockEntity f) {
				String n = m.nom().trim();
				String d = m.devise().trim();
				f.configurer(n.length() <= 32 ? n : n.substring(0, 32), d.length() <= 48 ? d : d.substring(0, 48), Apparence.unpack(m.apparence()));
			}
		});
	}
}
