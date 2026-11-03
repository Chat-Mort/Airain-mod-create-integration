package fr.chatmort.airain.gardien;

import java.util.LinkedHashMap;
import java.util.Map;

/** Ornements des gardiens d'élite (générés par capitaine/integrer.py) : {x, y, z, w, h, d, tuile} dans le repère de la pièce porteuse. */
final class EliteGeo {
	private EliteGeo() {}
	static final Map<String, float[][]> PARTIES = new LinkedHashMap<>();
	static {
		PARTIES.put("cap_tete", new float[][] {{-4.5f, -13f, -6f, 9f, 1f, 0.5f, 0f}, {-4.5f, -13f, 2.5f, 9f, 1f, 0.5f, 0f}, {-4.5f, -13f, -5.5f, 0.5f, 1f, 8f, 1f}, {4f, -13f, -5.5f, 0.5f, 1f, 8f, 1f}, {-4.5f, -15f, -6f, 1f, 2f, 0.5f, 0f}, {-0.5f, -15f, -6f, 1f, 2f, 0.5f, 0f}, {3.5f, -15f, -6f, 1f, 2f, 0.5f, 0f}, {-4.5f, -15f, -1.5f, 1f, 2f, 1f, 0f}, {3.5f, -15f, -1.5f, 1f, 2f, 1f, 0f}, {-4.5f, -15f, 2f, 1f, 2f, 0.5f, 0f}, {-0.5f, -15f, 2f, 1f, 2f, 0.5f, 0f}, {3.5f, -15f, 2f, 1f, 2f, 0.5f, 0f}, {-0.5f, -16f, -1f, 1f, 1f, 1f, 2f}, {-0.25f, -16.6f, -0.4f, 1f, 1f, 1f, 2f}, {0f, -17.2f, 0.2f, 1f, 1f, 1f, 2f}, {0.25f, -17.8f, 0.8f, 1f, 1f, 1f, 2f}, {0.5f, -18.4f, 1.4f, 1f, 1f, 1f, 2f}, {0.75f, -19f, 2f, 1f, 1f, 1f, 2f}, {1f, -19.6f, 2.6f, 1f, 1f, 1f, 2f}, {1.25f, -20.2f, 3.2f, 1f, 1f, 1f, 2f}});
		PARTIES.put("cap_tete_lum", new float[][] {{-1f, -14.5f, -6.5f, 2f, 1.5f, 0.5f, 9f}});
		PARTIES.put("cap_brasD", new float[][] {{-14.5f, -4f, -4f, 6f, 1.5f, 8f, 0f}, {-14.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {-14f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {-13.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {-13f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {-12.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {-12f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {-11.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {-11f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {-10.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {-10f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {-9.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {-9f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}});
		PARTIES.put("cap_brasG", new float[][] {{8.5f, -4f, -4f, 6f, 1.5f, 8f, 0f}, {8.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {9f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {9.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {10f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {10.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {11f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {11.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {12f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {12.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {13f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}, {13.5f, -2.5f, -4.5f, 0.5f, 1.5f, 0.5f, 2f}, {14f, -2.5f, -4.5f, 0.5f, 2.5f, 0.5f, 2f}});
		PARTIES.put("cap_corps", new float[][] {{-8f, -2f, 5f, 16f, 1f, 1.5f, 1f}, {-8.5f, -1f, 5.5f, 17f, 24f, 0.5f, 3f}});
		PARTIES.put("echo_corps", new float[][] {{-3.5f, 0f, -6.5f, 7f, 7f, 0.5f, 4f}, {-5f, -6.5f, 4f, 1.5f, 4.5f, 1.5f, 6f}, {-2f, -8.5f, 4f, 1.5f, 6.5f, 1.5f, 6f}, {1f, -7.5f, 4f, 1.5f, 5.5f, 1.5f, 6f}, {4f, -5.5f, 4f, 1.5f, 3.5f, 1.5f, 6f}});
		PARTIES.put("echo_corps_lum", new float[][] {{-2.6f, 0.9f, -6.7f, 5.2f, 5.2f, 0.2f, 7f}, {-1.6f, 1.9f, -6.8f, 3.2f, 3.2f, 0.2f, 8f}, {-5f, -8f, 4f, 1.5f, 1.5f, 1.5f, 7f}, {-2f, -10f, 4f, 1.5f, 1.5f, 1.5f, 7f}, {1f, -9f, 4f, 1.5f, 1.5f, 1.5f, 7f}, {4f, -7f, 4f, 1.5f, 1.5f, 1.5f, 7f}});
		PARTIES.put("echo_brasD", new float[][] {{-12.5f, -6.5f, -2f, 1.5f, 4f, 1.5f, 5f}, {-11f, -5f, 1f, 1.5f, 2.5f, 1.5f, 5f}, {-13f, -4f, 1.5f, 1.5f, 1.5f, 1.5f, 5f}});
		PARTIES.put("echo_brasD_lum", new float[][] {{-12.5f, -7.5f, -2f, 1.5f, 1f, 1.5f, 7f}, {-11f, -6f, 1f, 1.5f, 1f, 1.5f, 7f}, {-13f, -5f, 1.5f, 1.5f, 1f, 1.5f, 7f}});
		PARTIES.put("echo_brasG", new float[][] {{10.5f, -6.5f, -2f, 1.5f, 4f, 1.5f, 5f}, {12f, -5f, 1f, 1.5f, 2.5f, 1.5f, 5f}, {9.5f, -4f, 1.5f, 1.5f, 1.5f, 1.5f, 5f}});
		PARTIES.put("echo_brasG_lum", new float[][] {{10.5f, -7.5f, -2f, 1.5f, 1f, 1.5f, 7f}, {12f, -6f, 1f, 1.5f, 1f, 1.5f, 7f}, {9.5f, -5f, 1.5f, 1.5f, 1f, 1.5f, 7f}});
	}
}
