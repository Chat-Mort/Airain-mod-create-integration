package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;
import fr.chatmort.airain.AirainPartials;
import net.createmod.catnip.render.CachedBuffers;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/** Rendus du téléphérique (gare et sa poulie, câbles, nacelle) et du laminoir. Côté client seulement. */
public final class TelepheriqueRendus {
	private TelepheriqueRendus() {}

	// ------------------------------------------------------------------ câbles
	private static final ResourceLocation TEX_CABLE = ResourceLocation.fromNamespaceAndPath("airain", "block/airain_cable_strand");
	/**
	 * Dessine la travée qui part du nœud p vers son suivant : deux brins (de part et d'autre de l'axe), avec leur affaissement,
	 * en petits tubes texturés. Le PoseStack est au coin du bloc p.
	 */
	static void travee(Level l, BlockPos p, Telepherique.Noeud n, PoseStack ms, MultiBufferSource buf) {
		if (n.suivant() == null) return;
		Telepherique.Noeud m = Telepherique.noeud(l, n.suivant());
		Vec3 a = Telepherique.centre(l, p), b = m != null ? Telepherique.centre(l, n.suivant()) : Vec3.atBottomCenterOf(n.suivant()).add(0, 1, 0);
		Vec3 avant = n.precedent() != null ? Telepherique.centre(l, n.precedent()) : null;
		Vec3 apres = m != null && m.suivant() != null ? Telepherique.centre(l, m.suivant()) : null;
		Vec3 da = Telepherique.droite(avant, a, b), db = Telepherique.droite(a, b, apres);
		TextureAtlasSprite sp = Minecraft.getInstance().getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(TEX_CABLE);
		VertexConsumer vc = buf.getBuffer(RenderType.cutout());
		Vec3 o = Vec3.atLowerCornerOf(p);
		for (double cote : new double[]{Telepherique.BRIN, -Telepherique.BRIN}) {
			Vec3 a1 = a.add(da.scale(cote)), b1 = b.add(db.scale(cote));
			int n_ = Math.max(8, (int) (a1.distanceTo(b1) / 1.2));
			Vec3 prec = Telepherique.chainette(a1, b1, 0);
			for (int k = 1; k <= n_; k++) {
				Vec3 c = Telepherique.chainette(a1, b1, k / (double) n_);
				int lum = LevelRenderer.getLightColor(l, BlockPos.containing(prec.add(c).scale(0.5)));
				tube(ms, vc, sp, prec.subtract(o), c.subtract(o), 0.045f, lum);
				prec = c;
			}
		}
	}
	/** Un tube carré de demi-épaisseur r entre u et v. */
	private static void tube(PoseStack ms, VertexConsumer vc, TextureAtlasSprite sp, Vec3 u, Vec3 v, float r, int lum) {
		Vec3 d = v.subtract(u).normalize();
		Vec3 x = d.cross(new Vec3(0, 1, 0)); if (x.lengthSqr() < 1e-6) x = new Vec3(1, 0, 0); x = x.normalize().scale(r);
		Vec3 y = d.cross(x).normalize().scale(r);
		Vec3[] c = {x.add(y), x.subtract(y), x.scale(-1).subtract(y), x.scale(-1).add(y)};
		float u0 = sp.getU(7 / 16f), u1 = sp.getU(9 / 16f), v0 = sp.getV(0), v1 = sp.getV((float) Math.min(1, u.distanceTo(v)));
		PoseStack.Pose pz = ms.last();
		for (int i = 0; i < 4; i++) {
			Vec3 p0 = c[i], p1 = c[(i + 1) % 4];
			Vec3 nrm = p0.add(p1).normalize();
			sommet(vc, pz, u.add(p0), u0, v0, lum, nrm); sommet(vc, pz, u.add(p1), u1, v0, lum, nrm);
			sommet(vc, pz, v.add(p1), u1, v1, lum, nrm); sommet(vc, pz, v.add(p0), u0, v1, lum, nrm);
		}
	}
	private static void sommet(VertexConsumer vc, PoseStack.Pose p, Vec3 q, float u, float v, int lum, Vec3 n) {
		vc.addVertex(p, (float) q.x, (float) q.y, (float) q.z).setColor(255, 255, 255, 255).setUv(u, v).setLight(lum).setNormal(p, (float) n.x, (float) n.y, (float) n.z);
	}

	// ------------------------------------------------------------------ gare : demi-arbre sous le socle, poulie, câbles
	public static class GareRendu extends KineticBlockEntityRenderer<Telepherique.GareBlockEntity> {
		public GareRendu(BlockEntityRendererProvider.Context c) { super(c); }
		@Override
		protected void renderSafe(Telepherique.GareBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			BlockState s = be.getBlockState();
			renderRotatingBuffer(be, CachedBuffers.partialFacing(AllPartialModels.SHAFT_HALF, s, Direction.DOWN), ms, buf.getBuffer(RenderType.solid()), light);
			int haut = be.getLevel() != null ? LevelRenderer.getLightColor(be.getLevel(), be.getBlockPos().above()) : light;
			float ang = Mth.lerp(pt, be.angleAvant, be.angle);
			ms.pushPose();
			ms.translate(0.5, 1, 0.5); ms.mulPose(Axis.YP.rotationDegrees(ang)); ms.translate(-0.5, 0, -0.5);
			CachedBuffers.partial(AirainPartials.POULIE, s).light(haut).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
			if (be.getLevel() != null) travee(be.getLevel(), be.getBlockPos(), be, ms, buf);
		}
		@Override public boolean shouldRenderOffScreen(Telepherique.GareBlockEntity be) { return true; }
		@Override public int getViewDistance() { return 160; }
	}
	public static class TeteRendu implements BlockEntityRenderer<Telepherique.TeteBlockEntity> {
		public TeteRendu(BlockEntityRendererProvider.Context c) {}
		@Override
		public void render(Telepherique.TeteBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			if (be.getLevel() != null) travee(be.getLevel(), be.getBlockPos(), be, ms, buf);
		}
		@Override public boolean shouldRenderOffScreen(Telepherique.TeteBlockEntity be) { return true; }
		@Override public net.minecraft.world.phys.AABB getRenderBoundingBox(Telepherique.TeteBlockEntity be) { return new net.minecraft.world.phys.AABB(be.getBlockPos()).inflate(Telepherique.PORTEE + 4); }
		@Override public int getViewDistance() { return 160; }
	}

	// ------------------------------------------------------------------ laminoir : arbre traversant, rouleaux, lingot et fil
	public static class LaminoirRendu extends KineticBlockEntityRenderer<Telepherique.LaminoirBlockEntity> {
		public LaminoirRendu(BlockEntityRendererProvider.Context c) { super(c); }
		@Override
		protected void renderSafe(Telepherique.LaminoirBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			BlockState s = be.getBlockState();
			Direction f = s.getValue(Telepherique.Laminoir.HORIZONTAL_FACING);
			Direction.Axis ax = f.getClockWise().getAxis();
			renderRotatingBuffer(be, CachedBuffers.block(KineticBlockEntityRenderer.KINETIC_BLOCK, KineticBlockEntityRenderer.shaft(ax)), ms, buf.getBuffer(RenderType.solid()), light);
			float angle = getAngleForBe(be, be.getBlockPos(), ax);
			int r = switch (f) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };
			// deux rouleaux qui tournent en sens contraires (dessinés pour une sortie au nord : axe est-ouest)
			for (int k = 0; k < 2; k++) {
				ms.pushPose();
				ms.translate(0.5, 0, 0.5); ms.mulPose(Axis.YP.rotationDegrees(-r)); ms.translate(-0.5, 0, -0.5);
				float yc = k == 0 ? 9.25f / 16 : 11.75f / 16;
				ms.translate(0.5, yc, 0.5); ms.mulPose(Axis.XP.rotation(k == 0 ? angle : -angle)); ms.translate(-0.5, -yc, -0.5);
				CachedBuffers.partial(k == 0 ? AirainPartials.ROULEAU_BAS : AirainPartials.ROULEAU_HAUT, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
				ms.popPose();
			}
			// le lingot sur la table d'entrée, et le fil qui sort
			var ir = Minecraft.getInstance().getItemRenderer();
			ItemStack e = be.entree.getStackInSlot(0), o = be.sortie.getStackInSlot(0);
			float avance = be.progres / (float) Telepherique.LaminoirBlockEntity.TRAVAIL;
			ms.pushPose();
			ms.translate(0.5, 0, 0.5); ms.mulPose(Axis.YP.rotationDegrees(-r));
			if (!e.isEmpty()) {
				ms.pushPose(); ms.translate(0, 10.6 / 16, 0.55 - 0.35 * avance); ms.mulPose(Axis.XP.rotationDegrees(90)); ms.scale(0.4f, 0.4f, 0.4f);
				ir.renderStatic(e, ItemDisplayContext.FIXED, light, OverlayTexture.NO_OVERLAY, ms, buf, be.getLevel(), 0); ms.popPose();
			}
			if (!o.isEmpty()) {
				ms.pushPose(); ms.translate(0, 10.6 / 16, -0.55); ms.mulPose(Axis.XP.rotationDegrees(90)); ms.scale(0.35f, 0.35f, 0.35f);
				ir.renderStatic(o, ItemDisplayContext.FIXED, light, OverlayTexture.NO_OVERLAY, ms, buf, be.getLevel(), 0); ms.popPose();
			}
			ms.popPose();
		}
	}

	// ------------------------------------------------------------------ la nacelle
	public static class NacelleRendu extends EntityRenderer<Nacelle> {
		public NacelleRendu(EntityRendererProvider.Context c) { super(c); }
		@Override
		public void render(Nacelle n, float yaw, float pt, PoseStack ms, MultiBufferSource buf, int light) {
			BlockState s = Blocks.AIR.defaultBlockState();
			float lp = Mth.rotLerp(pt, n.lacetAvant, n.lacet), lc = Mth.rotLerp(pt, n.lacetChariotAvant, n.lacetChariot);
			ms.pushPose();
			// demi-tour de la plateforme : le portillon s'ouvre côté extérieur, à l'opposé du mât de la gare
			ms.mulPose(Axis.YP.rotationDegrees(180 - lp)); ms.translate(-0.5, 0, -0.5);
			CachedBuffers.partial(AirainPartials.PLATEFORME, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
			ms.pushPose();
			ms.mulPose(Axis.YP.rotationDegrees(-lc)); ms.translate(-0.5, 0, -0.5);
			CachedBuffers.partial(AirainPartials.BRAS, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.translate(0, Telepherique.SUSPENTE, 0);
			CachedBuffers.partial(AirainPartials.CHARIOT, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
			super.render(n, yaw, pt, ms, buf, light);
		}
		@Override public ResourceLocation getTextureLocation(Nacelle n) { return InventoryMenu.BLOCK_ATLAS; }
		@Override public boolean shouldRender(Nacelle n, net.minecraft.client.renderer.culling.Frustum f, double x, double y, double z) { return true; }
	}
}
