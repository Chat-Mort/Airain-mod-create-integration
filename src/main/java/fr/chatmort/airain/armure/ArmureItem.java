package fr.chatmort.airain.armure;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** Pièce d'armure sacrée (palier 1) ou impériale (palier 2). */
public class ArmureItem extends ArmorItem {
	public final int palier;

	public ArmureItem(Holder<ArmorMaterial> m, Type type, int palier, Properties p) {
		super(m, type, p);
		this.palier = palier;
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		String k = palier == 2 ? "imperiale" : "sacree";
		l.add(Component.translatable("airain.armure." + k + ".ensemble").withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable("airain.armure." + k + ".bonus").withStyle(ChatFormatting.GRAY));
		if (palier == 2 && getType() == Type.HELMET)
			l.add(Component.translatable("airain.armure.imperiale.couronne").withStyle(ChatFormatting.GRAY));
	}

	/** L'armure impériale a son propre modèle, peint sur une seule texture. */
	@Override
	public ResourceLocation getArmorTexture(ItemStack s, Entity e, EquipmentSlot slot, ArmorMaterial.Layer couche, boolean interieur) {
		return palier == 2 ? ResourceLocation.fromNamespaceAndPath("airain", "textures/models/armor/imperiale.png") : null;
	}

	/** Palier porté à cet emplacement : 2 impérial, 1 sacré (le casque couronné sacré compte), 0 sinon. */
	public static int palier(ItemStack s) {
		if (s.getItem() instanceof ArmureItem a) return a.palier;
		if (s.getItem() instanceof fr.chatmort.airain.gardien.CouronneItem && s.is(fr.chatmort.airain.AirainMod.CASQUE_COURONNE.get())
			&& fr.chatmort.airain.Sacre.sacree(s)) return 1;
		return 0;
	}

	public static boolean casqueImperial(ItemStack s) { return s.getItem() instanceof ArmureItem a && a.palier == 2 && a.getType() == Type.HELMET; }
}
