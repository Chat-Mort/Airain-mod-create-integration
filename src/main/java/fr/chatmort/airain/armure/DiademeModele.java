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

/** Le diadème porté : un cercle fin d'argent, une gemme lavande au front, des cristaux violets. */
public final class DiademeModele {
	private DiademeModele() {}
	public static final ModelLayerLocation COUCHE = new ModelLayerLocation(ResourceLocation.fromNamespaceAndPath("airain", "diademe"), "main");
	private static final int ARGENT = 0, SOMBRE = 1, LUEUR = 2, VIOLET = 3;
	private static int u(int t) { return (t % 2) * 32; }
	private static int v(int t) { return (t / 2) * 16; }

	public static LayerDefinition creer() {
		MeshDefinition mesh = HumanoidModel.createMesh(CubeDeformation.NONE, 0f);
		PartDefinition r = mesh.getRoot();
		CubeListBuilder c = CubeListBuilder.create();
		// cercle (quatre côtés) au niveau du front
		c.texOffs(u(ARGENT), v(ARGENT)).addBox(-4.6f, -6.6f, -4.6f, 9.2f, 0.8f, 0.5f);
		c.texOffs(u(ARGENT), v(ARGENT)).addBox(-4.6f, -6.6f, 4.1f, 9.2f, 0.8f, 0.5f);
		c.texOffs(u(SOMBRE), v(SOMBRE)).addBox(-4.6f, -6.6f, -4.1f, 0.5f, 0.8f, 8.2f);
		c.texOffs(u(SOMBRE), v(SOMBRE)).addBox(4.1f, -6.6f, -4.1f, 0.5f, 0.8f, 8.2f);
		// gemme au front, sertie d'argent
		c.texOffs(u(ARGENT), v(ARGENT)).addBox(-1.5f, -8.2f, -4.9f, 3f, 2.2f, 0.4f);
		c.texOffs(u(LUEUR), v(LUEUR)).addBox(-1f, -7.9f, -5.1f, 2f, 1.6f, 0.4f);
		c.texOffs(u(LUEUR), v(LUEUR)).addBox(-0.5f, -9.2f, -4.8f, 1f, 1f, 0.4f);
		// petits cristaux
		for (float[] k : new float[][] {{-4.7f, -2.5f}, {-4.7f, 1.5f}, {4.2f, -2.5f}, {4.2f, 1.5f}})
			c.texOffs(u(VIOLET), v(VIOLET)).addBox(k[0], -8f, k[1], 0.5f, 1.4f, 1f);
		r.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.ZERO).addOrReplaceChild("diademe", c, PartPose.ZERO);
		r.addOrReplaceChild("hat", CubeListBuilder.create(), PartPose.ZERO);
		return LayerDefinition.create(mesh, 64, 64);
	}

	public static final IClientItemExtensions EXTENSION = new IClientItemExtensions() {
		private HumanoidModel<LivingEntity> modele;

		@Override
		public HumanoidModel<?> getHumanoidArmorModel(LivingEntity e, ItemStack pile, EquipmentSlot emplacement, HumanoidModel<?> original) {
			if (modele == null) modele = new HumanoidModel<>(Minecraft.getInstance().getEntityModels().bakeLayer(COUCHE));
			return modele;
		}
	};
}
