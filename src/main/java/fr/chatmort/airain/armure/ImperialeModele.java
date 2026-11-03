package fr.chatmort.airain.armure;

import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
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

/**
 * L'armure de l'Empereur : un modèle par pièce (le moteur rend les parties du modèle selon l'emplacement, et la cape
 * ne doit apparaître qu'avec le plastron). Couronne, étoiles, loupe, grandes épaulières, cape rouge.
 */
public final class ImperialeModele {
	private ImperialeModele() {}
	public static final ModelLayerLocation[] COUCHES = new ModelLayerLocation[4];
	private static final String[] NOMS = {"casque", "plastron", "jambieres", "bottes"};
	static {
		for (int i = 0; i < 4; i++)
			COUCHES[i] = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "imperiale_" + NOMS[i]), "main");
	}

	private static void pieces(CubeListBuilder c, String part) {
		float[][] l = ImperialeGeo.PIECES.get(part);
		if (l == null) return;
		for (float[] b : l) {
			int[] t = ImperialeGeo.TUILES[(int) b[6]];
			c.texOffs(t[0], t[1]).addBox(b[0], b[1], b[2], b[3], b[4], b[5]);
		}
	}

	/** 0 casque, 1 plastron, 2 jambières, 3 bottes. */
	public static LayerDefinition creer(int piece) {
		MeshDefinition mesh = new MeshDefinition();
		PartDefinition r = mesh.getRoot();
		CubeDeformation un = new CubeDeformation(1f), demi = new CubeDeformation(0.5f);
		CubeListBuilder tete = CubeListBuilder.create(), corps = CubeListBuilder.create(), brasD = CubeListBuilder.create(), brasG = CubeListBuilder.create(),
			jambeD = CubeListBuilder.create(), jambeG = CubeListBuilder.create();
		switch (piece) {
			case 0 -> { tete.texOffs(0, 0).addBox(-4, -8, -4, 8, 8, 8, un); pieces(tete, "tete"); }
			case 1 -> {
				corps.texOffs(16, 16).addBox(-4, 0, -2, 8, 12, 4, un); pieces(corps, "corps"); pieces(corps, "cape_barre");
				brasD.texOffs(40, 16).addBox(-3, -2, -2, 4, 12, 4, un); pieces(brasD, "bras_d");
				brasG.texOffs(40, 16).mirror().addBox(-1, -2, -2, 4, 12, 4, un).mirror(false); pieces(brasG, "bras_g");
			}
			case 2 -> {
				corps.texOffs(16, 48).addBox(-4, 0, -2, 8, 12, 4, demi);
				jambeD.texOffs(0, 48).addBox(-2, 0, -2, 4, 12, 4, demi); pieces(jambeD, "jambe_d");
				jambeG.texOffs(0, 48).mirror().addBox(-2, 0, -2, 4, 12, 4, demi).mirror(false); pieces(jambeG, "jambe_g");
			}
			default -> {
				jambeD.texOffs(0, 16).addBox(-2, 0, -2, 4, 12, 4, un); pieces(jambeD, "pied_d");
				jambeG.texOffs(0, 16).mirror().addBox(-2, 0, -2, 4, 12, 4, un).mirror(false); pieces(jambeG, "pied_g");
			}
		}
		PartDefinition pc = r.addOrReplaceChild("body", corps, PartPose.ZERO);
		if (piece == 1)        // la cape, accrochée au dos, légèrement écartée
			pc.addOrReplaceChild("cape", CubeListBuilder.create().texOffs(ImperialeGeo.CAPE[0], ImperialeGeo.CAPE[1]).addBox(-6, 0, 0, 12, 22, 1),
				PartPose.offsetAndRotation(0, -0.2f, 3f, 0.06f, 0, 0));
		r.addOrReplaceChild("head", tete, PartPose.offset(0, 0, 0));
		r.addOrReplaceChild("hat", CubeListBuilder.create(), PartPose.ZERO);
		r.addOrReplaceChild("right_arm", brasD, PartPose.offset(-5, 2, 0));
		r.addOrReplaceChild("left_arm", brasG, PartPose.offset(5, 2, 0));
		r.addOrReplaceChild("right_leg", jambeD, PartPose.offset(-1.9f, 12, 0));
		r.addOrReplaceChild("left_leg", jambeG, PartPose.offset(1.9f, 12, 0));
		return LayerDefinition.create(mesh, 128, 128);
	}

	public static IClientItemExtensions extension(int piece) {
		return new IClientItemExtensions() {
			private HumanoidModel<LivingEntity> modele;

			@Override
			public HumanoidModel<?> getHumanoidArmorModel(LivingEntity e, ItemStack pile, EquipmentSlot emplacement, HumanoidModel<?> original) {
				if (modele == null) modele = new HumanoidModel<>(Minecraft.getInstance().getEntityModels().bakeLayer(COUCHES[piece]));
				return modele;
			}
		};
	}
}
