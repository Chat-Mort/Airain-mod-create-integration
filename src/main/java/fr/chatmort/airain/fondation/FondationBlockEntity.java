package fr.chatmort.airain.fondation;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Porte d'un étendard (petit ou grand) ou d'une bannière murale : nom, rayon de la zone, apparence de la bannière,
 * hauteur du mât, mise en berne. La bannière murale est purement décorative : elle n'entre pas au registre.
 */
public class FondationBlockEntity extends BlockEntity {
	public static final int RAYON_MIN = 16, RAYON_MAX = 128, PAS = 16;
	private String nom = "";
	private String devise = "";
	private int rayon = 48;
	private int hauteur = GrandEtendardBlock.MAT;   // grand étendard : nombre de blocs du mât
	private Apparence apparence = Apparence.DEFAUT;
	private boolean berne;
	/** Côté client : position de la bannière, 0 = hissée, 1 = en berne (avec la valeur du tick précédent). */
	private float hisse, hisseAvant;

	public FondationBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.FONDATION_BE.get(), pos, state);
	}

	public String nom() { return nom; }
	public String devise() { return devise; }
	public int rayon() { return rayon; }
	public int hauteur() { return hauteur; }

	public void hauteur(int h) {
		hauteur = h; maj();
	}
	public Apparence apparence() { return apparence; }
	public boolean murale() { return getBlockState().getBlock() instanceof BanniereMuraleBlock; }
	public boolean grand() { return getBlockState().getBlock() instanceof GrandEtendardBlock; }

	public float hisse(float pt) { return hisseAvant + (hisse - hisseAvant) * pt; }

	/** Signal de redstone : la bannière descend (ou s'enroule) lentement, puis remonte. */
	public void mettreEnBerne(boolean b) {
		if (b != berne) { berne = b; maj(); }
	}

	/** Tick côté client : animation de la mise en berne, claquements de toile par grand vent ou par orage. */
	public void tickClient() {
		hisseAvant = hisse;
		hisse = berne ? Math.min(1f, hisse + 1 / 60f) : Math.max(0f, hisse - 1 / 60f);
		if (level == null) return;
		BlockPos haut = worldPosition.above(grand() ? hauteur : murale() ? 0 : 2);
		float chance = (grand() || murale()) && apparence.vent() == 2 ? 0.004f : 0f;
		if (level.canSeeSky(haut)) chance += level.isThundering() ? 0.03f : level.isRaining() ? 0.012f : 0f;
		if (chance > 0 && level.random.nextFloat() < chance)
			level.playLocalSound(haut.getX() + 0.5, haut.getY(), haut.getZ() + 0.5, net.minecraft.sounds.SoundEvents.PHANTOM_FLAP,
				net.minecraft.sounds.SoundSource.BLOCKS, 0.22f, 0.55f + level.random.nextFloat() * 0.25f, false);
	}

	/** Vent dû à la météo, si le ciel est visible au sommet. */
	public float meteo() {
		if (level == null) return 1f;
		BlockPos haut = worldPosition.above(grand() ? hauteur : murale() ? 0 : 2);
		if (!level.canSeeSky(haut)) return 1f;
		return level.isThundering() ? 1.8f : level.isRaining() ? 1.35f : 1f;
	}

	/** Ticker client commun aux trois blocs. */
	@SuppressWarnings("unchecked")
	public static <T extends BlockEntity> net.minecraft.world.level.block.entity.BlockEntityTicker<T> ticker(
			net.minecraft.world.level.Level l, net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
		return l.isClientSide && type == AirainMod.FONDATION_BE.get()
			? (lv, p, st, be) -> ((FondationBlockEntity) be).tickClient() : null;
	}

	/** Position de la porte d'un étendard ou d'une bannière murale à partir de n'importe lequel de ses blocs. */
	public static BlockPos porte(net.minecraft.world.level.Level l, BlockPos pos) {
		BlockState s = l.getBlockState(pos);
		if (s.getBlock() instanceof GrandEtendardBlock) return pos.below(s.getValue(GrandEtendardBlock.PARTIE));
		if (s.getBlock() instanceof FondationBlock)
			return s.getValue(FondationBlock.HALF) == net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER ? pos.below() : pos;
		if (s.getBlock() instanceof BanniereMuraleBlock) return pos;
		return null;
	}

	public void configurer(String n, String d, Apparence a) {
		if (!(getBlockState().getBlock() instanceof GrandEtendardBlock) && a.estMasque()) {   // seul le grand peut être décoratif
			int[] v = a.valeurs(); v[12] = 0; a = Apparence.depuis(v);
		}
		nom = n; devise = d; apparence = a;
		if (level != null && !level.isClientSide && getBlockState().getBlock() instanceof FondationBlock)
			FondationBlock.appliquerStyle(level, worldPosition, a.style());
		enregistrer(); maj();
	}

	public void regler(int r) {
		rayon = Math.max(RAYON_MIN, Math.min(RAYON_MAX, r)); enregistrer(); maj();
	}

	public void enregistrer() {
		if (level instanceof ServerLevel sl && !murale())
			FondationRegistre.de(sl.getServer()).mettre(level, worldPosition, nom, rayon, devise, apparence.pack(), apparence.packExt());
	}

	@Override
	public void onLoad() {
		super.onLoad();
		if (level != null && !level.isClientSide && getBlockState().getBlock() instanceof GrandEtendardBlock)
			level.getServer().execute(() -> GrandEtendardBlock.marquerSommet(level, worldPosition, hauteur));   // étendards posés avant la hauteur réglable
		enregistrer();
	}

	private void maj() {
		setChanged();
		if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
	}

	@Override
	protected void saveAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.saveAdditional(tag, r);
		tag.putString("nom", nom); tag.putString("devise", devise); tag.putInt("rayon", rayon); tag.putInt("apparence", apparence.pack()); tag.putInt("ext", apparence.packExt()); tag.putBoolean("berne", berne); tag.putInt("hauteur", hauteur);
	}

	@Override
	protected void loadAdditional(CompoundTag tag, HolderLookup.Provider r) {
		super.loadAdditional(tag, r);
		nom = tag.getString("nom"); devise = tag.getString("devise"); rayon = tag.contains("rayon") ? tag.getInt("rayon") : 48;
		berne = tag.getBoolean("berne");
		hauteur = tag.contains("hauteur") ? tag.getInt("hauteur") : GrandEtendardBlock.MAT;
		apparence = tag.contains("apparence") ? Apparence.unpack(tag.getInt("apparence"), tag.getInt("ext")) : Apparence.DEFAUT;
	}

	@Override
	public CompoundTag getUpdateTag(HolderLookup.Provider r) { CompoundTag t = saveWithoutMetadata(r); t.putBoolean("sync", true); return t; }

	@Override
	public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
}
