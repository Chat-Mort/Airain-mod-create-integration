package fr.chatmort.airain.stockage;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/**
 * Rendu du stock d'un casier : la palette, les blocs empilés en petits cubes ou les objets en caisses à claire-voie
 * (la hauteur suit le remplissage), et l'étiquette émaillée sur la lisse (icône, nom, quantité, renforts, réservation).
 * Repère : pixels de modèle, casier tourné vers le nord (face avant à z = 0).
 */
public class CasierRendu implements BlockEntityRenderer<CasierBlockEntity> {
	private final Font font;
	public CasierRendu(BlockEntityRendererProvider.Context c) { font = c.getFont(); }
	private static TextureAtlasSprite sprite(String ns, String nom) {
		return Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(ResourceLocation.fromNamespaceAndPath(ns, "block/" + nom));
	}

	@Override
	public void render(CasierBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int lum, int overlay) {
		ItemStack m = be.modele();
		if (m.isEmpty()) return;
		Vec3 cam = Minecraft.getInstance().gameRenderer.getMainCamera().getPosition();
		double dist = cam.distanceToSqr(Vec3.atCenterOf(be.getBlockPos()));
		ms.pushPose();
		ms.translate(0.5, 0, 0.5);
		ms.mulPose(Axis.YP.rotationDegrees(-(be.getBlockState().getValue(CasierBlock.FACING).toYRot() + 180)));
		ms.translate(-0.5, 0, -0.5);
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		VertexConsumer vc = buf.getBuffer(RenderType.cutout());
		TextureAtlasSprite bois = sprite("minecraft", "oak_planks"), caisse = sprite("minecraft", "spruce_planks"), email = sprite("airain", "enamel");
		// palette : trois traverses et le plateau
		for (float z : new float[] {2.8f, 7.3f, 11.8f}) boite(ms, vc, bois, 2, 2.5f, z, 14, 3.5f, z + 1.4f, 0xFFFFFF, lum);
		boite(ms, vc, bois, 2, 3.5f, 2.8f, 14, 4.2f, 13.2f, 0xFFFFFF, lum);
		float f = be.quantite() <= 0 ? 0 : Math.max(0.04f, (float) be.quantite() / be.capacite());
		if (dist < 48 * 48 && be.quantite() > 0) {
			var ir = Minecraft.getInstance().getItemRenderer();
			if (m.getItem() instanceof BlockItem) {           // blocs : petits cubes, 3 × 3 par couche, 2 couches
				int n = Math.max(1, Math.round(f * 18));
				for (int k = 0; k < n; k++) {
					int xx = k % 3, zz = (k / 3) % 3, ly = k / 9;
					ms.pushPose();
					ms.translate(2.4 + xx * 3.8 + 1.75, 4.2 + ly * 4.2 + 1.75, 3.2 + zz * 3.4 + 1.75);
					ms.scale(7f, 7f, 7f);
					ir.renderStatic(m, ItemDisplayContext.FIXED, lum, OverlayTexture.NO_OVERLAY, ms, buf, be.getLevel(), 0);
					ms.popPose();
				}
			} else {                                          // objets : caisses à claire-voie, l'objet peint devant
				int n = Math.max(1, Math.round(f * 6));
				for (int k = 0; k < n; k++) {
					int xx = k % 3, ly = k / 3;
					float x0 = 2.4f + xx * 3.8f, y0 = 4.2f + ly * 4.4f;
					boite(ms, vc, caisse, x0, y0, 3.2f, x0 + 3.6f, y0 + 4.2f, 13f, 0xFFFFFF, lum);
					ms.pushPose();
					ms.translate(x0 + 1.8, y0 + 2.1, 3.1);
					ms.mulPose(Axis.YP.rotationDegrees(180));
					ms.scale(6f, 6f, 0.6f);
					ir.renderStatic(m, ItemDisplayContext.FIXED, lum, OverlayTexture.NO_OVERLAY, ms, buf, be.getLevel(), 0);
					ms.popPose();
				}
			}
		}
		// étiquette émaillée sur la lisse avant
		boite(ms, vc, email, 2, 0.1f, -0.35f, 14, 3.4f, 0.05f, 0x1D1D21, lum);
		if (dist < 20 * 20) {
			var ir = Minecraft.getInstance().getItemRenderer();
			ms.pushPose();
			ms.translate(13.2, 1.75, -0.4);
			ms.mulPose(Axis.YP.rotationDegrees(180));
			ms.scale(5f, 5f, 0.3f);
			ir.renderStatic(m, ItemDisplayContext.FIXED, lum, OverlayTexture.NO_OVERLAY, ms, buf, be.getLevel(), 0);
			ms.popPose();
			ms.pushPose();
			ms.translate(11.6, 3.1, -0.38);
			ms.mulPose(Axis.YP.rotationDegrees(180));
			float s = 0.16f;
			ms.scale(s, -s, s);
			String nom = font.plainSubstrByWidth(m.getHoverName().getString(), 45);   // place pour le cadenas de réservation
			font.drawInBatch(Component.literal(nom), 0, 0, 0xFFECE4CE, false, ms.last().pose(), buf, Font.DisplayMode.POLYGON_OFFSET, 0, lum);
			ms.scale(1.35f, 1.35f, 1);
			font.drawInBatch(Component.literal(nombre(be.quantite())).withStyle(st -> st.withBold(true)), 0, 6.6f, 0xFFE8C46E, false, ms.last().pose(), buf, Font.DisplayMode.POLYGON_OFFSET, 0, lum);
			ms.popPose();
		}
		// barrettes des renforts, à droite de l'étiquette
		for (int k = 0; k < be.renforts(); k++) boite(ms, vc, email, 2.5f, 0.5f + k * 0.7f, -0.45f, 3.2f, 0.95f + k * 0.7f, -0.35f, k < 2 ? 0xE8C46E : k == 2 ? 0x8CBEF0 : 0xD64030, lum);
		// réservation : un petit cadenas (corps cramoisi, anse crème) à côté des barrettes, pour ne pas se confondre avec le renfort IV
		if (be.reserve()) {
			boite(ms, vc, email, 3.45f, 0.5f, -0.45f, 4.25f, 1.2f, -0.35f, 0xD64030, lum);
			boite(ms, vc, email, 3.55f, 1.2f, -0.45f, 3.7f, 1.65f, -0.35f, 0xECE4CE, lum);
			boite(ms, vc, email, 4.0f, 1.2f, -0.45f, 4.15f, 1.65f, -0.35f, 0xECE4CE, lum);
			boite(ms, vc, email, 3.55f, 1.65f, -0.45f, 4.15f, 1.8f, -0.35f, 0xECE4CE, lum);
		}
		ms.popPose();
	}
	/** 1 856, 2 048 : espaces fines entre les milliers. */
	static String nombre(long n) {
		String s = Long.toString(n); StringBuilder b = new StringBuilder();
		for (int i = 0; i < s.length(); i++) { if (i > 0 && (s.length() - i) % 3 == 0) b.append(' '); b.append(s.charAt(i)); }
		return b.toString();
	}
	@Override public int getViewDistance() { return 64; }

	/** Boîte texturée pixel pour pixel (uv à la position), teintée. */
	public static void boite(PoseStack ms, VertexConsumer vc, TextureAtlasSprite s, float x0, float y0, float z0, float x1, float y1, float z1, int col, int lum) {
		PoseStack.Pose p = ms.last();
		int r = (col >> 16) & 255, g = (col >> 8) & 255, b = col & 255;
		float[][][] f = {
			{{x0, y0, z0}, {x0, y1, z0}, {x1, y1, z0}, {x1, y0, z0}, {0, 0, -1}},   // avant (nord)
			{{x1, y0, z1}, {x1, y1, z1}, {x0, y1, z1}, {x0, y0, z1}, {0, 0, 1}},
			{{x0, y1, z0}, {x0, y1, z1}, {x1, y1, z1}, {x1, y1, z0}, {0, 1, 0}},
			{{x0, y0, z1}, {x0, y0, z0}, {x1, y0, z0}, {x1, y0, z1}, {0, -1, 0}},
			{{x0, y0, z1}, {x0, y1, z1}, {x0, y1, z0}, {x0, y0, z0}, {-1, 0, 0}},
			{{x1, y0, z0}, {x1, y1, z0}, {x1, y1, z1}, {x1, y0, z1}, {1, 0, 0}}};
		float[] ombre = {1f, 0.8f, 0.95f, 0.55f, 0.75f, 0.75f};
		for (int i = 0; i < 6; i++) {
			float[][] q = f[i]; float o = ombre[i];
			for (int k = 0; k < 4; k++) {
				float[] v = q[k];
				// uv à la position (dans le carreau du bloc)
				float u, w;
				if (i < 2) { u = v[0]; w = 16 - v[1]; } else if (i < 4) { u = v[0]; w = v[2]; } else { u = v[2]; w = 16 - v[1]; }
				u = Math.max(0, Math.min(16, u)); w = Math.max(0, Math.min(16, w));
				vc.addVertex(p, v[0], v[1], v[2]).setColor((int) (r * o), (int) (g * o), (int) (b * o), 255).setUv(s.getU(u / 16f), s.getV(w / 16f)).setLight(lum).setNormal(p, q[4][0], q[4][1], q[4][2]);
			}
		}
	}
}
