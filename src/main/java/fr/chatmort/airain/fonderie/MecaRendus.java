package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;
import fr.chatmort.airain.AirainPartials;
import net.createmod.catnip.render.CachedBuffers;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.neoforged.neoforge.client.model.data.ModelData;
import org.joml.Vector3f;

/** Rendus des mécanismes : segments de passerelle mobile en mouvement, cabine du monte-charge entre deux étages. */
public final class MecaRendus {
	private MecaRendus() {}

	private static void bloc(BlockState s, PoseStack ms, MultiBufferSource buf, int light) {
		BlockRenderDispatcher d = Minecraft.getInstance().getBlockRenderer();
		d.renderSingleBlock(s, ms, buf, light, OverlayTexture.NO_OVERLAY, ModelData.EMPTY, null);
	}

	// ---------------------------------------------------------------- passerelle mobile : pont-levis ou télescope
	public static class Mobile implements BlockEntityRenderer<PasserelleMobile.Mecanisme> {
		public Mobile(BlockEntityRendererProvider.Context c) {}
		@Override
		public void render(PasserelleMobile.Mecanisme be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			if (be.getLevel() == null) return;
			float a = be.avanceAvant + (be.avance - be.avanceAvant) * pt;
			if (a >= 1) return;                                            // déployé : ce sont de vrais blocs
			Direction f = be.sens(); int n = be.longueur();
			boolean pont = be.pontLevis();
			float h = be.getBlockState().getValue(Passerelle.HAUT) ? 11 / 16f : 3 / 16f;
			for (int i = 1; i <= n; i++) {
				BlockPos q = be.getBlockPos().relative(f, i);
				BlockState s = be.getLevel().getBlockState(q);
				if (!(s.getBlock() instanceof Passerelle.Plancher) || s.getBlock() instanceof PasserelleMobile) break;
				s = s.setValue(Passerelle.RENTRE, false);
				ms.pushPose();
				if (pont) {
					// tout le tablier pivote autour du bord du mécanisme, au ras du plancher
					float px = 0.5f + f.getStepX() * 0.5f, pz = 0.5f + f.getStepZ() * 0.5f;
					ms.translate(px, h, pz);
					ms.mulPose(Axis.of(new Vector3f(-f.getStepZ(), 0, f.getStepX())).rotationDegrees(80f * (1 - a)));
					ms.translate(-px, -h, -pz);
					ms.translate(f.getStepX() * i, 0, f.getStepZ() * i);
				} else {
					// télescope : le segment k sort quand le précédent est sorti
					float e = a * n, fr = Math.max(0, Math.min(1, e - (i - 1)));
					if (fr <= 0.02f) { ms.popPose(); continue; }
					float d = i + fr - 1;
					ms.translate(f.getStepX() * d, 0, f.getStepZ() * d);
				}
				bloc(s, ms, buf, LevelRenderer.getLightColor(be.getLevel(), q));
				ms.popPose();
			}
		}
		@Override public boolean shouldRenderOffScreen(PasserelleMobile.Mecanisme be) { return true; }
		@Override public int getViewDistance() { return 96; }
	}

	// ---------------------------------------------------------------- monte-charge : arbre du treuil, et cabine en mouvement
	public static class Treuil extends KineticBlockEntityRenderer<MonteCharge.TreuilBlockEntity> {
		public Treuil(BlockEntityRendererProvider.Context c) { super(c); }
		@Override
		protected void renderSafe(MonteCharge.TreuilBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			super.renderSafe(be, pt, ms, buf, light, overlay);
			if (!be.mouvement || be.getLevel() == null) return;
			float y = be.posAvant + (be.pos - be.posAvant) * pt;
			Direction f = be.face;
			BlockState cab = MonteCharge.CABINE.get().defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, f);
			ms.pushPose();
			ms.translate(f.getStepX(), y, f.getStepZ());
			BlockPos q = be.getBlockPos().above(Math.round(y)).relative(f);
			int l = LevelRenderer.getLightColor(be.getLevel(), q);
			bloc(cab, ms, buf, l);
			// portail fermé pendant le trajet (dessiné face au nord, tourné comme la cabine)
			int r = switch (f) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };
			ms.translate(0.5, 0, 0.5); ms.mulPose(Axis.YP.rotationDegrees(-r)); ms.translate(-0.5, 0, -0.5);
			CachedBuffers.partial(AirainPartials.PORTAIL_CABINE, cab).light(l).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
		}
		@Override public boolean shouldRenderOffScreen(MonteCharge.TreuilBlockEntity be) { return true; }
		@Override public int getViewDistance() { return 128; }
	}

	// ---------------------------------------------------------------- allégeur : l'arbre, le volant d'inertie qui tourne, ses lampes quand il travaille
	public static class Allegeur extends KineticBlockEntityRenderer<Mecanique.AllegeurBlockEntity> {
		public Allegeur(BlockEntityRendererProvider.Context c) { super(c); }
		@Override
		protected void renderSafe(Mecanique.AllegeurBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			super.renderSafe(be, pt, ms, buf, light, overlay);
			BlockState s = be.getBlockState();
			Direction.Axis ax = s.getValue(BlockStateProperties.AXIS);
			float angle = getAngleForBe(be, be.getBlockPos(), ax);
			ms.pushPose();
			ms.translate(0.5, 0.5, 0.5);
			if (ax == Direction.Axis.X) ms.mulPose(Axis.YP.rotationDegrees(-90));
			if (ax == Direction.Axis.Y) ms.mulPose(Axis.XP.rotationDegrees(-90));
			ms.pushPose();
			ms.mulPose(Axis.ZP.rotation(angle));
			ms.translate(-0.5, -0.5, -0.5);
			CachedBuffers.partial(AirainPartials.VOLANT[AirainPartials.teinte(s)], s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
			if (be.actif) {
				ms.translate(-0.5, -0.5, -0.5);
				CachedBuffers.partial(AirainPartials.LAMPES_ALLEGEUR, s).light(net.minecraft.client.renderer.LightTexture.FULL_BRIGHT).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			}
			ms.popPose();
		}
	}

	// ---------------------------------------------------------------- surcompresseur : pistons qui battent, aiguille du manomètre, voyant
	public static class Surcompresseur implements BlockEntityRenderer<Mecanique.SurcompresseurBlockEntity> {
		public Surcompresseur(BlockEntityRendererProvider.Context c) {}
		@Override
		public void render(Mecanique.SurcompresseurBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			BlockState s = be.getBlockState();
			Direction f = s.getValue(BlockStateProperties.HORIZONTAL_FACING);
			int r = switch (f) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; };
			float ph = be.phaseAvant + (be.phase - be.phaseAvant) * pt;
			ms.pushPose();
			ms.translate(0.5, 0, 0.5); ms.mulPose(Axis.YP.rotationDegrees(-r)); ms.translate(-0.5, 0, -0.5);
			for (int i = 0; i < 2; i++) {                                // deux pistons en opposition
				ms.pushPose();
				ms.translate(i * 6 / 16f, (float) Math.sin(ph + i * Math.PI) * 1.5f / 16f, 0);
				CachedBuffers.partial(AirainPartials.PISTON[AirainPartials.teinte(s)], s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
				ms.popPose();
			}
			ms.pushPose();                                               // aiguille du manomètre (cadran tourné vers l'arrière)
			ms.translate(0.5, 18 / 16f, 14.25 / 16f);
			ms.mulPose(Axis.YP.rotationDegrees(180));
			ms.mulPose(Axis.ZP.rotationDegrees(-135f + 270f * be.aiguille));
			ms.translate(-0.5, -0.5, -0.5);
			CachedBuffers.partial(AirainPartials.AIGUILLE, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
			if (be.vitesse > 0)
				CachedBuffers.partial(AirainPartials.VOYANT_SURCOMP, s).light(net.minecraft.client.renderer.LightTexture.FULL_BRIGHT).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
		}
	}
}
