package fr.chatmort.airain.armure;

import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;

/**
 * Les coiffes de l'Écho : casque au diadème (netherite, cercle d'argent, gemme), tiare runique (le casque disparaît),
 * nimbe de la Haute-Prêtresse (couronne à branches fines ; le halo lumineux est dessiné à part par {@link CoiffesHalo}).
 */
public final class CoiffesModele {
	private CoiffesModele() {}
	public static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("airain", "textures/models/armor/coiffes_echo.png");
	public static final ModelLayerLocation[] COUCHES = {
		new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "casque_diademe"), "main"),
		new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "tiare_runique"), "main"),
		new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "nimbe"), "main")};
	public static final ModelLayerLocation HALO = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "halo"), "main");

	public static LayerDefinition creer(int k) {
		MeshDefinition mesh = HumanoidModel.createMesh(CubeDeformation.NONE, 0f);
		CubeListBuilder c = CubeListBuilder.create();
		switch (k) {
			case 0 -> { c.texOffs(0, 0).addBox(-4f, -8f, -4f, 8f, 8f, 8f, new CubeDeformation(1f)); CoiffesGeo.casque(c); }
			case 1 -> CoiffesGeo.tiare(c);
			default -> CoiffesGeo.nimbe(c);
		}
		// la tête et le chapeau du modèle de base sont vidés : seule la coiffe est dessinée (sinon un cube cache le visage)
		mesh.getRoot().addOrReplaceChild("head", CubeListBuilder.create(), PartPose.ZERO).addOrReplaceChild("coiffe", c, PartPose.ZERO);
		mesh.getRoot().addOrReplaceChild("hat", CubeListBuilder.create(), PartPose.ZERO);
		return LayerDefinition.create(mesh, 64, 96);
	}

	public static LayerDefinition creerHalo() {
		MeshDefinition mesh = new MeshDefinition();
		CubeListBuilder c = CubeListBuilder.create();
		CoiffesGeo.halo(c);
		mesh.getRoot().addOrReplaceChild("halo", c, PartPose.ZERO);
		return LayerDefinition.create(mesh, 64, 96);
	}

	public static IClientItemExtensions extension(int k) {
		return new IClientItemExtensions() {
			private HumanoidModel<LivingEntity> modele;

			@Override
			public HumanoidModel<?> getHumanoidArmorModel(LivingEntity e, ItemStack pile, EquipmentSlot emplacement, HumanoidModel<?> original) {
				if (modele == null) modele = new HumanoidModel<>(Minecraft.getInstance().getEntityModels().bakeLayer(COUCHES[k]));
				return modele;
			}
		};
	}
}
