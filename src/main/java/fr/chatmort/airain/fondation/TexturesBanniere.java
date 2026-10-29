package fr.chatmort.airain.fondation;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.ResourceLocation;

/**
 * Côté client : compose la toile d'une bannière (fond, partition et seconde couleur, motif, ornements, usure)
 * en une seule texture 16x32, mise en cache par combinaison de réglages.
 */
public final class TexturesBanniere {
	private static final Map<Long, ResourceLocation> CACHE = new HashMap<>(), LUEURS = new HashMap<>();

	private TexturesBanniere() {}

	public static ResourceLocation de(Apparence a) {
		if (!CACHE.containsKey(a.cleToile())) composer(a, a.cleToile());
		return CACHE.get(a.cleToile());
	}

	/** Broderie lumineuse : seulement le motif et les ornements (rendus en pleine lumière). */
	public static ResourceLocation lueur(Apparence a) {
		if (!LUEURS.containsKey(a.cleToile())) composer(a, a.cleToile());
		return LUEURS.get(a.cleToile());
	}

	private static NativeImage lire(ResourceLocation rl) {
		try (InputStream in = Minecraft.getInstance().getResourceManager().open(rl)) {
			return NativeImage.read(in);
		} catch (Exception e) {
			return null;
		}
	}

	// NativeImage range ses pixels en ABGR
	private static int alpha(int p) { return p >>> 24; }
	private static int gris(int p) { return p & 255; }
	private static int abgr(int a, int r, int g, int b) { return a << 24 | b << 16 | g << 8 | r; }

	private static int teinter(int p, int c, int a) {
		int v = gris(p);
		return abgr(a, (c >> 16 & 255) * v / 255, (c >> 8 & 255) * v / 255, (c & 255) * v / 255);
	}

	/** La seconde couleur s'applique-t-elle à ce pixel ? */
	static boolean partition(int type, int x, int y) {
		return switch (type) {
			case 1 -> y >= 15;                                          // coupé
			case 2 -> x >= 8;                                           // parti
			case 3 -> y >= 15 + Math.abs(x - 7.5f) * 1.1f;              // chevron
			case 4 -> Math.abs(y - 5 - x * 1.3f) < 3.2f;                // bande
			case 5 -> x <= 3 || x >= 12 || y <= 6;                      // bordure
			default -> false;
		};
	}

	/** Bruit stable par pixel (même usure à chaque fois). */
	private static float bruit(int x, int y, int graine) {
		int h = x * 73856093 ^ y * 19349663 ^ graine * 83492791;
		h ^= h >>> 13; h *= 0x5bd1e995; h ^= h >>> 15;
		return (h & 0xFFFF) / 65535f;
	}

	private static void composer(Apparence a, long cle) {
		NativeImage out = new NativeImage(16, 32, true);
		NativeImage fond = lire(a.texFond()), orn = lire(a.texOrnement());
		NativeImage motif = a.texMotif() == null ? null : lire(a.texMotif());
		boolean[] brode = new boolean[16 * 32];
		int c1 = Apparence.FONDS[a.fond()], c2 = Apparence.FONDS[a.fond2()], co = Apparence.ORNEMENTS[a.ornement()], cm = a.teinteMotif();
		for (int y = 0; y < 32; y++)
			for (int x = 0; x < 16; x++) {
				int p = 0;
				if (fond != null && alpha(fond.getPixelRGBA(x, y)) > 0)
					p = teinter(fond.getPixelRGBA(x, y), partition(a.partition(), x, y) ? c2 : c1, 255);
				if (motif != null && alpha(motif.getPixelRGBA(x, y)) > 0) { p = teinter(motif.getPixelRGBA(x, y), cm, 255); brode[y * 16 + x] = true; }
				if (orn != null && alpha(orn.getPixelRGBA(x, y)) > 0) { p = teinter(orn.getPixelRGBA(x, y), co, 255); brode[y * 16 + x] = true; }
				out.setPixelRGBA(x, y, p);
			}
		if (a.etat() > 0) user(out, a.etat());
		for (NativeImage i : new NativeImage[] {fond, orn, motif}) if (i != null) i.close();
		NativeImage lueur = new NativeImage(16, 32, true);
		for (int y = 0; y < 32; y++)
			for (int x = 0; x < 16; x++)
				if (brode[y * 16 + x] && alpha(out.getPixelRGBA(x, y)) > 0) lueur.setPixelRGBA(x, y, out.getPixelRGBA(x, y));
		ResourceLocation rl = ResourceLocation.fromNamespaceAndPath("airain", "banniere/" + Long.toHexString(cle));
		ResourceLocation rl2 = ResourceLocation.fromNamespaceAndPath("airain", "banniere/lueur_" + Long.toHexString(cle));
		Minecraft.getInstance().getTextureManager().register(rl, new DynamicTexture(out));
		Minecraft.getInstance().getTextureManager().register(rl2, new DynamicTexture(lueur));
		CACHE.put(cle, rl);
		LUEURS.put(cle, rl2);
	}

	/** Usée : couleurs passées, bords effilochés. Déchirée : en plus, bas en lambeaux, trous et une déchirure. */
	private static void user(NativeImage im, int etat) {
		boolean dechiree = etat == 2;
		float pale = dechiree ? 0.42f : 0.28f;
		int[] bas = new int[16];
		for (int x = 0; x < 16; x++) {
			bas[x] = -1;
			for (int y = 31; y >= 0; y--) if (alpha(im.getPixelRGBA(x, y)) > 0) { bas[x] = y; break; }
		}
		for (int y = 0; y < 32; y++)
			for (int x = 0; x < 16; x++) {
				int p = im.getPixelRGBA(x, y);
				if (alpha(p) == 0) continue;
				int r = p & 255, g = p >> 8 & 255, b = p >> 16 & 255;
				int l = (r * 3 + g * 6 + b) / 10;
				float sombre = 1f - bruit(x, y, 7) * (dechiree ? 0.22f : 0.12f);   // taches
				r = (int) ((r + (l + 25 - r) * pale) * sombre); g = (int) ((g + (l + 22 - g) * pale) * sombre); b = (int) ((b + (l + 15 - b) * pale) * sombre);
				boolean bord = x == 0 || x == 15 || y >= bas[x] - (dechiree ? (int) (bruit(x, 0, 3) * 5) : 0);
				boolean retire = bord && y > 3 && bruit(x, y, 11) < (dechiree ? 0.75f : 0.35f);
				if (dechiree) {
					retire |= y > 3 && bruit(x, y, 29) < 0.035f;                                  // trous
					retire |= y > 6 && Math.abs(x - (13 - (y - 18) * 0.5f)) < 0.6f && y >= 18 && y <= 26;   // déchirure
				}
				im.setPixelRGBA(x, y, retire ? 0 : abgr(255, Math.min(255, r), Math.min(255, g), Math.min(255, b)));
			}
	}
}
