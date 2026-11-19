package fr.chatmort.airain.affichage;

import com.simibubi.create.content.equipment.clipboard.ClipboardCloneable;
import com.simibubi.create.foundation.blockEntity.SmartBlockEntity;
import com.simibubi.create.foundation.blockEntity.behaviour.BlockEntityBehaviour;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

/**
 * Bloc-entité du tableau émaillé. Chaque bloc retrouve le coin en haut à gauche de son tableau (vu de face) ; ce coin
 * (le contrôleur) garde les réglages, les valeurs reçues des liaisons d'affichage, la taille, et règle la lumière et
 * l'accrochage de tous les blocs.
 */
public class EmailBlockEntity extends SmartBlockEntity implements ClipboardCloneable {
	public static final int LARGEUR_MAX = 16, HAUTEUR_MAX = 8;
	/** Réglages : seulement sur le contrôleur (ou en attente d'être rendus au nouveau contrôleur). */
	Reglages reglages;
	final List<String> valeurs = new ArrayList<>();
	/** 1.66.4 : les liaisons d'affichage attribuées depuis le menu du tableau (position de la liaison → ligne, −1 : aucune).
	 *  Le tableau a toujours le dernier mot : une liaison attribuée n'écrit que sur sa ligne, une ligne attribuée refuse les autres. */
	final java.util.Map<BlockPos, Integer> attributions = new java.util.HashMap<>();
	/** La ligne attribuée à cette liaison (−1 : aucune), ou null si le tableau ne l'a jamais réglée. */
	public Integer ligneDe(BlockPos lien) { return attributions.get(lien); }
	/** La liaison attribuée à la ligne, ou null. */
	public BlockPos lienDe(int ligne) {
		for (var e : attributions.entrySet()) if (e.getValue() == ligne) return e.getKey();
		return null;
	}
	private BlockPos ctl;
	int largeur = 1, hauteur = 1;
	boolean alerte, allume;
	private boolean aSynchroniser;

	public EmailBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }
	@Override public void addBehaviours(List<BlockEntityBehaviour> b) {}

	// ---------------------------------------------------------------- géométrie du tableau
	public Direction face() { return getBlockState().getValue(EmailBlock.FACING); }
	/** La droite de celui qui regarde le tableau. */
	public static Direction droite(Direction face) { return face.getCounterClockWise(); }
	public BlockPos controleur() { return ctl == null ? worldPosition : ctl; }
	public boolean estControleur() { return controleur().equals(worldPosition); }
	public Reglages reglages() { return reglages; }
	public String valeur(int i) { return i < valeurs.size() ? valeurs.get(i) : ""; }

	private boolean pareil(BlockPos q) {
		BlockState s = level.getBlockState(q);
		return s.getBlock() instanceof EmailBlock && s.getValue(EmailBlock.FACING) == face();
	}
	/** Le coin en haut à gauche, la largeur et la hauteur ; null si ce bloc est en dehors du rectangle trouvé. */
	private int[] rectangle(BlockPos c) {
		Direction d = droite(face());
		int w = 1; while (w < LARGEUR_MAX && pareil(c.relative(d, w))) w++;
		int h = 1;
		lignes:
		while (h < HAUTEUR_MAX) {
			for (int i = 0; i < w; i++) if (!pareil(c.below(h).relative(d, i))) break lignes;
			h++;
		}
		return new int[] {w, h};
	}
	private void resoudre() {
		Direction g = droite(face()).getOpposite();
		BlockPos c = worldPosition;
		for (int n = 0; n < 48; n++) {
			BlockPos a = c;
			while (pareil(a.above()) && worldPosition.getY() - a.getY() < HAUTEUR_MAX - 1) a = a.above();
			while (pareil(a.relative(g))) a = a.relative(g);
			if (a.equals(c)) break;
			c = a;
		}
		int[] r = rectangle(c);
		Direction d = droite(face());
		// ce bloc est-il dans le rectangle ?
		int dx = (worldPosition.getX() - c.getX()) * d.getStepX() + (worldPosition.getZ() - c.getZ()) * d.getStepZ();
		int dy = c.getY() - worldPosition.getY();
		if (dx < 0 || dx >= r[0] || dy < 0 || dy >= r[1]) { c = worldPosition; r = rectangle(c); r[0] = 1; r[1] = 1; }
		boolean change = !c.equals(controleur());
		ctl = c;
		if (estControleur()) {
			if (reglages == null) reglages = Reglages.neufs();
			if (r[0] != largeur || r[1] != hauteur) { largeur = r[0]; hauteur = r[1]; change = true; }
		} else {
			largeur = hauteur = 1;
			// des réglages en attente : rendus au contrôleur s'il n'en a pas encore de vrais
			if (reglages != null && level.getBlockEntity(c) instanceof EmailBlockEntity e) {
				if (!reglages.vide() && (e.reglages == null || e.reglages.vide())) { e.reglages = reglages; e.valeurs.clear(); e.valeurs.addAll(valeurs); e.marquer(); }
				reglages = null; valeurs.clear(); change = true;
			}
		}
		if (change) marquer();
	}
	/** Tous les blocs du tableau (contrôleur seulement). */
	public List<BlockPos> membres() {
		List<BlockPos> l = new ArrayList<>(); Direction d = droite(face());
		for (int j = 0; j < hauteur; j++) for (int i = 0; i < largeur; i++) l.add(worldPosition.below(j).relative(d, i));
		return l;
	}
	@Override
	public AABB getRenderBoundingBox() {
		Direction d = droite(face());
		BlockPos b = worldPosition.below(hauteur - 1).relative(d, largeur - 1);
		return new AABB(worldPosition).minmax(new AABB(b)).inflate(1);
	}

	// ---------------------------------------------------------------- vie du tableau
	void marquer() { setChanged(); aSynchroniser = true; }
	public void tick() {
		if (level == null || level.isClientSide) return;
		if ((level.getGameTime() + worldPosition.asLong()) % 10 == 0) {
			resoudre();
			if (estControleur()) etat();
		}
		if (aSynchroniser) { aSynchroniser = false; sendData(); }
	}
	/** Accrochage choisi (ou deviné), alerte, signal de redstone, lumière : appliqués à tous les blocs. */
	private void etat() {
		Reglages r = reglages;
		List<BlockPos> m = membres();
		boolean signal = false;
		for (BlockPos p : m) if (level.hasNeighborSignal(p)) { signal = true; break; }
		boolean a = false;
		if (r.alerteLigne > 0 && r.alerteLigne <= r.avant.size()) {
			Double v = Reglages.mesure(valeur(r.alerteLigne - 1));
			a = v != null && v > r.seuil;
		}
		boolean al = r.eclairage != 0 && (r.allumage == 0 || (r.allumage == 1 && signal) || (r.allumage == 2 && a));
		if (a != alerte || al != allume) { alerte = a; allume = al; marquer(); }
		EmailBlock.Montage mo = montage();
		int lum = allume || (alerte && r.alerteAction == 1) ? Math.max(r.intensite, alerte ? 7 : 0) : 0;
		for (BlockPos p : m) {
			BlockState s = level.getBlockState(p);
			if (!(s.getBlock() instanceof EmailBlock)) continue;
			BlockState n = s.setValue(EmailBlock.MONTAGE, mo).setValue(EmailBlock.LUMIERE, lum);
			if (n != s) level.setBlock(p, n, Block.UPDATE_CLIENTS);
		}
	}
	private EmailBlock.Montage montage() {
		int c = reglages.accrochage;
		if (c > 0) return EmailBlock.Montage.values()[c - 1];
		Direction f = face(), d = droite(f);
		for (BlockPos p : membres()) {           // un mur derrière : au mur
			BlockPos q = p.relative(f.getOpposite());
			if (level.getBlockState(q).isFaceSturdy(level, q, f)) return EmailBlock.Montage.MUR;
		}
		for (int i = 0; i < largeur; i++) if (!level.getBlockState(worldPosition.above().relative(d, i)).isAir()) return EmailBlock.Montage.PENDU;
		for (int i = 0; i < largeur; i++) if (!level.getBlockState(worldPosition.below(hauteur).relative(d, i)).isAir()) return EmailBlock.Montage.PIED;
		return EmailBlock.Montage.MUR;
	}
	/** Le bloc s'en va : ses réglages passent à un voisin du même tableau. */
	void confier() {
		if (reglages == null || !estControleur() || largeur * hauteur < 2) return;
		for (BlockPos p : membres()) {
			if (p.equals(worldPosition)) continue;
			if (level.getBlockEntity(p) instanceof EmailBlockEntity e) { e.reglages = reglages; e.valeurs.clear(); e.valeurs.addAll(valeurs); e.ctl = p; e.marquer(); return; }
		}
	}

	// ---------------------------------------------------------------- reçu du menu et des liaisons d'affichage
	public void appliquer(Reglages r) {
		// un nombre de lignes de liste changé : les valeurs déjà reçues sont oubliées, les liaisons les renvoient
		if (reglages != null && !nombres(reglages).equals(nombres(r))) valeurs.clear();
		reglages = r; marquer();
		etat();
	}
	private static java.util.List<Integer> nombres(Reglages r) {
		java.util.List<Integer> n = new java.util.ArrayList<>();
		for (int i = 0; r.liable(i) != null; i++) n.add(r.liable(i).nb);
		return n;
	}
	/** Les valeurs reçues sont oubliées (une liaison a changé de ligne) : les liaisons les renvoient à leur prochain passage. */
	void oublierValeurs() { valeurs.clear(); marquer(); }
	/** Une liaison d'affichage écrit sur la ligne i (face avant, puis face arrière si elle est différente). */
	public void recevoir(int i, String v) {
		if (i < 0 || i >= 2 * Reglages.MAX_LIGNES) return;
		while (valeurs.size() <= i) valeurs.add("");
		if (!valeurs.get(i).equals(v)) { valeurs.set(i, v); marquer(); }
	}
	public int lignesLiables() {
		if (reglages == null) return 1;
		return Math.max(1, reglages.avant.size() + (reglages.memeFace ? 0 : reglages.arriere.size()));
	}
	/** Le texte d'une ligne pour l'écran de la liaison : « Ligne 3 · Stress ». */
	public String nomLigne(int i) {
		if (reglages == null) return "";
		List<Reglages.Ligne> l = i < reglages.avant.size() ? reglages.avant : reglages.arriere;
		int k = i < reglages.avant.size() ? i : i - reglages.avant.size();
		return k < l.size() ? l.get(k).texte : "";
	}

	// ---------------------------------------------------------------- sauvegarde et synchro
	@Override
	protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.write(t, r, client);
		if (reglages != null) t.put("reglages", reglages.ecrire());
		ListTag v = new ListTag(); for (String s : valeurs) v.add(StringTag.valueOf(s)); t.put("valeurs", v);
		if (ctl != null) t.putLong("ctl", ctl.asLong());
		t.putByte("w", (byte) largeur); t.putByte("h", (byte) hauteur);
		if (client) { t.putBoolean("alerte", alerte); t.putBoolean("allume", allume); }
		ListTag a = new ListTag();
		for (var e : attributions.entrySet()) { CompoundTag c = new CompoundTag(); c.putLong("p", e.getKey().asLong()); c.putInt("l", e.getValue()); a.add(c); }
		t.put("liaisons", a);
	}
	@Override
	protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
		super.read(t, r, client);
		reglages = t.contains("reglages") ? Reglages.lire(t.getCompound("reglages")) : null;
		valeurs.clear(); for (Tag x : t.getList("valeurs", Tag.TAG_STRING)) valeurs.add(x.getAsString());
		ctl = t.contains("ctl") ? BlockPos.of(t.getLong("ctl")) : null;
		largeur = Math.max(1, t.getByte("w")); hauteur = Math.max(1, t.getByte("h"));
		if (client) { alerte = t.getBoolean("alerte"); allume = t.getBoolean("allume"); }
		attributions.clear();
		for (Tag x : t.getList("liaisons", Tag.TAG_COMPOUND)) { CompoundTag c = (CompoundTag) x; attributions.put(BlockPos.of(c.getLong("p")), c.getInt("l")); }
	}

	// ---------------------------------------------------------------- presse-papiers de Create : copier tous les réglages
	@Override public String getClipboardKey() { return "airain_enamel_board"; }
	@Override
	public boolean writeToClipboard(@NotNull HolderLookup.Provider r, CompoundTag tag, Direction side) {
		EmailBlockEntity c = level.getBlockEntity(controleur()) instanceof EmailBlockEntity e ? e : this;
		if (c.reglages == null) return false;
		tag.put("reglages", c.reglages.ecrire()); return true;
	}
	@Override
	public boolean readFromClipboard(@NotNull HolderLookup.Provider r, CompoundTag tag, Player p, Direction side, boolean simuler) {
		if (!tag.contains("reglages")) return false;
		if (simuler) return true;
		EmailBlockEntity c = level.getBlockEntity(controleur()) instanceof EmailBlockEntity e ? e : this;
		c.appliquer(Reglages.lire(tag.getCompound("reglages")));
		return true;
	}

	static EmailBlockEntity de(BlockEntity be) {
		if (!(be instanceof EmailBlockEntity e) || e.level == null) return null;
		return e.level.getBlockEntity(e.controleur()) instanceof EmailBlockEntity c ? c : e;
	}
}
