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

/** Pièce d'armure de fin de partie : Empire (sacrée 1, impériale 2) ou Écho (runique 1, arcanique 2). */
public class ArmureItem extends ArmorItem {
	public final int palier;
	public final Lignee lignee;

	public ArmureItem(Holder<ArmorMaterial> m, Type type, int palier, Properties p) { this(m, type, palier, Lignee.EMPIRE, p); }

	public ArmureItem(Holder<ArmorMaterial> m, Type type, int palier, Lignee lignee, Properties p) {
		super(m, type, p);
		this.palier = palier;
		this.lignee = lignee;
	}

	public String nomPalier() { return lignee == Lignee.EMPIRE ? (palier == 2 ? "imperiale" : "sacree") : (palier == 2 ? "arcanique" : "runique"); }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.lignee." + lignee.cle()).withStyle(ChatFormatting.DARK_RED, ChatFormatting.ITALIC));
		String k = nomPalier();
		l.add(Component.translatable("airain.armure." + k + ".ensemble").withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable("airain.armure." + k + ".bonus").withStyle(ChatFormatting.GRAY));
		if (lignee == Lignee.ECHO && getType() == Type.HELMET)
			l.add(Component.translatable("airain.diademe.effet").withStyle(ChatFormatting.GRAY));
		if (lignee == Lignee.EMPIRE && palier == 2 && getType() == Type.HELMET)
			l.add(Component.translatable("airain.armure.imperiale.couronne").withStyle(ChatFormatting.GRAY));
		if (palier == 2 && getType() == Type.HELMET)
			l.add(Component.translatable("airain.armure.vol").withStyle(ChatFormatting.AQUA));
	}

	/** L'armure impériale a son propre modèle, peint sur une seule texture. */
	@Override
	public ResourceLocation getArmorTexture(ItemStack s, Entity e, EquipmentSlot slot, ArmorMaterial.Layer couche, boolean interieur) {
		if (palier < 2) return null;
		return ResourceLocation.fromNamespaceAndPath("airain", "textures/models/armor/" + (lignee == Lignee.EMPIRE ? "imperiale" : "arcanique") + ".png");
	}

	/** Palier de la lignée porté à cet emplacement (le casque couronné sacré compte pour l'Empire), 0 sinon. */
	public static int palier(ItemStack s, Lignee l) {
		if (s.getItem() instanceof ArmureItem a) return a.lignee == l ? a.palier : 0;
		if (l != Lignee.EMPIRE) return 0;
		if (s.getItem() instanceof fr.chatmort.airain.gardien.CouronneItem && s.is(fr.chatmort.airain.AirainMod.CASQUE_COURONNE.get())
			&& fr.chatmort.airain.Sacre.sacree(s)) return 1;
		return 0;
	}

	public static boolean casqueImperial(ItemStack s) { return s.getItem() instanceof ArmureItem a && a.lignee == Lignee.EMPIRE && a.palier == 2 && a.getType() == Type.HELMET; }

	/** Le diadème d'Écho, seul ou monté sur un casque de la lignée de l'Écho. */
	public static boolean diademe(ItemStack s) {
		return s.getItem() instanceof DiademeItem || (s.getItem() instanceof ArmureItem a && a.lignee == Lignee.ECHO && a.getType() == Type.HELMET);
	}
}
