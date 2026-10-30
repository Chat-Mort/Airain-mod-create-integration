package fr.chatmort.airain.enchant;

import com.simibubi.create.api.equipment.goggles.IHaveGoggleInformation;
import fr.chatmort.airain.AirainMod;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.LongArrayTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.ChiseledBookShelfBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayList;
import java.util.List;

/**
 * Livre flottant (même logique que la table vanilla) et lecture des bibliothèques : le serveur compte toutes les deux
 * secondes les livres et les tomes des bibliothèques sculptées voisines et l'envoie au client (le client ne voit pas
 * leur contenu) : de là viennent les glyphes qui volent vers la table et les informations des lunettes.
 */
public class TableEmpireBlockEntity extends BlockEntity implements IHaveGoggleInformation {
	private static final RandomSource HASARD = RandomSource.create();
	public int temps;
	public float tourne, oTourne, cibleRot, flip, oFlip, flipCible, flipVit, ouvert, oOuvert;
	private int livres, enchantements, tomes;
	/** Bibliothèques qui comptent (position relative), et celles qui portent un tome ancien. */
	private long[] etageres = new long[0], etageresTome = new long[0];

	public TableEmpireBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.TABLE_BE.get(), pos, state);
	}

	public List<BlockPos> etageres(boolean tome) {
		List<BlockPos> l = new ArrayList<>();
		for (long v : tome ? etageresTome : etageres) l.add(BlockPos.of(v));
		return l;
	}

	public static void tickServeur(Level level, BlockPos pos, BlockState state, TableEmpireBlockEntity be) {
		if (level.getGameTime() % 40 != 0) return;
		int nl = 0, nt = 0;
		List<Long> et = new ArrayList<>(), eto = new ArrayList<>();
		for (BlockPos p : BlockPos.betweenClosed(pos.offset(-Bibliotheque.RAYON, -1, -Bibliotheque.RAYON), pos.offset(Bibliotheque.RAYON, 2, Bibliotheque.RAYON))) {
			if (!(level.getBlockEntity(p) instanceof ChiseledBookShelfBlockEntity e)) continue;
			boolean livre = false, tome = false;
			for (int i = 0; i < e.getContainerSize(); i++) {
				ItemStack s = e.getItem(i);
				if (Bibliotheque.enchantementDuTome(s) != null) { nt++; tome = true; }
				else if (s.is(Items.ENCHANTED_BOOK)) { nl++; livre = true; }
			}
			if (livre || tome) et.add(p.subtract(pos).asLong());
			if (tome) eto.add(p.subtract(pos).asLong());
		}
		int ne = Bibliotheque.lire(level, pos).size();
		long[] a = et.stream().mapToLong(Long::longValue).toArray(), b = eto.stream().mapToLong(Long::longValue).toArray();
		if (nl != be.livres || nt != be.tomes || ne != be.enchantements || !java.util.Arrays.equals(a, be.etageres) || !java.util.Arrays.equals(b, be.etageresTome)) {
			be.livres = nl; be.tomes = nt; be.enchantements = ne; be.etageres = a; be.etageresTome = b;
			be.setChanged();
			level.sendBlockUpdated(pos, state, state, Block.UPDATE_CLIENTS);
		}
	}

	@Override
	public boolean addToGoggleTooltip(List<Component> tooltip, boolean isPlayerSneaking) {
		tooltip.add(Component.literal("    ").append(Component.translatable("airain.table.lunettes.titre")));
		tooltip.add(Component.literal("     ").append(Component.translatable("airain.table.livres", livres).withStyle(ChatFormatting.GRAY)));
		tooltip.add(Component.literal("     ").append(Component.translatable("airain.table.enchantements", enchantements).withStyle(ChatFormatting.AQUA)));
		if (tomes > 0)
			tooltip.add(Component.literal("     ").append(Component.translatable("airain.table.tomes", tomes).withStyle(ChatFormatting.GOLD)));
		if (livres == 0 && tomes == 0)
			tooltip.add(Component.literal("     ").append(Component.translatable("airain.table.aucun").withStyle(ChatFormatting.DARK_GRAY)));
		return true;
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.saveAdditional(tag, r);
		tag.putInt("livres", livres); tag.putInt("enchantements", enchantements); tag.putInt("tomes", tomes);
		tag.put("etageres", new LongArrayTag(etageres)); tag.put("etageresTome", new LongArrayTag(etageresTome));
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.loadAdditional(tag, r);
		livres = tag.getInt("livres"); enchantements = tag.getInt("enchantements"); tomes = tag.getInt("tomes");
		etageres = tag.getLongArray("etageres"); etageresTome = tag.getLongArray("etageresTome");
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider r) {
		CompoundTag t = saveWithoutMetadata(r);
		t.putBoolean("sync", true);
		return t;
	}

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() {
		return ClientboundBlockEntityDataPacket.create(this);
	}

	public static void animer(Level level, BlockPos pos, BlockState state, TableEmpireBlockEntity be) {
		be.oOuvert = be.ouvert;
		be.oTourne = be.tourne;
		Player p = level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 3.0, false);
		if (p != null) {
			be.cibleRot = (float) Mth.atan2(p.getZ() - (pos.getZ() + 0.5), p.getX() - (pos.getX() + 0.5));
			be.ouvert += 0.1F;
			if (be.ouvert < 0.5F || HASARD.nextInt(40) == 0) {
				float avant = be.flipCible;
				do {
					be.flipCible += (float) (HASARD.nextInt(4) - HASARD.nextInt(4));
				} while (avant == be.flipCible);
			}
		} else {
			be.cibleRot += 0.02F;
			be.ouvert -= 0.1F;
		}
		be.tourne = Mth.wrapDegrees(be.tourne * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		be.cibleRot = Mth.wrapDegrees(be.cibleRot * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		float d = Mth.wrapDegrees((be.cibleRot - be.tourne) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		be.tourne += d * 0.4F;
		be.ouvert = Mth.clamp(be.ouvert, 0.0F, 1.0F);
		be.temps++;
		be.oFlip = be.flip;
		float f = Mth.clamp((be.flipCible - be.flip) * 0.4F, -0.2F, 0.2F);
		be.flipVit += (f - be.flipVit) * 0.9F;
		be.flip += be.flipVit;
	}
}
