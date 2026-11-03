package fr.chatmort.airain.armure;

import java.util.Map;

/** Généré par armure/gen_arcanique.py : pièces ajoutées de l'armure arcanique (pixels, repère de la partie). */
final class ArcaniqueGeo {
	private ArcaniqueGeo() {}
	static final int[][] TUILES = {{64, 0}, {96, 0}, {64, 16}, {96, 16}, {64, 32}, {96, 32}, {64, 48}, {96, 48}};
	static final int[] PANS = {64, 64};
	static final Map<String, float[][]> PIECES = Map.of(
		"tete", new float[][] {
			{-1f, -10.2f, 2.6f, 2f, 1.4f, 2f, 3},
			{-0.5f, -11f, 3.4f, 1f, 1f, 1.4f, 2},
			{-5.2f, -9.2f, -5.4f, 10.4f, 0.8f, 0.6f, 0},
			{-5.2f, -9.2f, -5.4f, 0.6f, 9.4f, 0.6f, 0},
			{4.6f, -9.2f, -5.4f, 0.6f, 9.4f, 0.6f, 0},
			{-4f, -7.2f, -5.35f, 8f, 0.6f, 0.3f, 6},
			{-1f, -8.2f, -5.6f, 2f, 1.6f, 0.4f, 5},
			{-1.5f, -8.5f, -5.5f, 3f, 2.2f, 0.2f, 6}},
		"corps", new float[][] {
			{-4.6f, -1.6f, -3.3f, 3.4f, 2.4f, 0.6f, 0},
			{1.2f, -1.6f, -3.3f, 3.4f, 2.4f, 0.6f, 0},
			{-4.6f, -1.6f, 2.7f, 9.2f, 2.4f, 0.6f, 0},
			{-1f, 8.6f, -3.45f, 2f, 1.6f, 0.4f, 5}},
		"bras_d", new float[][] {
			{-4.4f, -3.4f, -3.6f, 6f, 2.6f, 7.2f, 0},
			{-4.5f, -1.1f, -3.7f, 6.2f, 0.5f, 7.4f, 1},
			{-1.9f, -3.6f, -3.7f, 1f, 0.3f, 7.4f, 4}},
		"bras_g", new float[][] {
			{-1.6f, -3.4f, -3.6f, 6f, 2.6f, 7.2f, 0},
			{-1.7f, -1.1f, -3.7f, 6.2f, 0.5f, 7.4f, 1},
			{0.9f, -3.6f, -3.7f, 1f, 0.3f, 7.4f, 4}},
		"pied_d", new float[][] {
			{-2.6f, 11f, -3.4f, 5.2f, 1.2f, 0.6f, 0}},
		"pied_g", new float[][] {
			{-2.6f, 11f, -3.4f, 5.2f, 1.2f, 0.6f, 0}}
	);
}
