package fr.chatmort.airain.gardien;

import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;

/** Couronne d'airain portée : fleurons, bandeau riveté, loupe sur l'œil droit, deux rouages qui tournent sur les oreilles. */
public class CouronneModele extends HumanoidModel<LivingEntity> {
	public static final ModelLayerLocation COUCHE = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "couronne"), "main");
	public static final ModelLayerLocation COUCHE_CASQUE = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "casque_couronne"), "main");
	private final ModelPart rouageD, rouageG;

	public CouronneModele(ModelPart racine) {
		super(racine);
		rouageD = head.getChild("rouage_d");
		rouageG = head.getChild("rouage_g");
	}

	private static int u(int m) { return (m % 2) * 32; }
	private static int v(int m) { return (m / 2) * 12; }

	public static LayerDefinition creer() { return creer(CouronneGeo.SEULE, CouronneGeo.MOYEU_X_SEULE, false); }
	public static LayerDefinition creerCasque() { return creer(CouronneGeo.CASQUE, CouronneGeo.MOYEU_X_CASQUE, true); }

	private static LayerDefinition creer(float[][] fixe, float moyeuX, boolean casque) {
		MeshDefinition mesh = HumanoidModel.createMesh(CubeDeformation.NONE, 0f);
		PartDefinition racine = mesh.getRoot();
		PartDefinition tete = racine.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.ZERO);
		racine.addOrReplaceChild("hat", CubeListBuilder.create(), PartPose.ZERO);
		for (String p : new String[] {"body", "right_arm", "left_arm", "right_leg", "left_leg"})
			racine.addOrReplaceChild(p, CubeListBuilder.create(), PartPose.ZERO);
		CubeListBuilder c = CubeListBuilder.create();
		if (casque)      // le casque de netherite : la tête vanilla, gonflée d'un pixel, UV en (64, 0)
			c.texOffs(64, 0).addBox(-4f, -8f, -4f, 8, 8, 8, new CubeDeformation(1f));
		for (float[] b : fixe)
			c.texOffs(u((int) b[6]), v((int) b[6])).addBox(b[0], b[1], b[2], b[3], b[4], b[5]);
		tete.addOrReplaceChild("couronne", c, PartPose.ZERO);
		for (int cote = -1; cote <= 1; cote += 2) {
			CubeListBuilder r = CubeListBuilder.create();
			for (int[] d : CouronneGeo.ROUAGE)
				r.texOffs(u(d[2]), v(d[2])).addBox(-0.5f, d[0] - 0.5f, d[1] - 0.5f, 1, 1, 1);
			tete.addOrReplaceChild(cote < 0 ? "rouage_d" : "rouage_g", r,
				PartPose.offset(cote * moyeuX, CouronneGeo.MOYEU_Y, CouronneGeo.MOYEU_Z));
		}
		return LayerDefinition.create(mesh, 128, 64);
	}

	public static final IClientItemExtensions EXTENSION = extension(COUCHE);
	public static final IClientItemExtensions EXTENSION_CASQUE = extension(COUCHE_CASQUE);

	/** Le modèle remplace le casque vanilla ; les rouages tournent en sens contraires. */
	private static IClientItemExtensions extension(ModelLayerLocation couche) {
		return new IClientItemExtensions() {
			private CouronneModele instance;

			@Override
			public HumanoidModel<?> getHumanoidArmorModel(LivingEntity e, ItemStack pile, EquipmentSlot emplacement, HumanoidModel<?> original) {
				if (instance == null) instance = new CouronneModele(Minecraft.getInstance().getEntityModels().bakeLayer(couche));
				float t = e.tickCount + Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(true);
				instance.rouageD.xRot = t * 0.05f;
				instance.rouageG.xRot = -t * 0.05f;
				return instance;
			}
		};
	}
}
