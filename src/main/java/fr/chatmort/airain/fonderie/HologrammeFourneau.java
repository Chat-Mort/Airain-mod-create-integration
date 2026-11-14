package fr.chatmort.airain.fonderie;

import com.simibubi.create.content.processing.burner.BlazeBurnerBlock;
import fr.chatmort.airain.fonderie.HautFourneauBlockEntity.Attendu;
import fr.chatmort.airain.fonderie.HautFourneauBlockEntity.Case;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * L'hologramme du haut-fourneau (1.55) : clic droit main nue sur le trou de coulée d'un fourneau incomplet, et les blocs
 * manquants apparaissent en fantôme à leur place (les mauvais blocs sont entourés de rouge). Pendant ce temps, un clic
 * droit avec le bon bloc en main le pose dans la case fantôme visée, même en l'air (pose assistée).
 *
 * L'état « hologramme allumé » est tenu des deux côtés (client et serveur), chacun dans sa table : les deux appliquent
 * les mêmes règles, à partir du même monde.
 */
public final class HologrammeFourneau {
	private HologrammeFourneau() {}

	/** 30 secondes. */
	public static final long DUREE = 600;
	private record Actif(BlockPos trou, long fin) {}
	private static final Map<UUID, Actif> SERVEUR = new ConcurrentHashMap<>(), CLIENT = new ConcurrentHashMap<>();
	private static Map<UUID, Actif> table(boolean client) { return client ? CLIENT : SERVEUR; }

	/** Allume (true) ou éteint (false) l'hologramme de ce fourneau pour ce joueur. */
	public static boolean basculer(Player j, BlockPos trou, boolean client) {
		Map<UUID, Actif> t = table(client);
		Actif a = t.get(j.getUUID());
		long now = j.level().getGameTime();
		if (a != null && a.trou().equals(trou) && a.fin() > now) { t.remove(j.getUUID()); return false; }
		t.put(j.getUUID(), new Actif(trou.immutable(), now + DUREE));
		return true;
	}
	/** Le fourneau dont l'hologramme est allumé pour ce joueur (null : aucun, expiré, ou fourneau monté). */
	public static HautFourneauBlockEntity actif(Player j) {
		Map<UUID, Actif> t = table(j.level().isClientSide);
		Actif a = t.get(j.getUUID());
		if (a == null) return null;
		if (a.fin() < j.level().getGameTime() || a.trou().distSqr(j.blockPosition()) > 64 * 64
			|| !(j.level().getBlockEntity(a.trou()) instanceof HautFourneauBlockEntity be) || be.forme()) { t.remove(j.getUUID()); return null; }
		return be;
	}

	// ------------------------------------------------------------------ ce que montre l'hologramme
	/** Une case de l'hologramme : le bloc fantôme à poser, ou (faux) un bloc à enlever ou à remplacer. */
	public record Fantome(BlockPos pos, BlockState etat, boolean faux) {}

	private static final ResourceLocation GRILLE = ResourceLocation.parse("airain:airain_grate");
	private static final ResourceLocation BRULEUR = ResourceLocation.parse("create:blaze_burner");
	private static boolean libre(BlockState s) { return s.isAir() || s.canBeReplaced(); }

	public static List<Fantome> fantomes(HautFourneauBlockEntity be) {
		List<Fantome> r = new ArrayList<>();
		Level l = be.getLevel();
		if (l == null) return r;
		Direction a = be.avant();
		// une tuyère au moins : si aucune n'est posée, la première place libre la montre (sinon une brique à remplacer)
		boolean uneTuyere = false; BlockPos placeTuyere = null, briqueTuyere = null;
		for (Case c : HautFourneauBlockEntity.PLAN) {
			if (c.quoi() != Attendu.TUYERE) continue;
			BlockState s = l.getBlockState(be.local(c.lx(), c.ly(), c.lz()));
			if (s.is(Fourneau.TUYERE.get())) uneTuyere = true;
			else if (libre(s) && placeTuyere == null) placeTuyere = be.local(c.lx(), c.ly(), c.lz());
			else if (s.is(Fourneau.BRIQUES.get()) && briqueTuyere == null) briqueTuyere = be.local(c.lx(), c.ly(), c.lz());
		}
		for (Case c : HautFourneauBlockEntity.PLAN) {
			BlockPos p = be.local(c.lx(), c.ly(), c.lz());
			BlockState s = l.getBlockState(p);
			if (c.quoi() == Attendu.TUYERE && !uneTuyere && p.equals(briqueTuyere) && placeTuyere == null) { r.add(new Fantome(p, s, true)); continue; }
			if (HautFourneauBlockEntity.conforme(c.quoi(), s)) continue;
			if (c.quoi() == Attendu.VIDE || !libre(s)) { r.add(new Fantome(p, s, true)); continue; }
			BlockState e = attendu(c, a, !uneTuyere && p.equals(placeTuyere));
			if (e != null) r.add(new Fantome(p, e, false));
		}
		// le brûleur à blaze sous la grille (il n'entre pas dans la structure, mais le fourneau en a besoin)
		BlockPos b = be.centre(0).below();
		BlockState bs = l.getBlockState(b);
		if (!(bs.getBlock() instanceof BlazeBurnerBlock)) {
			if (libre(bs)) r.add(new Fantome(b, BuiltInRegistries.BLOCK.get(BRULEUR).defaultBlockState(), false));
			else r.add(new Fantome(b, bs, true));
		}
		return r;
	}
	/** Le bloc qu'on montre (ou qu'on pose) dans une case vide. */
	private static BlockState attendu(Case c, Direction a, boolean tuyere) {
		return switch (c.quoi()) {
			case BRIQUE -> Fourneau.BRIQUES.get().defaultBlockState();
			case TUYERE -> tuyere ? Fourneau.TUYERE.get().defaultBlockState().setValue(FourneauBlocs.FACING, HautFourneauBlockEntity.dehors(a, c.lx(), c.ly(), c.lz()).get(0))
				: Fourneau.BRIQUES.get().defaultBlockState();
			case GRILLE -> BuiltInRegistries.BLOCK.get(GRILLE).defaultBlockState();
			case GUEULARD -> Fourneau.GUEULARD.get().defaultBlockState();
			default -> null;
		};
	}

	// ------------------------------------------------------------------ pose assistée
	/** Le bloc que ce bloc tenu en main poserait dans cette case (null : il n'y va pas). */
	private static BlockState pourCase(Case c, Direction a, Block b) {
		return switch (c.quoi()) {
			case BRIQUE -> b == Fourneau.BRIQUES.get() ? b.defaultBlockState() : null;
			case TUYERE -> b == Fourneau.BRIQUES.get() ? b.defaultBlockState()
				: b == Fourneau.TUYERE.get() ? b.defaultBlockState().setValue(FourneauBlocs.FACING, HautFourneauBlockEntity.dehors(a, c.lx(), c.ly(), c.lz()).get(0)) : null;
			case GRILLE -> HautFourneauBlockEntity.estGrille(b.defaultBlockState()) ? b.defaultBlockState() : null;
			case GUEULARD -> b == Fourneau.GUEULARD.get() ? b.defaultBlockState() : null;
			default -> null;
		};
	}
	/** Pose le bloc tenu dans la case fantôme visée. Vrai si quelque chose a été posé (ou le serait, côté client). */
	public static boolean poser(Player j, InteractionHand main) {
		HautFourneauBlockEntity be = actif(j);
		if (be == null) return false;
		ItemStack st = j.getItemInHand(main);
		if (!(st.getItem() instanceof BlockItem bi)) return false;
		Level l = j.level();
		Direction a = be.avant();
		Vec3 oeil = j.getEyePosition(), fin = oeil.add(j.getViewVector(1f).scale(j.blockInteractionRange()));
		BlockPos meilleur = null; BlockState etat = null; double d = Double.MAX_VALUE;
		for (Case c : HautFourneauBlockEntity.PLAN) {
			BlockPos p = be.local(c.lx(), c.ly(), c.lz());
			if (!libre(l.getBlockState(p))) continue;
			BlockState e = pourCase(c, a, bi.getBlock());
			if (e == null) continue;
			var touche = new AABB(p).clip(oeil, fin);
			if (touche.isPresent() && touche.get().distanceTo(oeil) < d) { d = touche.get().distanceTo(oeil); meilleur = p; etat = e; }
		}
		if (meilleur == null) return false;
		// un vrai bloc devant la case fantôme : c'est lui qu'on vise
		BlockHitResult vrai = l.clip(new ClipContext(oeil, fin, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, j));
		if (vrai.getType() == HitResult.Type.BLOCK && vrai.getLocation().distanceTo(oeil) < d - 1e-3) return false;
		if (!l.isClientSide) {
			l.setBlock(meilleur, etat, Block.UPDATE_ALL);
			SoundType son = etat.getSoundType(l, meilleur, j);
			l.playSound(null, meilleur, son.getPlaceSound(), SoundSource.BLOCKS, (son.getVolume() + 1f) / 2f, son.getPitch() * 0.8f);
			if (!j.getAbilities().instabuild) st.shrink(1);
		}
		return true;
	}

	// ------------------------------------------------------------------ événements (les deux côtés)
	public static void clicBloc(PlayerInteractEvent.RightClickBlock e) {
		if (poser(e.getEntity(), e.getHand())) { e.setCanceled(true); e.setCancellationResult(InteractionResult.sidedSuccess(e.getLevel().isClientSide)); }
	}
	public static void clicObjet(PlayerInteractEvent.RightClickItem e) {
		if (poser(e.getEntity(), e.getHand())) { e.setCanceled(true); e.setCancellationResult(InteractionResult.sidedSuccess(e.getLevel().isClientSide)); }
	}
}
