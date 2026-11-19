package fr.chatmort.airain.affichage;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import com.simibubi.create.content.redstone.displayLink.DisplayLinkBlockEntity;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;

/**
 * Les liaisons d'affichage de Create visées sur un tableau émaillé, et leur répartition par ligne depuis le menu du tableau.
 * Une ligne ne reçoit qu'une liaison : en donner une à une ligne déjà prise met l'ancienne de côté (aucune ligne).
 */
public final class Liaisons {
	/** Portée de recherche (celle des liaisons de Create par défaut). */
	public static final int PORTEE = 64;
	/** Ligne « aucune » : hors du tableau, la liaison n'y écrit plus. */
	public static final int AUCUNE = 99;

	private Liaisons() {}

	/** Les liaisons chargées autour du tableau dont la cible fait partie de ce tableau (côté client comme serveur). */
	public static List<DisplayLinkBlockEntity> vers(Level l, BlockPos tableau) {
		List<DisplayLinkBlockEntity> r = new ArrayList<>();
		int c0 = (tableau.getX() - PORTEE) >> 4, c1 = (tableau.getX() + PORTEE) >> 4, d0 = (tableau.getZ() - PORTEE) >> 4, d1 = (tableau.getZ() + PORTEE) >> 4;
		for (int cx = c0; cx <= c1; cx++)
			for (int cz = d0; cz <= d1; cz++) {
				if (!l.hasChunk(cx, cz)) continue;
				for (var be : l.getChunk(cx, cz).getBlockEntities().values())
					if (be instanceof DisplayLinkBlockEntity d && vise(l, d, tableau)) r.add(d);
			}
		r.sort(Comparator.comparingLong(d -> d.getBlockPos().asLong()));
		return r;
	}

	static boolean vise(Level l, DisplayLinkBlockEntity d, BlockPos tableau) {
		EmailBlockEntity e = EmailBlockEntity.de(l.getBlockEntity(d.getTargetPosition()));
		return e != null && e.getBlockPos().equals(tableau);
	}

	/** La ligne est-elle attribuée à une autre liaison, toujours là et toujours visée sur ce tableau ? (sinon l'attribution est oubliée) */
	static boolean prise(EmailBlockEntity e, int ligne, BlockPos moi) {
		BlockPos autre = e.lienDe(ligne);
		if (autre == null || autre.equals(moi)) return false;
		if (e.getLevel() != null && e.getLevel().isLoaded(autre)
			&& !(e.getLevel().getBlockEntity(autre) instanceof DisplayLinkBlockEntity d && vise(e.getLevel(), d, e.getBlockPos()))) {
			e.attributions.remove(autre); e.marquer(); return false;
		}
		return true;
	}

	/** Serveur : la liaison en lien passe sur la ligne (ou sur aucune si ligne < 0) ; le tableau le retient. */
	static void affecter(Level l, EmailBlockEntity tableau, BlockPos lien, int ligne) {
		if (!(l.getBlockEntity(lien) instanceof DisplayLinkBlockEntity d) || !vise(l, d, tableau.getBlockPos())) return;
		int cible = ligne < 0 || ligne >= tableau.lignesLiables() ? -1 : ligne;
		if (cible >= 0) {
			BlockPos ancien = tableau.lienDe(cible);
			if (ancien != null && !ancien.equals(lien)) {
				tableau.attributions.put(ancien, -1);
				if (l.getBlockEntity(ancien) instanceof DisplayLinkBlockEntity a) poser(a, AUCUNE);
			}
		}
		tableau.attributions.put(lien, cible);
		poser(d, cible < 0 ? AUCUNE : cible);
		// réservations de lignes de Create (données du tableau) : effacées, chaque liaison reprend la sienne en écrivant
		CompoundTag t = tableau.getPersistentData();
		t.remove("DisplayLink");
		tableau.oublierValeurs();
		d.updateGatheredData();
	}

	private static void poser(DisplayLinkBlockEntity d, int ligne) {
		d.targetLine = ligne;
		d.notifyUpdate();
	}
}
