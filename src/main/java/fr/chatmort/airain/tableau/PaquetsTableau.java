package fr.chatmort.airain.tableau;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Échanges du tableau de service. */
public final class PaquetsTableau {
	private PaquetsTableau() {}

	public record NoteVue(int id, int couleur, boolean fait, String texte, String auteur, int jour, boolean nouvelle) {
		public static final StreamCodec<RegistryFriendlyByteBuf, NoteVue> CODEC = StreamCodec.of((b, n) -> {
			b.writeVarInt(n.id()); b.writeVarInt(n.couleur()); b.writeBoolean(n.fait()); b.writeUtf(n.texte(), 256);
			b.writeUtf(n.auteur(), 64); b.writeVarInt(n.jour()); b.writeBoolean(n.nouvelle());
		}, b -> new NoteVue(b.readVarInt(), b.readVarInt(), b.readBoolean(), b.readUtf(256), b.readUtf(64), b.readVarInt(), b.readBoolean()));
	}

	/** Serveur → client : ouvrir (ou rafraîchir) un tableau. */
	public record Ouvrir(BlockPos pos, Component titre, List<NoteVue> notes) implements CustomPacketPayload {
		public static final Type<Ouvrir> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "tableau_ouvrir"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Ouvrir> CODEC = StreamCodec.composite(
			BlockPos.STREAM_CODEC, Ouvrir::pos, ComponentSerialization.STREAM_CODEC, Ouvrir::titre,
			NoteVue.CODEC.apply(ByteBufCodecs.collection(ArrayList::new)), Ouvrir::notes, Ouvrir::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
	}

	/** Client → serveur : action sur une note. action 0 : ajouter (texte, couleur) ; 1 : fait / à faire ; 2 : retirer. */
	public record Action(BlockPos pos, int action, int id, String texte, int couleur) implements CustomPacketPayload {
		public static final Type<Action> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "tableau_action"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Action> CODEC = StreamCodec.composite(
			BlockPos.STREAM_CODEC, Action::pos, ByteBufCodecs.VAR_INT, Action::action, ByteBufCodecs.VAR_INT, Action::id,
			ByteBufCodecs.stringUtf8(256), Action::texte, ByteBufCodecs.VAR_INT, Action::couleur, Action::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Action m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.pos().getCenter()) > 64) return;
				if (!(p.level().getBlockState(m.pos()).getBlock() instanceof TableauBlock)) return;
				Tableaux all = Tableaux.de(p.server);
				Tableaux.Tableau t = all.tableau(p.level().dimension().location(), m.pos());
				String nom = p.getGameProfile().getName();
				switch (m.action()) {
					case 0 -> {
						String texte = m.texte().strip();
						if (texte.isEmpty() || t.notes.size() >= Tableaux.NOTES) break;
						Tableaux.Note n = new Tableaux.Note();
						n.id = t.suivant++; n.couleur = Math.floorMod(m.couleur(), 3); n.texte = texte.length() > 200 ? texte.substring(0, 200) : texte;
						n.auteur = nom; n.jour = (int) (p.server.overworld().getDayTime() / 24000L) + 1; n.lus.add(nom);
						t.notes.add(n);
						p.level().playSound(null, m.pos(), net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, net.minecraft.sounds.SoundSource.BLOCKS, 1f, 1.3f);
					}
					case 1 -> t.notes.stream().filter(n -> n.id == m.id()).findFirst().ifPresent(n -> n.fait = !n.fait);
					case 2 -> t.notes.removeIf(n -> n.id == m.id());
					default -> {}
				}
				all.setDirty();
				envoyer(p, m.pos());
			});
		}
	}

	/** Envoie le tableau au joueur et marque ses notes comme lues. */
	public static void envoyer(ServerPlayer p, BlockPos pos) {
		Tableaux all = Tableaux.de(p.server);
		Tableaux.Tableau t = all.tableau(p.level().dimension().location(), pos);
		String nom = p.getGameProfile().getName();
		List<NoteVue> l = new ArrayList<>();
		for (Tableaux.Note n : t.notes) {
			l.add(new NoteVue(n.id, n.couleur, n.fait, n.texte, n.auteur, n.jour, !n.lus.contains(nom)));
			n.lus.add(nom);
		}
		all.setDirty();
		PacketDistributor.sendToPlayer(p, new Ouvrir(pos, Tableaux.nomBase(p.server, p.level().dimension().location(), pos), l));
	}
}
