package fr.chatmort.airain.balise;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Formes de collision de chaque case de la tour (3 x 8 x 3), lues dans BaliseGeo.CASES. */
final class BaliseFormes {
	private static final VoxelShape[] FORMES = new VoxelShape[3 * 8 * 3];
	static {
		for (float[] c : BaliseGeo.CASES) {
			VoxelShape s = Shapes.empty();
			for (int i = 3; i + 5 < c.length; i += 6)
				s = Shapes.or(s, Block.box(c[i], c[i + 1], c[i + 2], c[i + 3], c[i + 4], c[i + 5]));
			FORMES[indice((int) c[0], (int) c[1], (int) c[2])] = s.optimize();
		}
	}

	private BaliseFormes() {}

	static int indice(int x, int y, int z) { return (y * 3 + z) * 3 + x; }

	/** null si la case est vide (rien n'y est posé). */
	static VoxelShape de(int x, int y, int z) {
		if (x < 0 || x > 2 || y < 0 || y > 7 || z < 0 || z > 2) return null;
		return FORMES[indice(x, y, z)];
	}
}
