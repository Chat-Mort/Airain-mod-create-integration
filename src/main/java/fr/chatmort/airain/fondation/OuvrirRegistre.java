package fr.chatmort.airain.fondation;

import io.netty.buffer.ByteBuf;
import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

import java.util.ArrayList;
import java.util.List;

/** Serveur → client : ouvrir le registre des fondations, avec toutes les bases et tous les trophées. */
public record OuvrirRegistre(List<Base> bases, List<Trophee> trophees) implements CustomPacketPayload {
	public record Base(String nom, String devise, BlockPos pos, ResourceLocation dim, int apparence, int ext, int gardiens, int limite) {
		private record Tete(String nom, String devise, BlockPos pos, ResourceLocation dim) {}
		private static final StreamCodec<ByteBuf, Tete> TETE = StreamCodec.composite(
			ByteBufCodecs.stringUtf8(64), Tete::nom, ByteBufCodecs.stringUtf8(64), Tete::devise,
			BlockPos.STREAM_CODEC, Tete::pos, ResourceLocation.STREAM_CODEC, Tete::dim, Tete::new);
		public static final StreamCodec<ByteBuf, Base> CODEC = StreamCodec.composite(
			TETE, b -> new Tete(b.nom(), b.devise(), b.pos(), b.dim()),
			ByteBufCodecs.INT, Base::apparence, ByteBufCodecs.INT, Base::ext, ByteBufCodecs.VAR_INT, Base::gardiens, ByteBufCodecs.VAR_INT, Base::limite,
			(t, a, e, g, l) -> new Base(t.nom(), t.devise(), t.pos(), t.dim(), a, e, g, l));
	}

	/** base : indice dans la liste des bases (-1 : hors de toute base). */
	public record Trophee(ResourceLocation objet, String plaque, int jour, int base) {
		public static final StreamCodec<ByteBuf, Trophee> CODEC = StreamCodec.composite(
			ResourceLocation.STREAM_CODEC, Trophee::objet, ByteBufCodecs.stringUtf8(64), Trophee::plaque,
			ByteBufCodecs.VAR_INT, Trophee::jour, ByteBufCodecs.VAR_INT, Trophee::base, Trophee::new);
	}

	public static final Type<OuvrirRegistre> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "ouvrir_registre"));
	public static final StreamCodec<RegistryFriendlyByteBuf, OuvrirRegistre> CODEC = StreamCodec.composite(
		Base.CODEC.apply(ByteBufCodecs.collection(ArrayList::new)), OuvrirRegistre::bases,
		Trophee.CODEC.apply(ByteBufCodecs.collection(ArrayList::new)), OuvrirRegistre::trophees, OuvrirRegistre::new);

	@Override
	public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
