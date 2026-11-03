package fr.chatmort.airain.gardien;

import com.mojang.blaze3d.vertex.PoseStack;

import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;

/** Les modules montés sur le gardien, portés par la tête, le torse ou les bras ; niveau 2 en netherite noirci. */
public class ModulesCouche extends RenderLayer<GardienEntity, GardienRenderer.Modele> {
	public static final ModelLayerLocation COUCHE = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "gardien_modules"), "main");
	private static final ResourceLocation[] TEXTURES = {
		ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/gardien_modules.png"),
		ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/gardien_modules_2.png")};
	private final ModelPart racine;

	public ModulesCouche(RenderLayerParent<GardienEntity, GardienRenderer.Modele> parent, EntityRendererProvider.Context ctx) {
		super(parent);
		racine = ctx.bakeLayer(COUCHE);
	}

	public static LayerDefinition creer() {
		MeshDefinition mesh = new MeshDefinition();
		PartDefinition r = mesh.getRoot();
		for (var e : ModulesGeo.PARTIES.entrySet()) {
			CubeListBuilder c = CubeListBuilder.create();
			for (float[] b : e.getValue()) {
				int m = (int) b[6];
				c.texOffs((m % 8) * 32, (m / 8) * 32).addBox(b[0], b[1], b[2], b[3], b[4], b[5]);
			}
			r.addOrReplaceChild(e.getKey(), c, PartPose.ZERO);
		}
		return LayerDefinition.create(mesh, 256, 256);
	}

	@Override
	public void render(PoseStack pose, MultiBufferSource tampons, int lumiere, GardienEntity e, float pas, float ampleur, float pt, float age, float lacet, float tangage) {
		if (e.isInvisible()) return;
		GardienRenderer.Modele m = getParentModel();
		int voile = LivingEntityRenderer.getOverlayCoords(e, 0f);
		boolean actif = !e.enPanne();
		for (int i = 0; i < 6; i++) {
			Module.Emplacement emp = Module.Emplacement.values()[i % 3];
			int code = i < 3 ? e.codeModule(emp) : e.codeModule2(emp);
			Module mod = Module.de(code);
			if (mod == null) continue;
			ResourceLocation tex = TEXTURES[Module.niveau(code) - 1];
			switch (mod) {
				case LANTERNE -> dessiner(pose, tampons, m.tete(), "lanterne", tex, lumiere, voile, actif, 0f);
				case LUNETTE -> dessiner(pose, tampons, m.tete(), "lunette", tex, lumiere, voile, actif, 0f);
				case CANON -> {
					dessiner(pose, tampons, m.corps(), "canon", tex, lumiere, voile, actif, 0f);
					float recul = e.reculCanon > 0 ? (e.reculCanon - pt) / 6f * 2.2f : 0f;   // le fût recule au tir
					dessiner(pose, tampons, m.corps(), "canon_fut", tex, lumiere, voile, actif, Math.max(0f, recul));
				}
				case TESLA -> {
					dessiner(pose, tampons, m.corps(), "tesla", tex, lumiere, voile, actif, 0f);
					boolean arc = e.eclairTesla > 0 || (actif && (e.tickCount / 3 + e.getId()) % 11 == 0);
					if (arc && actif) dessiner(pose, tampons, m.corps(), "tesla_eclairs", tex, lumiere, voile, true, 0f);
				}
				case BLINDAGE -> {
					dessiner(pose, tampons, m.corps(), "blindage", tex, lumiere, voile, actif, 0f);
					dessiner(pose, tampons, m.brasD(), "blindage_brasD", tex, lumiere, voile, actif, 0f);
					dessiner(pose, tampons, m.brasG(), "blindage_brasG", tex, lumiere, voile, actif, 0f);
				}
				case CHAUDIERE -> dessiner(pose, tampons, m.corps(), "chaudiere", tex, lumiere, voile, actif, 0f);
			}
		}
	}

	/** Dessine une partie (et sa version lumineuse, si elle existe) dans le repère de la pièce porteuse. */
	private void dessiner(PoseStack pose, MultiBufferSource tampons, ModelPart porteur, String nom, ResourceLocation tex,
						  int lumiere, int voile, boolean allume, float reculZ) {
		pose.pushPose();
		porteur.translateAndRotate(pose);
		if (reculZ != 0f) pose.translate(0f, 0f, reculZ / 16f);
		if (ModulesGeo.PARTIES.containsKey(nom))
			racine.getChild(nom).render(pose, tampons.getBuffer(RenderType.entityCutoutNoCull(tex)), lumiere, voile);
		if (ModulesGeo.PARTIES.containsKey(nom + "_lum"))
			racine.getChild(nom + "_lum").render(pose, tampons.getBuffer(RenderType.entityCutoutNoCull(tex)),
				allume ? LightTexture.FULL_BRIGHT : lumiere, voile, allume ? -1 : 0xFF806040);
		pose.popPose();
	}
}
