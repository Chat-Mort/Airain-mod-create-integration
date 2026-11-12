package fr.chatmort.airain.fusion;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.InventoryMenu;

/** L'Écho liquide dans la cuve du condenseur, à la hauteur de ce qu'elle contient vraiment (lumineux, comme la source). */
public class CondenseurRenderer implements BlockEntityRenderer<CondenseurBlockEntity> {
	private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("ars_nouveau", "block/source_still");
	// La cuve : de 2 à 14 en largeur, du dessus du socle (3) au plafond (14), en seizièmes de bloc
	private static final float BAS = 3 / 16f, HAUT = 14 / 16f, MIN = 2 / 16f, MAX = 14 / 16f;

	public CondenseurRenderer(BlockEntityRendererProvider.Context c) { }

	@Override
	public void render(CondenseurBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
		float plein = be.niveauClient();
		if (plein <= 0.001f) return;
		float y = BAS + (HAUT - BAS) * Math.min(1f, plein);
		TextureAtlasSprite s = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(TEXTURE);
		VertexConsumer v = buf.getBuffer(RenderType.solid());
		PoseStack.Pose p = ms.last();
		int l = LightTexture.FULL_BRIGHT;
		// le dessus, puis les quatre côtés (la texture n'est pas écrasée : elle est coupée à la hauteur du liquide)
		quad(v, p, s, l, MIN, y, MAX, MAX, y, MAX, MAX, y, MIN, MIN, y, MIN, 0, 1, 0, MIN, MIN, MAX, MAX);
		float h = (y - BAS);
		quad(v, p, s, l, MIN, BAS, MIN, MIN, y, MIN, MAX, y, MIN, MAX, BAS, MIN, 0, 0, -1, 0, 1 - h, MAX - MIN, 1);
		quad(v, p, s, l, MAX, BAS, MAX, MAX, y, MAX, MIN, y, MAX, MIN, BAS, MAX, 0, 0, 1, 0, 1 - h, MAX - MIN, 1);
		quad(v, p, s, l, MIN, BAS, MAX, MIN, y, MAX, MIN, y, MIN, MIN, BAS, MIN, -1, 0, 0, 0, 1 - h, MAX - MIN, 1);
		quad(v, p, s, l, MAX, BAS, MIN, MAX, y, MIN, MAX, y, MAX, MAX, BAS, MAX, 1, 0, 0, 0, 1 - h, MAX - MIN, 1);
	}

	/** Un quadrilatère ; u0..u1 / v0..v1 sont des fractions de la texture (0 à 1). */
	private static void quad(VertexConsumer v, PoseStack.Pose p, TextureAtlasSprite s, int l,
							 float x1, float y1, float z1, float x2, float y2, float z2, float x3, float y3, float z3, float x4, float y4, float z4,
							 float nx, float ny, float nz, float u0, float v0, float u1, float v1) {
		float a0 = s.getU(u0), a1 = s.getU(u1), b0 = s.getV(v0), b1 = s.getV(v1);
		v.addVertex(p, x1, y1, z1).setColor(255, 255, 255, 255).setUv(a0, b1).setLight(l).setNormal(p, nx, ny, nz);
		v.addVertex(p, x2, y2, z2).setColor(255, 255, 255, 255).setUv(a0, b0).setLight(l).setNormal(p, nx, ny, nz);
		v.addVertex(p, x3, y3, z3).setColor(255, 255, 255, 255).setUv(a1, b0).setLight(l).setNormal(p, nx, ny, nz);
		v.addVertex(p, x4, y4, z4).setColor(255, 255, 255, 255).setUv(a1, b1).setLight(l).setNormal(p, nx, ny, nz);
	}
}
