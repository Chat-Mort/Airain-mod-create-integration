package fr.chatmort.airain.trophee;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client → serveur : apparence du piédestal et texte de la plaque. */
public record ConfigurerSocle(BlockPos pos, int apparence, String plaque) implements CustomPacketPayload {
	public static final Type<ConfigurerSocle> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "configurer_socle"));
	public static final StreamCodec<RegistryFriendlyByteBuf, ConfigurerSocle> CODEC = StreamCodec.composite(
		BlockPos.STREAM_CODEC, ConfigurerSocle::pos, ByteBufCodecs.VAR_INT, ConfigurerSocle::apparence,
		ByteBufCodecs.stringUtf8(32), ConfigurerSocle::plaque, ConfigurerSocle::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }

	public static void traiter(ConfigurerSocle m, IPayloadContext ctx) {
		ctx.enqueueWork(() -> {
			if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.pos().getCenter()) > 100) return;
			if (p.level().getBlockEntity(m.pos()) instanceof SocleBlockEntity s) appliquer(p, s, SocleApparence.unpack(m.apparence()), m.plaque().trim());
		});
	}

	/** Applique des réglages (écran ou gabarit) ; la colonne haute demande la place au-dessus. */
	public static void appliquer(net.minecraft.world.entity.player.Player p, SocleBlockEntity s, SocleApparence a, String plaque) {
		if (!SocleBlock.changerHauteur(s.getLevel(), s.getBlockPos(), a.haute())) {
			int[] v = a.valeurs(); v[5] = 0; a = SocleApparence.depuis(v);
			if (p != null) p.displayClientMessage(Component.translatable("airain.socle.pas_de_place").withStyle(ChatFormatting.RED), true);
		}
		s.configurer(a, plaque);
	}
}
