package fr.chatmort.airain.enchant;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.BookModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/** Livre de laiton et de cuir vert qui flotte au-dessus de la table, comme celui de la table vanilla. */
public class TableEmpireRenderer implements BlockEntityRenderer<TableEmpireBlockEntity> {
	private static final ResourceLocation LIVRE = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/table_livre.png");
	private final BookModel livre;

	public TableEmpireRenderer(BlockEntityRendererProvider.Context ctx) {
		this.livre = new BookModel(ctx.bakeLayer(ModelLayers.BOOK));
	}

	@Override
	public void render(TableEmpireBlockEntity be, float pt, PoseStack ms, MultiBufferSource buffers, int light, int overlay) {
		ms.pushPose();
		ms.translate(0.5F, 0.75F, 0.5F);
		float t = be.temps + pt;
		ms.translate(0.0F, 0.1F + Mth.sin(t * 0.1F) * 0.01F, 0.0F);
		float d = Mth.wrapDegrees((be.tourne - be.oTourne) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		ms.mulPose(Axis.YP.rotation(-(be.oTourne + d * pt)));
		ms.mulPose(Axis.ZP.rotationDegrees(80.0F));
		float flip = Mth.lerp(pt, be.oFlip, be.flip);
		float g = Mth.frac(flip + 0.25F) * 1.6F - 0.3F;
		float h = Mth.frac(flip + 0.75F) * 1.6F - 0.3F;
		livre.setupAnim(t, Mth.clamp(g, 0.0F, 1.0F), Mth.clamp(h, 0.0F, 1.0F), Mth.lerp(pt, be.oOuvert, be.ouvert));
		livre.renderToBuffer(ms, buffers.getBuffer(RenderType.entitySolid(LIVRE)), light, overlay, -1);
		ms.popPose();
	}
}
