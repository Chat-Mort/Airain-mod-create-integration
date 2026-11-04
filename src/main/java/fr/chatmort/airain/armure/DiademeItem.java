package fr.chatmort.airain.armure;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.event.AnvilUpdateEvent;

/** Le diadème d'Écho (récompense de la fin Écho), porté seul, ou monté à l'enclume sur un casque de netherite : le casque au diadème. */
public class DiademeItem extends ArmorItem {
	private final boolean casque;

	public DiademeItem(Holder<ArmorMaterial> m, boolean casque, Properties p) { super(m, Type.HELMET, p); this.casque = casque; }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		if (casque) {                                             // présenté comme les autres pièces de la lignée
			l.add(Component.translatable("airain.lignee.echo").withStyle(ChatFormatting.DARK_RED, ChatFormatting.ITALIC));
			l.add(Component.translatable("airain.diademe.effet").withStyle(ChatFormatting.GOLD));
			l.add(Component.translatable("airain.diademe.l1").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
		} else {
			l.add(Component.translatable("airain.lignee.echo").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
			l.add(Component.translatable("airain.diademe.l1").withStyle(ChatFormatting.LIGHT_PURPLE));
			l.add(Component.translatable("airain.diademe.effet").withStyle(ChatFormatting.GRAY));
		}
		l.add(Component.translatable(casque ? "item.airain.diadem_helmet.separer" : "item.airain.echo_diadem.enclume").withStyle(ChatFormatting.DARK_GRAY));
	}

	@Override
	public ResourceLocation getArmorTexture(ItemStack s, Entity e, EquipmentSlot slot, ArmorMaterial.Layer couche, boolean interieur) {
		return casque ? ResourceLocation.fromNamespaceAndPath("airain", "textures/models/armor/echo_headpieces.png") : null;
	}

	/** Accroupi + clic droit avec le casque au diadème : le diadème se détache, le casque de netherite garde ses enchantements. */
	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		if (!casque || !p.isShiftKeyDown()) return super.use(level, p, main);
		if (!level.isClientSide) {
			ItemStack netherite = new ItemStack(Items.NETHERITE_HELMET);
			netherite.applyComponents(p.getItemInHand(main).getComponentsPatch());
			p.setItemInHand(main, netherite);
			p.getInventory().placeItemBackInInventory(new ItemStack(fr.chatmort.airain.AirainMod.DIADEME.get()));
			level.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1f, 0.8f);
		}
		return InteractionResultHolder.sidedSuccess(p.getItemInHand(main), level.isClientSide);
	}

	/** Enclume : casque de netherite à gauche, diadème à droite → casque au diadème (enchantements, usure et nom conservés). */
	public static void enclume(AnvilUpdateEvent e) {
		if (!e.getLeft().is(Items.NETHERITE_HELMET) || !e.getRight().is(fr.chatmort.airain.AirainMod.DIADEME.get())) return;
		ItemStack sortie = new ItemStack(fr.chatmort.airain.AirainMod.CASQUE_DIADEME.get());
		sortie.applyComponents(e.getLeft().getComponentsPatch());
		String nom = e.getName();
		if (nom != null && !nom.isBlank() && !nom.equals(e.getLeft().getHoverName().getString()))
			sortie.set(DataComponents.CUSTOM_NAME, Component.literal(nom));
		e.setOutput(sortie);
		e.setCost(fr.chatmort.airain.gardien.CouronneItem.COUT_ENCLUME);
		e.setMaterialCost(1);
	}
}
