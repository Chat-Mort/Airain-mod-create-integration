package fr.chatmort.airain.gardien;

import java.util.List;

import fr.chatmort.airain.AirainMod;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.event.AnvilUpdateEvent;

/** La couronne d'airain, et le casque couronné (couronne montée sur un casque de netherite, à l'enclume). */
public class CouronneItem extends ArmorItem {
	public static final int COUT_ENCLUME = 5;
	private final boolean casque;

	public CouronneItem(Holder<ArmorMaterial> materiau, boolean casque, Item.Properties p) {
		super(materiau, Type.HELMET, p);
		this.casque = casque;
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		for (int i = 1; i <= 4; i++) l.add(Component.translatable("item.airain.couronne_airain.l" + i).withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable(casque ? "item.airain.casque_couronne.separer" : "item.airain.couronne_airain.enclume").withStyle(ChatFormatting.DARK_GRAY));
	}

	/** Accroupi + clic droit avec le casque couronné : la couronne se détache, le casque de netherite garde ses enchantements. */
	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack pile = p.getItemInHand(main);
		if (!casque || !p.isShiftKeyDown()) return super.use(level, p, main);
		if (!level.isClientSide) {
			ItemStack netherite = new ItemStack(Items.NETHERITE_HELMET);
			netherite.applyComponents(pile.getComponentsPatch());
			p.setItemInHand(main, netherite);
			p.getInventory().placeItemBackInInventory(new ItemStack(AirainMod.COURONNE.get()));
			level.playSound(null, p.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE.value(), SoundSource.PLAYERS, 1f, 0.8f);
		}
		return InteractionResultHolder.sidedSuccess(p.getItemInHand(main), level.isClientSide);
	}

	/** Enclume : casque de netherite à gauche, couronne à droite → casque couronné (enchantements, usure et nom conservés). */
	public static void enclume(AnvilUpdateEvent e) {
		if (!e.getLeft().is(Items.NETHERITE_HELMET) || !e.getRight().is(AirainMod.COURONNE.get())) return;
		ItemStack sortie = new ItemStack(AirainMod.CASQUE_COURONNE.get());
		sortie.applyComponents(e.getLeft().getComponentsPatch());
		String nom = e.getName();
		if (nom != null && !nom.isBlank() && !nom.equals(e.getLeft().getHoverName().getString()))
			sortie.set(DataComponents.CUSTOM_NAME, Component.literal(nom));
		e.setOutput(sortie);
		e.setCost(COUT_ENCLUME);
		e.setMaterialCost(1);
	}
}
