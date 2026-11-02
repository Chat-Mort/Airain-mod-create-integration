package fr.chatmort.airain.comptoir;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;

/**
 * Plan de l'Empire (bureau d'études) : au clic droit, il devient un schéma de Create, prêt pour le canon à schémas.
 * Les fichiers sont livrés avec le pack : schematics/uploaded/airain/airain_<plan>.nbt (serveur) et schematics/airain_<plan>.nbt (client).
 */
public class PlanItem extends Item {
	public static final String PROPRIETAIRE = "airain";

	public PlanItem(Properties p) { super(p); }

	public static String plan(ItemStack s) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d == null ? "" : d.copyTag().getString("plan");
	}

	@Override
	public Component getName(ItemStack s) {
		String c = plan(s);
		return c.isEmpty() ? super.getName(s) : Component.translatable("item.airain.plan.nom", Component.translatable("airain.plan." + c));
	}

	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack pile = p.getItemInHand(main);
		String c = plan(pile);
		if (c.isEmpty() || level.isClientSide) return InteractionResultHolder.sidedSuccess(pile, level.isClientSide);
		ItemStack schema = com.simibubi.create.content.schematics.SchematicItem.create(
			level, "airain_" + c + ".nbt", PROPRIETAIRE);
		schema.set(DataComponents.CUSTOM_NAME, Component.translatable("item.airain.plan.nom", Component.translatable("airain.plan." + c)).withStyle(s -> s.withItalic(false)));
		level.playSound(null, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.8f);
		if (pile.getCount() == 1) return InteractionResultHolder.consume(schema);
		pile.shrink(1);
		if (!p.getInventory().add(schema)) p.drop(schema, false);
		return InteractionResultHolder.consume(pile);
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext ctx, java.util.List<Component> l, TooltipFlag f) {
		String c = plan(s);
		if (!c.isEmpty()) l.add(Component.translatable("airain.plan." + c + ".desc").withStyle(ChatFormatting.GRAY));
		l.add(Component.translatable("airain.plan.aide").withStyle(ChatFormatting.DARK_GRAY));
	}
}
