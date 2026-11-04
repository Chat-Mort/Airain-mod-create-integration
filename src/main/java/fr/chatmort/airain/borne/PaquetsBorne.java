package fr.chatmort.airain.borne;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Échanges de la borne de commande. */
public final class PaquetsBorne {
	private PaquetsBorne() {}
	public static final int PILES = 27;

	/** Serveur → client : ouvrir le catalogue. */
	public record Ouvrir(BlockPos pos, boolean empire, int restant, boolean occupee) implements CustomPacketPayload {
		public static final Type<Ouvrir> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "borne_ouvrir"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Ouvrir> CODEC = StreamCodec.composite(
			BlockPos.STREAM_CODEC, Ouvrir::pos, ByteBufCodecs.BOOL, Ouvrir::empire, ByteBufCodecs.VAR_INT, Ouvrir::restant,
			ByteBufCodecs.BOOL, Ouvrir::occupee, Ouvrir::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
	}

	/** Une ligne du bon de commande : l'objet, le lot (indice dans Catalogue.LOTS) et le nombre de lots. */
	public record Ligne(ResourceLocation id, int lot, int fois) {
		public static final StreamCodec<RegistryFriendlyByteBuf, Ligne> CODEC = StreamCodec.composite(
			ResourceLocation.STREAM_CODEC, Ligne::id, ByteBufCodecs.VAR_INT, Ligne::lot, ByteBufCodecs.VAR_INT, Ligne::fois, Ligne::new);
		public Item item() { return BuiltInRegistries.ITEM.get(id); }
		public int quantite() { return Catalogue.LOTS[lot] * fois; }
		public long prix() { return (long) Catalogue.prix(item(), lot) * fois; }
		public int piles() { int m = Math.max(1, new ItemStack(item()).getMaxStackSize()); return (quantite() + m - 1) / m; }
	}

	public static long total(List<Ligne> l) { long t = 0; for (Ligne x : l) t += x.prix(); return t; }
	public static int piles(List<Ligne> l) { int t = 0; for (Ligne x : l) t += x.piles(); return t; }

	/** Client → serveur : passer commande. */
	public record Commander(BlockPos pos, List<Ligne> lignes) implements CustomPacketPayload {
		public static final Type<Commander> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "borne_commander"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Commander> CODEC = StreamCodec.composite(
			BlockPos.STREAM_CODEC, Commander::pos, Ligne.CODEC.apply(ByteBufCodecs.collection(ArrayList::new)), Commander::lignes, Commander::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Commander m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p) || p.distanceToSqr(m.pos().getCenter()) > 100) return;
				if (!(p.level().getBlockEntity(m.pos()) instanceof BorneBlockEntity be)) return;
				if (!(be.getBlockState().getBlock() instanceof BorneBlock b) || !b.lignee().autorisee(p.server)) return;
				String refus = null;
				if (be.enCours()) refus = "airain.borne.en_cours";
				else if (be.zoneOccupee()) refus = "airain.borne.occupee";
				else if (m.lignes().isEmpty()) return;
				else {
					for (Ligne l : m.lignes())
						if (l.fois() < 1 || l.fois() > 64 || l.item() == Items.AIR || !Catalogue.vendable(l.item()) || Catalogue.prix(l.item(), l.lot()) <= 0) return;
					if (piles(m.lignes()) > PILES) refus = "airain.borne.trop";
					else if (!Catalogue.payer(p, total(m.lignes()))) refus = "airain.borne.fonds";
				}
				if (refus != null) { p.displayClientMessage(Component.translatable(refus).withStyle(ChatFormatting.RED), true); return; }
				List<ItemStack> piles = new ArrayList<>();
				for (Ligne l : m.lignes()) {
					int n = l.quantite(), max = Math.max(1, new ItemStack(l.item()).getMaxStackSize());
					while (n > 0) { int q = Math.min(n, max); piles.add(new ItemStack(l.item(), q)); n -= q; }
				}
				be.lancer(piles);
				p.displayClientMessage(Component.translatable(b.empire ? "airain.borne.ok_empire" : "airain.borne.ok_echo")
					.withStyle(b.empire ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE), true);
			});
		}
	}
}
