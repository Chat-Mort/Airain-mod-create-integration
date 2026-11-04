package fr.chatmort.airain.gardien;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;

import net.minecraft.client.model.IronGolemModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;

/** Golem de laiton au vert-de-gris ; en panne, il est assis, tête basse, couvert de mousse. */
public class GardienRenderer extends MobRenderer<GardienEntity, GardienRenderer.Modele> {
	private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/guardian.png");
	private static final ResourceLocation CAPITAINE = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/guardian_captain.png");
	private static final ResourceLocation ECHO = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/guardian_echo.png");
	private static final ResourceLocation MOUSSE = ResourceLocation.fromNamespaceAndPath("airain", "textures/entity/guardian_moss.png");

	public GardienRenderer(EntityRendererProvider.Context ctx) {
		super(ctx, new Modele(ctx.bakeLayer(ModelLayers.IRON_GOLEM)), 0.7f);
		addLayer(new Fissures(this));
		addLayer(new Mousse(this));
		addLayer(new ModulesCouche(this, ctx));
		addLayer(new EliteCouche(this, ctx));
	}

	@Override
	public ResourceLocation getTextureLocation(GardienEntity e) { return e.capitaine() ? CAPITAINE : e.echo() ? ECHO : TEXTURE; }

	@Override
	protected void setupRotations(GardienEntity e, PoseStack pose, float bob, float yRot, float pt, float echelle) {
		super.setupRotations(e, pose, bob, yRot, pt, echelle);
		if (e.enPanne()) {
			pose.translate(0f, -0.8f, 0f);
			return;
		}
		if (e.walkAnimation.speed() >= 0.01f) {
			float f = 13f, g = e.walkAnimation.position(pt) + 6f;
			float h = (Math.abs(g % f - f * 0.5f) - f * 0.25f) / (f * 0.25f);
			pose.mulPose(Axis.ZP.rotationDegrees(6.5f * h));
		}
	}

	public static class Modele extends IronGolemModel<GardienEntity> {
		private final ModelPart tete, corps, brasD, brasG, jambeD, jambeG;

		public Modele(ModelPart racine) {
			super(racine);
			tete = racine.getChild("head");
			corps = racine.getChild("body");
			brasD = racine.getChild("right_arm");
			brasG = racine.getChild("left_arm");
			jambeD = racine.getChild("right_leg");
			jambeG = racine.getChild("left_leg");
		}

		public ModelPart tete() { return tete; }
		public ModelPart corps() { return corps; }
		public ModelPart brasD() { return brasD; }
		public ModelPart brasG() { return brasG; }

		@Override
		public void setupAnim(GardienEntity e, float pas, float ampleur, float age, float lacet, float tangage) {
			super.setupAnim(e, pas, ampleur, age, lacet, tangage);
			if (!e.enPanne()) return;
			tete.xRot = 0.75f; tete.yRot = 0.25f;
			brasD.xRot = -0.35f; brasD.zRot = 0.12f;
			brasG.xRot = -0.2f; brasG.zRot = -0.18f;
			jambeD.xRot = -1.45f; jambeD.yRot = 0.2f;
			jambeG.xRot = -1.45f; jambeG.yRot = -0.2f;
		}

		@Override
		public void prepareMobModel(GardienEntity e, float pas, float ampleur, float pt) {
			if (e.enPanne()) return;     // pas d'animation d'attaque ni de fleur
			super.prepareMobModel(e, pas, ampleur, pt);
		}
	}

	/** Les fissures du golem vanilla, selon ses points de vie. */
	static class Fissures extends RenderLayer<GardienEntity, Modele> {
		Fissures(RenderLayerParent<GardienEntity, Modele> parent) { super(parent); }

		@Override
		public void render(PoseStack pose, MultiBufferSource tampon, int lumiere, GardienEntity e, float pas, float ampleur, float pt, float age, float lacet, float tangage) {
			if (e.isInvisible()) return;
			String n = e.getCrackiness().name().toLowerCase(java.util.Locale.ROOT);
			if (n.equals("none")) return;
			renderColoredCutoutModel(getParentModel(), ResourceLocation.withDefaultNamespace("textures/entity/iron_golem/iron_golem_crackiness_" + n + ".png"),
				pose, tampon, lumiere, e, -1);
		}
	}

	static class Mousse extends RenderLayer<GardienEntity, Modele> {
		Mousse(RenderLayerParent<GardienEntity, Modele> parent) { super(parent); }

		@Override
		public void render(PoseStack pose, MultiBufferSource tampon, int lumiere, GardienEntity e, float pas, float ampleur, float pt, float age, float lacet, float tangage) {
			if (e.isInvisible() || !e.enPanne()) return;
			renderColoredCutoutModel(getParentModel(), MOUSSE, pose, tampon, lumiere, e, -1);
		}
	}
}
