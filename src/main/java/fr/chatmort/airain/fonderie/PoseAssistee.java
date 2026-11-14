package fr.chatmort.airain.fonderie;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

/**
 * Pose assistée des passerelles : clic droit sur le bord (ou le côté) d'une pièce de passerelle avec une pièce de passerelle
 * en main → la nouvelle pièce se pose de l'autre côté, au bon niveau et dans le bon sens, même dans le vide.
 *  - passerelle : même niveau (basse ou haute) ; au bout d'un escalier ou d'une rampe, au niveau d'arrivée ;
 *  - escalier, rampe : ils montent en s'éloignant ; accroupi, ils descendent ;
 *  - escalier à palier : il monte en s'éloignant, virage à droite (accroupi : à gauche) ;
 *  - pièces-mécanismes : comme une passerelle, tournées vers le vide.
 * Sur le dessus d'une pièce (loin des bords), la pose normale reste possible.
 */
public final class PoseAssistee {
	private PoseAssistee() {}

	private static boolean piece(Block b) {
		return b instanceof Passerelle.Plancher || b instanceof Passerelle.Escalier || b instanceof Passerelle.Rampe || b instanceof Passerelle.Palier;
	}

	public static void clic(PlayerInteractEvent.RightClickBlock e) {
		ItemStack st = e.getItemStack();
		if (!(st.getItem() instanceof BlockItem bi) || !piece(bi.getBlock())) return;
		Level l = e.getLevel(); Player j = e.getEntity();
		BlockPos p = e.getPos(); BlockState source = l.getBlockState(p);
		if (!piece(source.getBlock()) || source.getBlock() instanceof Passerelle.Plancher pl && source.getValue(Passerelle.RENTRE)) return;
		BlockHitResult hit = e.getHitVec();
		Direction face = hit.getDirection();
		double x = hit.getLocation().x - p.getX(), z = hit.getLocation().z - p.getZ();
		double bord = Math.min(Math.min(x, 1 - x), Math.min(z, 1 - z));
		if (face.getAxis().isVertical() && bord > 0.25) return;                    // sur le dessus : pose normale
		Direction d = face.getAxis().isHorizontal() ? face : Passerelle.coteVise(p, hit.getLocation());
		int niveau = Passerelle.niveauFace(source, d);
		if (niveau < 0) return;                                                     // flanc d'escalier : rien à prolonger
		BlockPos q = niveau == 19 ? p.relative(d).above() : p.relative(d);
		int n = niveau == 19 ? 3 : niveau;                                          // niveau du plancher à rejoindre dans q
		boolean bas = j.isShiftKeyDown();
		Block b = bi.getBlock();
		BlockState s = null;
		if (b instanceof PasserelleMobile) s = Passerelle.Plancher.cotes(b.defaultBlockState().setValue(Passerelle.HAUT, n == 11), l, q);
		else if (b instanceof Passerelle.Plancher) s = Passerelle.Plancher.cotes(b.defaultBlockState().setValue(Passerelle.HAUT, n == 11), l, q);
		else if (b instanceof Passerelle.Escalier) {
			if (n != 3) return;
			if (bas) { q = q.below(); s = b.defaultBlockState().setValue(Passerelle.FACING, d.getOpposite()); }
			else s = b.defaultBlockState().setValue(Passerelle.FACING, d);
			s = Passerelle.cotesMontee(s, l, q);
		} else if (b instanceof Passerelle.Rampe) {
			if (!bas) s = b.defaultBlockState().setValue(Passerelle.FACING, d).setValue(Passerelle.HAUT, n == 11);
			else if (n == 11) s = b.defaultBlockState().setValue(Passerelle.FACING, d.getOpposite()).setValue(Passerelle.HAUT, false);
			else { q = q.below(); s = b.defaultBlockState().setValue(Passerelle.FACING, d.getOpposite()).setValue(Passerelle.HAUT, true); }
			s = Passerelle.cotesMontee(s, l, q);
		} else if (b instanceof Passerelle.Palier) {
			if (n != 3) return;
			s = Passerelle.Palier.cotes(b.defaultBlockState().setValue(Passerelle.FACING, d).setValue(Passerelle.A_GAUCHE, bas), l, q);
		}
		if (s == null || !l.getBlockState(q).canBeReplaced() || !l.isUnobstructed(s, q, CollisionContext.of(j))) return;
		e.setCanceled(true);
		e.setCancellationResult(InteractionResult.sidedSuccess(l.isClientSide));
		if (l.isClientSide) return;
		l.setBlock(q, s, Block.UPDATE_ALL);
		b.setPlacedBy(l, q, s, j, st);
		// pièce-mécanisme : tournée dans le prolongement, vers l'extérieur
		if (l.getBlockEntity(q) instanceof PasserelleMobile.Mecanisme m) m.orienter(d);
		SoundType son = s.getSoundType(l, q, j);
		l.playSound(null, q, son.getPlaceSound(), SoundSource.BLOCKS, (son.getVolume() + 1f) / 2f, son.getPitch() * 0.8f);
		if (!j.getAbilities().instabuild) st.shrink(1);
	}
}
