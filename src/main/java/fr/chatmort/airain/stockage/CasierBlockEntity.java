package fr.chatmort.airain.stockage;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponentMap;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Le contenu d'un casier : un seul objet (modèle), sa quantité, le nombre de renforts (capacité 32 piles × 2^renforts),
 * et la réservation à la clé. Le contenu reste dans l'objet quand on casse le casier.
 */
public class CasierBlockEntity extends BlockEntity {
	public static final int PILES = 32, RENFORTS_MAX = 4;
	/** 1.66.6 : piles par casier selon les renforts (×4 par renfort, puis 5 120 au IV : 327 680 objets, comme un baril de
	 *  netherite de Sophisticated avec son amélioration de pile en netherite). */
	private static final int[] CAPACITES = {32, 128, 512, 2048, 5120};
	public static int piles(int renforts) { return CAPACITES[Math.max(0, Math.min(RENFORTS_MAX, renforts))]; }
	ItemStack modele = ItemStack.EMPTY;
	long quantite;
	int renforts;
	boolean reserve;
	private final Map<UUID, Long> derniersDepots = new HashMap<>();
	final Reseau reseau = new Reseau(this);
	public Reseau reseau() { return reseau; }

	public CasierBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }

	public ItemStack modele() { return modele; }
	public long quantite() { return quantite; }
	public int renforts() { return renforts; }
	public boolean reserve() { return reserve; }
	public long capacite() { return modele.isEmpty() ? (long) piles(renforts) : (long) piles(renforts) * modele.getMaxStackSize(); }
	public long capacitePour(ItemStack s) { return (long) piles(renforts) * s.getMaxStackSize(); }
	/** Ce casier accepte-t-il cet objet ? */
	boolean accepte(ItemStack s) {
		if (s.isEmpty()) return false;
		if (modele.isEmpty()) return true;
		return ItemStack.isSameItemSameComponents(modele, s);
	}
	/** Ajoute jusqu'à n exemplaires de s ; rend combien sont entrés. */
	long ajouter(ItemStack s, long n, boolean simuler) {
		if (!accepte(s)) return 0;
		long place = capacitePour(s) - (modele.isEmpty() ? 0 : quantite);
		long k = Math.max(0, Math.min(place, n));
		if (k > 0 && !simuler) {
			if (modele.isEmpty()) { modele = s.copyWithCount(1); quantite = 0; }
			quantite += k; changer();
		}
		return k;
	}
	/** Retire jusqu'à n exemplaires ; rend la pile retirée. */
	ItemStack retirer(long n, boolean simuler) {
		if (modele.isEmpty() || quantite <= 0) return ItemStack.EMPTY;
		int k = (int) Math.min(Math.min(n, quantite), modele.getMaxStackSize());
		ItemStack r = modele.copyWithCount(k);
		if (!simuler) {
			quantite -= k;
			if (quantite <= 0 && !reserve) { modele = ItemStack.EMPTY; quantite = 0; }
			changer();
		}
		return r;
	}
	void changer() {
		setChanged();
		if (level != null && !level.isClientSide) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
	}

	// ---------------------------------------------------------------- à la main
	void deposer(Player j, InteractionHand h) {
		long t = level.getGameTime();
		Long avant = derniersDepots.get(j.getUUID());
		boolean double_ = avant != null && t - avant <= 8;
		int n = 0;
		if (h != null) {
			ItemStack st = j.getItemInHand(h);
			long k = ajouter(st, st.getCount(), false);
			if (k > 0) { st.shrink((int) k); n += k; }
			else if (!modele.isEmpty() && !accepte(st)) { info(j); return; }
		}
		if (double_ && !modele.isEmpty()) {          // deux clics de suite : tout ce qu'on porte de cet objet
			var inv = j.getInventory();
			for (int i = 0; i < inv.getContainerSize(); i++) {
				ItemStack s = inv.getItem(i);
				if (!accepte(s)) continue;
				long k = ajouter(s, s.getCount(), false);
				if (k > 0) { s.shrink((int) k); n += k; }
			}
		}
		derniersDepots.put(j.getUUID(), t);
		if (n > 0) level.playSound(null, worldPosition, SoundEvents.ITEM_FRAME_ADD_ITEM, SoundSource.BLOCKS, 0.6f, 1.1f);
		else if (h == null && !double_) info(j);
	}
	void prendre(Player j, boolean un) {
		ItemStack r = retirer(un ? 1 : modele.isEmpty() ? 0 : modele.getMaxStackSize(), false);
		if (r.isEmpty()) return;
		if (!j.getInventory().add(r)) j.drop(r, false);
		level.playSound(null, worldPosition, SoundEvents.ITEM_FRAME_REMOVE_ITEM, SoundSource.BLOCKS, 0.6f, 1f);
	}
	void info(Player j) {
		if (modele.isEmpty()) j.displayClientMessage(Component.translatable("airain.casier.vide", piles(renforts)).withStyle(ChatFormatting.GOLD), true);
		else j.displayClientMessage(Component.translatable("airain.casier.contenu", modele.getHoverName(), quantite, capacite()).withStyle(ChatFormatting.GOLD), true);
	}
	void verrouiller(Player j) {
		if (modele.isEmpty()) { if (j != null) j.displayClientMessage(Component.translatable("airain.casier.rien_a_reserver").withStyle(ChatFormatting.RED), true); return; }
		reserve = !reserve;
		if (!reserve && quantite <= 0) modele = ItemStack.EMPTY;
		changer();
		if (j != null) j.displayClientMessage(Component.translatable(reserve ? "airain.casier.reserve" : "airain.casier.libere").withStyle(ChatFormatting.GOLD), true);
		level.playSound(null, worldPosition, SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
	}
	void renforcer(Player j, ItemStack st, int niveau) {
		if (renforts >= RENFORTS_MAX) { j.displayClientMessage(Component.translatable("airain.casier.renforce_max").withStyle(ChatFormatting.RED), true); return; }
		if (niveau != renforts + 1) { j.displayClientMessage(Component.translatable("airain.casier.renfort_ordre", renforts + 1).withStyle(ChatFormatting.RED), true); return; }
		renforts++;
		if (!j.getAbilities().instabuild) st.shrink(1);
		changer();
		level.playSound(null, worldPosition, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 0.8f, 1.2f);
		j.displayClientMessage(Component.translatable("airain.casier.renforce", piles(renforts)).withStyle(ChatFormatting.GOLD), true);
	}

	// ---------------------------------------------------------------- sauvegarde, synchro, contenu gardé dans l'objet
	CompoundTag contenu(HolderLookup.Provider r) {
		CompoundTag t = new CompoundTag();
		if (!modele.isEmpty()) t.put("modele", modele.save(r));
		t.putLong("quantite", quantite); t.putByte("renforts", (byte) renforts); t.putBoolean("reserve", reserve);
		return t;
	}
	void lireContenu(CompoundTag t, HolderLookup.Provider r) {
		modele = t.contains("modele") ? ItemStack.parse(r, t.getCompound("modele")).orElse(ItemStack.EMPTY) : ItemStack.EMPTY;
		quantite = t.getLong("quantite"); renforts = Math.max(0, Math.min(RENFORTS_MAX, t.getByte("renforts"))); reserve = t.getBoolean("reserve");
		if (modele.isEmpty()) quantite = 0;
	}
	@Override protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); t.put("casier", contenu(r)); }
	@Override protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); lireContenu(t.getCompound("casier"), r); }
	@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { CompoundTag t = super.getUpdateTag(r); t.put("casier", contenu(r)); return t; }
	@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
	// l'objet du casier cassé emporte son contenu (copié par la table de butin)
	@Override
	protected void collectImplicitComponents(DataComponentMap.Builder b) {
		super.collectImplicitComponents(b);
		if (level != null && (quantite > 0 || renforts > 0 || reserve)) b.set(DataComponents.CUSTOM_DATA, CustomData.of(contenu(level.registryAccess())));
	}
	@Override
	protected void applyImplicitComponents(BlockEntity.DataComponentInput in) {
		super.applyImplicitComponents(in);
		CustomData d = in.get(DataComponents.CUSTOM_DATA);
		if (d != null && level != null) lireContenu(d.copyTag(), level.registryAccess());
		else if (d != null) attente = d.copyTag();
	}
	private CompoundTag attente;
	@Override
	public void onLoad() {
		super.onLoad();
		if (attente != null && level != null) { lireContenu(attente, level.registryAccess()); attente = null; }
	}
	@Override public void removeComponentsFromTag(CompoundTag t) { t.remove("casier"); }
}
