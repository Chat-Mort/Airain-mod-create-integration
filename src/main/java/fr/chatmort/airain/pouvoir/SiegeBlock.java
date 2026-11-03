package fr.chatmort.airain.pouvoir;

import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import com.mojang.serialization.MapCodec;

import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.armure.Lignee;
import fr.chatmort.airain.fondation.FondationRegistre;

/** Trône impérial / solium de la Prêtresse : un seul par monde, dans une base sacrée, réservé à sa fin. */
public class SiegeBlock extends HorizontalDirectionalBlock {
	private static final VoxelShape FORME = Block.box(0, 0, 0, 16, 10, 16);
	public final boolean trone;

	public SiegeBlock(boolean trone, Properties p) {
		super(p);
		this.trone = trone;
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	@Override
	protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return simpleCodec(p -> new SiegeBlock(trone, p)); }

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }

	public Lignee lignee() { return trone ? Lignee.EMPIRE : Lignee.ECHO; }

	/** Pose : fin, base sacrée, unicité. Sinon le bloc retombe. */
	@Override
	public void setPlacedBy(Level l, BlockPos pos, BlockState s, LivingEntity qui, ItemStack pile) {
		if (!(l instanceof ServerLevel sl)) return;
		String refus = null;
		Pouvoir pv = Pouvoir.de(sl.getServer());
		var f = FondationRegistre.de(sl.getServer()).zone(sl.dimension().location(), pos.getX() + 0.5, pos.getZ() + 0.5);
		if (!lignee().autorisee(sl.getServer())) refus = "airain.siege.refus_fin_" + lignee().cle();
		else if (f == null || !f.sacree()) refus = "airain.siege.refus_base";
		else if (pv.present() && !(pv.dim.equals(sl.dimension().location()) && pv.pos.equals(pos))) refus = "airain.siege.refus_unique";
		if (refus != null) {
			l.destroyBlock(pos, true);
			if (qui instanceof Player p) p.displayClientMessage(Component.translatable(refus), true);
			return;
		}
		pv.poser(l, pos, trone);
		for (ServerPlayer p : sl.getServer().getPlayerList().getPlayers()) {
			Siege.reapparition(p, sl, pos, s);
			p.sendSystemMessage(Component.translatable(trone ? "airain.siege.pose_trone" : "airain.siege.pose_solium").withStyle(trone ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE));
		}
		sl.playSound(null, pos, trone ? SoundEvents.BEACON_ACTIVATE : SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1f, 0.7f);
	}

	@Override
	protected void onRemove(BlockState s, Level l, BlockPos pos, BlockState n, boolean deplace) {
		if (!s.is(n.getBlock()) && l instanceof ServerLevel sl) {
			Pouvoir pv = Pouvoir.de(sl.getServer());
			if (pv.present() && pv.pos.equals(pos) && pv.dim.equals(sl.dimension().location())) pv.retirer();
		}
		super.onRemove(s, l, pos, n, deplace);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos pos, Player p, BlockHitResult h) {
		if (l.isClientSide) return InteractionResult.SUCCESS;
		if (p.isPassenger() || !(p instanceof ServerPlayer sp)) return InteractionResult.PASS;
		if (!l.getEntitiesOfClass(Assise.class, new net.minecraft.world.phys.AABB(pos)).isEmpty()) return InteractionResult.PASS;
		Assise a = AirainMod.ASSISE.get().create(l);
		if (a == null) return InteractionResult.PASS;
		a.setPos(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5);
		a.setYRot(s.getValue(FACING).toYRot());
		l.addFreshEntity(a);
		p.startRiding(a, true);
		Siege.reapparition(sp, (ServerLevel) l, pos, s);
		Siege.menu(sp, trone);
		return InteractionResult.CONSUME;
	}

	@Override
	public void appendHoverText(ItemStack s, Item.TooltipContext c, List<Component> l, TooltipFlag f) {
		String k = trone ? "trone" : "solium";
		for (int i = 1; i <= 3; i++) l.add(Component.translatable("block.airain." + k + ".l" + i).withStyle(i == 1 ? ChatFormatting.GOLD : ChatFormatting.GRAY));
	}
}
