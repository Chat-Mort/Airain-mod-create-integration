package fr.chatmort.airain.gardien;

import com.mojang.blaze3d.vertex.PoseStack;

import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;

/** Ornements des gardiens d'élite : couronne, plumet, épaulettes et cape du capitaine ; cœur de résonance et cristaux du gardien d'Écho. */
public class EliteCouche extends RenderLayer<GardienEntity, GardienRenderer.Modele> {
	public static final ModelLayerLocation COUCHE = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "gardien_elite"), "main");
	private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/gardien_elite.png");
	private final ModelPart racine;

	public EliteCouche(RenderLayerParent<GardienEntity, GardienRenderer.Modele> parent, EntityRendererProvider.Context ctx) {
		super(parent);
		racine = ctx.bakeLayer(COUCHE);
	}

	public static LayerDefinition creer() {
		MeshDefinition mesh = new MeshDefinition();
		for (var e : EliteGeo.PARTIES.entrySet()) {
			CubeListBuilder c = CubeListBuilder.create();
			for (float[] b : e.getValue()) {
				int t = (int) b[6];
				c.texOffs((t % 4) * 64, (t / 4) * 32).addBox(b[0], b[1], b[2], b[3], b[4], b[5]);
			}
			mesh.getRoot().addOrReplaceChild(e.getKey(), c, PartPose.ZERO);
		}
		return LayerDefinition.create(mesh, 256, 128);
	}

	@Override
	public void render(PoseStack pose, MultiBufferSource tampons, int lumiere, GardienEntity e, float pas, float ampleur, float pt, float age, float lacet, float tangage) {
		if (e.isInvisible() || e.rang() == 0) return;
		GardienRenderer.Modele m = getParentModel();
		int voile = LivingEntityRenderer.getOverlayCoords(e, 0f);
		String p = e.capitaine() ? "cap_" : "echo_";
		dessiner(pose, tampons, m.tete(), p + "tete", lumiere, voile);
		dessiner(pose, tampons, m.corps(), p + "corps", lumiere, voile);
		dessiner(pose, tampons, m.brasD(), p + "brasD", lumiere, voile);
		dessiner(pose, tampons, m.brasG(), p + "brasG", lumiere, voile);
	}

	private void dessiner(PoseStack pose, MultiBufferSource tampons, ModelPart porteur, String nom, int lumiere, int voile) {
		boolean a = EliteGeo.PARTIES.containsKey(nom), b = EliteGeo.PARTIES.containsKey(nom + "_lum");
		if (!a && !b) return;
		pose.pushPose();
		porteur.translateAndRotate(pose);
		var tampon = tampons.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
		if (a) racine.getChild(nom).render(pose, tampon, lumiere, voile);
		if (b) racine.getChild(nom + "_lum").render(pose, tampon, LightTexture.FULL_BRIGHT, voile);
		pose.popPose();
	}
}
