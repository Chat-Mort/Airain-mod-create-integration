package fr.chatmort.airain.chronique;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * Serveur → client : un thème joué une seule fois, à un moment de l'histoire (la lettre d'Ada, la fin).
 * Il coupe la musique en cours et ne dépend pas de la position (comme la musique du jeu).
 */
public record Theme(String son) implements CustomPacketPayload {
	public static final Type<Theme> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "theme"));
	public static final StreamCodec<RegistryFriendlyByteBuf, Theme> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, Theme::son, Theme::new);

	/** Thème d'Ada et d'Elias. */
	public static final String ADA_ELIAS = "kubejs:mechanical_love";
	/** La fin : la mélodie commune, renversée et descendante. */
	public static final String EPILOGUE = "kubejs:epilogue";

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }

	public static void jouer(MinecraftServer s, String son) {
		for (ServerPlayer p : s.getPlayerList().getPlayers()) net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(p, new Theme(son));
	}
}
