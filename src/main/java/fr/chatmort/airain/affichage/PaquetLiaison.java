package fr.chatmort.airain.affichage;

import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client → serveur : depuis le menu du tableau émaillé, la liaison d'affichage lien passe sur la ligne (−1 : aucune). */
public record PaquetLiaison(BlockPos tableau, BlockPos lien, int ligne) implements CustomPacketPayload {
	public static final Type<PaquetLiaison> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "liaison_tableau_emaille"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PaquetLiaison> CODEC = StreamCodec.composite(
		BlockPos.STREAM_CODEC, PaquetLiaison::tableau, BlockPos.STREAM_CODEC, PaquetLiaison::lien, ByteBufCodecs.VAR_INT, PaquetLiaison::ligne, PaquetLiaison::new);
	@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

	public static void traiter(PaquetLiaison m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> {
			if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.tableau().getCenter()) > 32 * 32) return;
			if (m.lien().distSqr(m.tableau()) > (double) Liaisons.PORTEE * Liaisons.PORTEE) return;
			if (p.level().getBlockEntity(m.tableau()) instanceof EmailBlockEntity e && e.estControleur()) Liaisons.affecter(p.level(), e, m.lien(), m.ligne());
		});
	}
}
