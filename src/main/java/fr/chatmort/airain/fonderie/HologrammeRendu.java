package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.client.model.data.ModelData;

/** Dessin de l'hologramme du haut-fourneau (côté client) : blocs fantômes bleutés, contour rouge sur les blocs faux. */
public final class HologrammeRendu {
	private HologrammeRendu() {}

	public static void rendu(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		HautFourneauBlockEntity be = HologrammeFourneau.actif(mc.player);
		if (be == null) return;
		var liste = HologrammeFourneau.fantomes(be);
		if (liste.isEmpty()) return;
		PoseStack ms = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		BlockRenderDispatcher br = mc.getBlockRenderer();
		// léger battement de l'opacité, pour qu'on le distingue des vrais blocs
		float t = (System.currentTimeMillis() % 2000) / 2000f;
		float alpha = 0.38f + 0.12f * (float) Math.sin(t * Math.PI * 2);
		VertexConsumer fantome = new Translucide(buf.getBuffer(Sheets.translucentCullBlockSheet()), alpha);
		for (var f : liste) {
			if (f.faux()) continue;
			ms.pushPose();
			ms.translate(f.pos().getX() - cam.x, f.pos().getY() - cam.y, f.pos().getZ() - cam.z);
			// un rien plus petit qu'un bloc : pas de scintillement contre les blocs voisins
			ms.translate(0.5, 0.5, 0.5); ms.scale(0.98f, 0.98f, 0.98f); ms.translate(-0.5, -0.5, -0.5);
			br.getModelRenderer().renderModel(ms.last(), fantome, f.etat(), br.getBlockModel(f.etat()), 0.65f, 0.85f, 1f,
				LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY, ModelData.EMPTY, null);
			ms.popPose();
		}
		buf.endBatch(Sheets.translucentCullBlockSheet());
		VertexConsumer lignes = buf.getBuffer(RenderType.lines());
		for (var f : liste) {
			AABB b = new AABB(f.pos()).inflate(0.004).move(-cam.x, -cam.y, -cam.z);
			if (f.faux()) LevelRenderer.renderLineBox(ms, lignes, b, 1f, 0.25f, 0.2f, 1f);
			else LevelRenderer.renderLineBox(ms, lignes, b, 0.55f, 0.8f, 1f, 0.35f);
		}
		buf.endBatch(RenderType.lines());
	}

	/** Passe les sommets au tampon en réduisant leur opacité. */
	private record Translucide(VertexConsumer v, float alpha) implements VertexConsumer {
		@Override public VertexConsumer addVertex(float x, float y, float z) { v.addVertex(x, y, z); return this; }
		@Override public VertexConsumer setColor(int r, int g, int b, int a) { v.setColor(r, g, b, (int) (a * alpha)); return this; }
		@Override public VertexConsumer setUv(float u, float w) { v.setUv(u, w); return this; }
		@Override public VertexConsumer setUv1(int u, int w) { v.setUv1(u, w); return this; }
		@Override public VertexConsumer setUv2(int u, int w) { v.setUv2(u, w); return this; }
		@Override public VertexConsumer setNormal(float x, float y, float z) { v.setNormal(x, y, z); return this; }
	}
}
