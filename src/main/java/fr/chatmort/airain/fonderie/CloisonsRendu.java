package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 1.63 : le vantail du portail coulissant. Chaque bloc dessine sa part (grillage, bandeaux du cadre aux bords du vantail,
 * traverse, poignée côté ouverture) et glisse de toute la largeur du vantail, le long de la cloison.
 */
public class CloisonsRendu implements BlockEntityRenderer<Cloisons.PortailBE> {
	private static final String[] STADES = {"", "exposed_", "weathered_", "oxidized_"};
	public CloisonsRendu(BlockEntityRendererProvider.Context c) {}
	private static TextureAtlasSprite sprite(String n) { return Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(ResourceLocation.fromNamespaceAndPath("airain", "block/" + n)); }
	private static boolean meme(Level l, BlockPos q, Direction.Axis a) { BlockState s = l.getBlockState(q); return s.getBlock() instanceof Cloisons.Portail && s.getValue(Cloisons.AXE) == a; }

	@Override
	public void render(Cloisons.PortailBE be, float pt, PoseStack ms, MultiBufferSource buf, int lum, int ov) {
		Level l = be.getLevel(); if (l == null) return;
		BlockState s = be.getBlockState();
		if (!(s.getBlock() instanceof Cloisons.Portail g)) return;
		Direction.Axis a = s.getValue(Cloisons.AXE);
		BlockPos p = be.getBlockPos();
		boolean pos = s.getValue(Cloisons.SENS);
		// largeur du vantail le long de l'axe (rangée de ce bloc)
		int avant = 0, apres = 0;
		while (avant < 16 && meme(l, p.relative(a, -(avant + 1)), a)) avant++;
		while (apres < 16 && meme(l, p.relative(a, apres + 1), a)) apres++;
		int largeur = avant + apres + 1;
		float t = Mth.lerp(pt, be.avant, be.avance); t = t * t * (3 - 2 * t);
		float dec = t * largeur * 16 * (pos ? 1 : -1);
		boolean bordNeg = avant == 0, bordPos = apres == 0, haut = !meme(l, p.above(), a), bas = !meme(l, p.below(), a);
		boolean poignee = (pos ? bordNeg : bordPos) && bas;
		String pre = STADES[g.stade];
		TextureAtlasSprite gr = sprite(pre + "airain_grate"), bd = sprite(pre + "airain_band"), ci = sprite(pre + "chiseled_airain");
		VertexConsumer vc = buf.getBuffer(RenderType.cutout());
		ms.pushPose();
		if (a == Direction.Axis.Z) { ms.translate(0.5, 0, 0.5); ms.mulPose(com.mojang.math.Axis.YP.rotationDegrees(90)); ms.translate(-0.5, 0, -0.5); }
		ms.scale(1 / 16f, 1 / 16f, 1 / 16f);
		ms.translate(a == Direction.Axis.Z ? -dec : dec, 0, 0);
		// dessiné le long de x, vantail à z 9..11 (contre la cloison, du côté sud)
		boite(ms, vc, gr, 0, 0, 9.75f, 16, 16, 10.25f, lum);
		if (haut) boite(ms, vc, bd, 0, 14.5f, 9.4f, 16, 16, 10.6f, lum);
		if (bas) boite(ms, vc, bd, 0, 0, 9.4f, 16, 1.5f, 10.6f, lum);
		boite(ms, vc, bd, 0, 7.4f, 9.5f, 16, 8.6f, 10.5f, lum);
		// en z, le repère tourné inverse le sens de l'axe
		boolean z = a == Direction.Axis.Z;
		if (z ? bordPos : bordNeg) boite(ms, vc, bd, 0, 0, 9.3f, 1.5f, 16, 10.7f, lum);
		if (z ? bordNeg : bordPos) boite(ms, vc, bd, 14.5f, 0, 9.3f, 16, 16, 10.7f, lum);
		if (poignee) { float x = (z ? !pos : pos) ? 1.8f : 12.2f; boite(ms, vc, ci, x, 9.5f, 8.6f, x + 2, 13.5f, 11.4f, lum); }
		ms.popPose();
	}
	@Override public boolean shouldRenderOffScreen(Cloisons.PortailBE be) { return true; }
	@Override public net.minecraft.world.phys.AABB getRenderBoundingBox(Cloisons.PortailBE be) { return be.getRenderBoundingBox(); }

	private static void boite(PoseStack ms, VertexConsumer vc, TextureAtlasSprite sp, float x0, float y0, float z0, float x1, float y1, float z1, int lum) {
		fr.chatmort.airain.stockage.CasierRendu.boite(ms, vc, sp, x0, y0, z0, x1, y1, z1, 0xFFFFFF, lum);
	}
}
