package fr.chatmort.airain.fondation;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * Gabarit de bannière : accroupi + clic droit sur un étendard ou une bannière murale copie son apparence ;
 * clic droit sur un autre l'y applique, mode décoratif compris (le nom et la devise de la cible sont conservés ;
 * seul un grand étendard peut être décoratif).
 */
public class GabaritItem extends Item {
	public GabaritItem(Properties p) {
		super(p);
	}

	private static CompoundTag donnees(ItemStack s) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d == null ? null : d.copyTag();
	}

	@Override
	public InteractionResult useOn(UseOnContext ctx) {
		Level level = ctx.getLevel();
		BlockPos porte = FondationBlockEntity.porte(level, ctx.getClickedPos());
		if (porte == null || !(level.getBlockEntity(porte) instanceof FondationBlockEntity f)) return InteractionResult.PASS;
		if (level.isClientSide) return InteractionResult.SUCCESS;
		Player p = ctx.getPlayer();
		ItemStack s = ctx.getItemInHand();
		CompoundTag d = donnees(s);
		if (p != null && p.isShiftKeyDown()) {
			CompoundTag t = new CompoundTag();
			t.putInt("apparence", f.apparence().pack()); t.putInt("ext", f.apparence().packExt()); t.putInt("hauteur", f.hauteur());
			s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
			p.displayClientMessage(Component.translatable("airain.gabarit.copie").withStyle(ChatFormatting.GOLD), true);
			level.playSound(null, porte, SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8f, 1.1f);
			return InteractionResult.CONSUME;
		}
		if (d == null || !d.contains("apparence")) {
			if (p != null) p.displayClientMessage(Component.translatable("airain.gabarit.vide").withStyle(ChatFormatting.GRAY), true);
			return InteractionResult.CONSUME;
		}
		int[] v = Apparence.unpack(d.getInt("apparence"), d.getInt("ext")).valeurs();
		if (f.grand() && d.contains("hauteur") && d.getInt("hauteur") != f.hauteur())
			GrandEtendardBlock.changerHauteur(level, porte, f.hauteur(), d.getInt("hauteur"));
		f.configurer(f.nom(), f.devise(), Apparence.depuis(v));
		if (p != null) p.displayClientMessage(Component.translatable("airain.gabarit.applique").withStyle(ChatFormatting.GOLD), true);
		level.playSound(null, porte, SoundEvents.WOOL_PLACE, SoundSource.BLOCKS, 0.8f, 1f);
		return InteractionResult.CONSUME;
	}

	@Override
	public boolean isFoil(ItemStack s) {
		CompoundTag d = donnees(s);
		return d != null && d.contains("apparence");
	}

	@Override
	public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> lignes, TooltipFlag f) {
		CompoundTag d = donnees(s);
		lignes.add(Component.translatable(d != null && d.contains("apparence") ? "airain.gabarit.plein" : "airain.gabarit.aide")
			.withStyle(ChatFormatting.GRAY));
	}
}
