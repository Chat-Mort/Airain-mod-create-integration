package fr.chatmort.airain.comptoir;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.saveddata.maps.MapDecorationTypes;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;

/**
 * Carte de l'Empire (vendue par le cartographe) : au clic droit, elle devient une carte au trésor vers la structure
 * de ce type la plus proche. La cible est dans custom_data : {cible:"avant_poste"} → tag airain:carte/avant_poste.
 */
public class CarteItem extends Item {
	public CarteItem(Properties p) { super(p); }

	public static String cible(ItemStack s) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d == null ? "" : d.copyTag().getString("cible");
	}

	@Override
	public Component getName(ItemStack s) {
		String c = cible(s);
		return c.isEmpty() ? super.getName(s) : Component.translatable("item.airain.carte_empire.nom", Component.translatable("airain.carte." + c));
	}

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack pile = p.getItemInHand(main);
		String c = cible(pile);
		if (c.isEmpty() || !(level instanceof ServerLevel sl)) return InteractionResultHolder.sidedSuccess(pile, level.isClientSide);
		TagKey<Structure> tag = TagKey.create(Registries.STRUCTURE, ResourceLocation.fromNamespaceAndPath("airain", "carte/" + c));
		BlockPos cible = sl.findNearestMapStructure(tag, p.blockPosition(), 100, false);
		if (cible == null) {
			p.displayClientMessage(Component.translatable("airain.carte.introuvable"), true);
			return InteractionResultHolder.fail(pile);
		}
		ItemStack carte = MapItem.create(sl, cible.getX(), cible.getZ(), (byte) 2, true, true);
		MapItem.renderBiomePreviewMap(sl, carte);
		MapItemSavedData.addTargetDecoration(carte, cible, "+", MapDecorationTypes.RED_X);
		carte.set(DataComponents.CUSTOM_NAME, Component.translatable("item.airain.carte_empire.nom", Component.translatable("airain.carte." + c))
			.withStyle(s -> s.withItalic(false)));
		sl.playSound(null, p.blockPosition(), SoundEvents.UI_CARTOGRAPHY_TABLE_TAKE_RESULT, SoundSource.PLAYERS, 1f, 1f);
		if (pile.getCount() == 1) return InteractionResultHolder.consume(carte);
		pile.shrink(1);
		if (!p.getInventory().add(carte)) p.drop(carte, false);
		return InteractionResultHolder.consume(pile);
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, java.util.List<Component> l, TooltipFlag f) {
		l.add(Component.translatable("airain.carte.aide").withStyle(ChatFormatting.GRAY));
	}
}
