package fr.chatmort.airain.fusion;

import com.hollingsworth.arsnouveau.api.source.ISourceTile;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;

/** Accès à la source d'Ars Nouveau (jarres de source et autres réserves) autour d'une machine. */
public final class Source {
	private Source() {}

	/** Prend jusqu'à {@code n} de source dans les réserves à {@code rayon} blocs ; renvoie ce qui a été pris. */
	public static int prendre(Level l, BlockPos centre, int rayon, int n) {
		int pris = 0;
		for (BlockPos p : BlockPos.betweenClosed(centre.offset(-rayon, -rayon, -rayon), centre.offset(rayon, rayon, rayon))) {
			if (pris >= n) break;
			if (l.getBlockEntity(p) instanceof ISourceTile t && t.getSource() > 0) pris += t.removeSource(Math.min(n - pris, t.getSource()));
		}
		return pris;
	}

	/** Ajoute jusqu'à {@code n} de source dans les réserves à {@code rayon} blocs ; renvoie ce qui a été versé. */
	public static int verser(Level l, BlockPos centre, int rayon, int n) {
		int verse = 0;
		for (BlockPos p : BlockPos.betweenClosed(centre.offset(-rayon, -rayon, -rayon), centre.offset(rayon, rayon, rayon))) {
			if (verse >= n) break;
			if (l.getBlockEntity(p) instanceof ISourceTile t && t.canAcceptSource()) {
				int place = t.getMaxSource() - t.getSource();
				if (place > 0) { int a = Math.min(place, n - verse); t.addSource(a); verse += a; }
			}
		}
		return verse;
	}
}
