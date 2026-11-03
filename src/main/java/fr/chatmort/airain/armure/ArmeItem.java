package fr.chatmort.airain.armure;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.level.Level;

/** Armes sacrées (palier 1) et impériales (palier 2) : épée, katana, espadon, twinblade. */
public class ArmeItem extends SwordItem {
	public enum Type { EPEE, KATANA, ESPADON, TWINBLADE }
	public final Type type;
	public final int palier;

	public ArmeItem(Tier tier, Type type, int palier, Properties p) {
		super(tier, p);
		this.type = type;
		this.palier = palier;
	}

	/** Dégâts et vitesse finaux, portée et recul ajoutés. */
	public static ItemAttributeModifiers stats(double degats, double vitesse, double portee, double recul, double balayage) {
		var b = ItemAttributeModifiers.builder()
			.add(Attributes.ATTACK_DAMAGE, new AttributeModifier(BASE_ATTACK_DAMAGE_ID, degats - 1, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
			.add(Attributes.ATTACK_SPEED, new AttributeModifier(BASE_ATTACK_SPEED_ID, vitesse - 4, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND);
		if (portee != 0) b.add(Attributes.ENTITY_INTERACTION_RANGE, new AttributeModifier(id("portee"), portee, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND);
		if (recul != 0) b.add(Attributes.ATTACK_KNOCKBACK, new AttributeModifier(id("recul"), recul, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND);
		if (balayage != 0) b.add(Attributes.SWEEPING_DAMAGE_RATIO, new AttributeModifier(id("balayage"), balayage, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND);
		return b.build();
	}

	static ResourceLocation id(String n) { return ResourceLocation.fromNamespaceAndPath("airain", "arme_" + n); }

	@Override
	public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
		String k = "airain.arme." + type.name().toLowerCase(java.util.Locale.ROOT);
		l.add(Component.translatable(k + ".nom").withStyle(ChatFormatting.GOLD));
		l.add(Component.translatable(k + ".effet" + palier).withStyle(ChatFormatting.GRAY));
		if (type == Type.KATANA) l.add(Component.translatable("airain.arme.katana.souffle" + palier).withStyle(ChatFormatting.GRAY));
	}

	@Override
	public boolean hurtEnemy(ItemStack s, LivingEntity cible, LivingEntity porteur) {
		if (porteur instanceof ServerPlayer p && cible.level() instanceof ServerLevel sl && Armes.autorise(p, palier)) {
			if (type == Type.EPEE) Armes.jugement(sl, p, cible, palier);
			else if (type == Type.TWINBLADE) Armes.doubleCoup(p, cible, palier);
		}
		return super.hurtEnemy(s, cible, porteur);
	}

	// ---- clic droit : ruée (katana), fracas (espadon, à charger), tourbillon (twinblade impériale)
	@Override
	public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
		ItemStack s = p.getItemInHand(main);
		if (main != InteractionHand.MAIN_HAND) return InteractionResultHolder.pass(s);
		if (!level.isClientSide && !Armes.autorise(p, palier)) return InteractionResultHolder.fail(s);
		switch (type) {
			case KATANA -> {
				if (!level.isClientSide) Armes.iai((ServerPlayer) p, this, palier);
				return InteractionResultHolder.sidedSuccess(s, level.isClientSide);
			}
			case ESPADON -> { p.startUsingItem(main); return InteractionResultHolder.consume(s); }
			case TWINBLADE -> {
				if (palier < 2) return InteractionResultHolder.pass(s);
				if (!level.isClientSide) Armes.tourbillon((ServerPlayer) p, this);
				return InteractionResultHolder.sidedSuccess(s, level.isClientSide);
			}
			default -> { return InteractionResultHolder.pass(s); }
		}
	}

	@Override
	public UseAnim getUseAnimation(ItemStack s) { return type == Type.ESPADON ? UseAnim.SPEAR : UseAnim.NONE; }

	@Override
	public int getUseDuration(ItemStack s, LivingEntity e) { return type == Type.ESPADON ? 72000 : 0; }

	@Override
	public void releaseUsing(ItemStack s, Level level, LivingEntity e, int reste) {
		if (type != Type.ESPADON || !(e instanceof ServerPlayer p)) return;
		if (getUseDuration(s, e) - reste >= 15) Armes.fracas(p, this, palier);
	}
}
