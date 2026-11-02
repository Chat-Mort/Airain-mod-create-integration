package fr.chatmort.airain.reliure;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Les échanges de la Reliure. */
public final class Paquets {
	private Paquets() {}

	/** Client → serveur : lire le livre n° index de la Reliure trouvée à (ou, case). */
	public record Lire(int ou, int slot, int index) implements CustomPacketPayload {
		public static final Type<Lire> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "reliure_lire"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Lire> CODEC = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, Lire::ou, ByteBufCodecs.VAR_INT, Lire::slot, ByteBufCodecs.VAR_INT, Lire::index, Lire::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Lire m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p)) return;
				ItemStack r = Reliure.trouver(p, m.ou(), m.slot());
				List<ItemStack> l = Reliure.livres(r);
				if (m.index() >= 0 && m.index() < l.size()) Reliure.lire(p, l.get(m.index()));
			});
		}
	}

	/** Client → serveur : la touche de la Reliure ; le serveur la cherche (sacs compris) et renvoie ses livres. */
	public record Chercher() implements CustomPacketPayload {
		public static final Type<Chercher> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "reliure_chercher"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Chercher> CODEC = StreamCodec.unit(new Chercher());
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Chercher m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p)) return;
				ItemStack r = Reliure.chercher(p);
				if (r.isEmpty()) {
					p.displayClientMessage(net.minecraft.network.chat.Component.translatable("airain.reliure.introuvable"), true);
					return;
				}
				PacketDistributor.sendToPlayer(p, new Ouvrir(Reliure.RECHERCHE, -1, Reliure.livres(r)));
			});
		}
	}

	/** Serveur → client : ouvrir l'écran de lecture avec ces livres. */
	public record Ouvrir(int ou, int slot, List<ItemStack> livres) implements CustomPacketPayload {
		public static final Type<Ouvrir> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "reliure_ouvrir"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Ouvrir> CODEC = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, Ouvrir::ou, ByteBufCodecs.VAR_INT, Ouvrir::slot,
			ItemStack.OPTIONAL_STREAM_CODEC.apply(ByteBufCodecs.collection(ArrayList::new)), Ouvrir::livres, Ouvrir::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
	}
}
