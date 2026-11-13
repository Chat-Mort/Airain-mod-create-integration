package fr.chatmort.airain.atelier;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import fr.chatmort.airain.AirainPartials;
import net.createmod.catnip.render.CachedBuffers;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/** Rendus animés des pièces d'atelier : aiguille du manomètre, réflecteur du gyrophare, flèches et textes des bornes. */
public final class AtelierRendus {
	private AtelierRendus() {}

	static int rot(Direction d) { return switch (d) { case EAST -> 90; case SOUTH -> 180; case WEST -> 270; default -> 0; }; }

	// ---------------------------------------------------------------- manomètre : l'aiguille suit la lecture (lissée)
	public static class ManometreRendu implements BlockEntityRenderer<Manometre.ManometreBlockEntity> {
		public ManometreRendu(BlockEntityRendererProvider.Context c) {}
		@Override
		public void render(Manometre.ManometreBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			BlockState s = be.getBlockState();
			if (be.getLevel() == null) return;
			float cible = Manometre.lecture(be.getLevel(), s, be.getBlockPos());
			be.aiguille += (cible - be.aiguille) * 0.08f;
			AttachFace f = s.getValue(Manometre.FACE);
			Direction d = s.getValue(Manometre.FACING);
			int y = rot(f == AttachFace.WALL ? d : d.getOpposite());
			// centre du cadran (modèle dessiné face au nord)
			float cy = f == AttachFace.FLOOR ? 6 : f == AttachFace.CEILING ? 10 : 8;
			float cz = f == AttachFace.WALL ? 12.3f : 6.3f;
			ms.pushPose();
			ms.translate(0.5, 0, 0.5);
			ms.mulPose(Axis.YP.rotationDegrees(-y));
			ms.translate(-0.5, 0, -0.5);
			ms.translate(0.5, cy / 16f, cz / 16f);
			ms.mulPose(Axis.ZP.rotationDegrees(-135f + 270f * be.aiguille));
			ms.translate(-0.5, -0.5, -0.5);
			CachedBuffers.partial(AirainPartials.AIGUILLE, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
		}
	}

	// ---------------------------------------------------------------- gyrophare : le réflecteur tourne quand il est allumé
	public static class GyrophareRendu implements BlockEntityRenderer<Lampes.GyrophareBlockEntity> {
		public GyrophareRendu(BlockEntityRendererProvider.Context c) {}
		@Override
		public void render(Lampes.GyrophareBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			BlockState s = be.getBlockState();
			if (!s.getValue(BlockStateProperties.LIT) || be.getLevel() == null) return;
			float a = ((be.getLevel().getGameTime() % 40) + pt) * 9f;
			ms.pushPose();
			ms.translate(0.5, 0, 0.5);
			ms.mulPose(Axis.YP.rotationDegrees(a));
			ms.translate(-0.5, 0, -0.5);
			CachedBuffers.partial(AirainPartials.REFLECTEUR, s).light(LightTexture.FULL_BRIGHT).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			ms.popPose();
		}
	}

	// ---------------------------------------------------------------- borne : flèches (8 directions) et leurs textes
	public static class BorneRendu implements BlockEntityRenderer<Borne.BorneBlockEntity> {
		private final Font font;
		public BorneRendu(BlockEntityRendererProvider.Context c) { font = c.getFont(); }
		@Override
		public void render(Borne.BorneBlockEntity be, float pt, PoseStack ms, MultiBufferSource buf, int light, int overlay) {
			BlockState s = be.getBlockState();
			fleche(s, s.getValue(Borne.FLECHE_HAUT), be.texteHaut, 9.5f, ms, buf, light);
			fleche(s, s.getValue(Borne.FLECHE_BAS), be.texteBas, 2.5f, ms, buf, light);
		}
		private void fleche(BlockState s, Borne.Dir8 d, String texte, float y, PoseStack ms, MultiBufferSource buf, int light) {
			if (d == Borne.Dir8.AUCUNE) return;
			boolean ecrit = texte != null && !texte.isEmpty();
			ms.pushPose();
			ms.translate(0.5, 0, 0.5);
			ms.mulPose(Axis.YP.rotationDegrees(-45f * d.rang()));          // la flèche, dessinée vers le nord, tourne vers sa direction
			ms.translate(-0.5, y / 16f, -0.5);
			CachedBuffers.partial(ecrit ? AirainPartials.PLANCHETTE : AirainPartials.FLECHE, s).light(light).renderInto(ms, buf.getBuffer(RenderType.cutout()));
			if (ecrit) {
				float w = font.width(texte), k = Math.min(0.016f, 0.7f / Math.max(1, w));
				for (int c = 0; c < 2; c++) {                                // une face, puis l'autre (le texte se lit toujours de gauche à droite)
					ms.pushPose();
					ms.translate(c == 0 ? 8.53 / 16 : 7.47 / 16, 3 / 16f, 0.5 / 16);
					ms.mulPose(Axis.YP.rotationDegrees(c == 0 ? 90 : -90));
					ms.scale(k, -k, k);
					font.drawInBatch(texte, -w / 2, -4, 0xF0C870, false, ms.last().pose(), buf, Font.DisplayMode.POLYGON_OFFSET, 0, light);
					ms.popPose();
				}
			}
			ms.popPose();
		}
	}
	@SuppressWarnings("unused") private static final Minecraft INUTILE = null;
}
