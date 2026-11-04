package fr.chatmort.airain.borne;

import java.util.List;

import com.mojang.serialization.MapCodec;

import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.armure.Lignee;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
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
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Borne de commande de fin de partie : machine différentielle (Empire) ou archive résonante (Écho).
 * Le cœur porte le modèle (borne + décors latéraux) et le block entity ; les autres cases sont des
 * {@link BornePartieBlock} : décors à gauche et à droite, étage, et la zone d'arrivage 3 x 3 devant la borne.
 */
public class BorneBlock extends HorizontalDirectionalBlock implements EntityBlock {
	public final boolean empire;

	public BorneBlock(boolean empire, Properties p) {
		super(p);
		this.empire = empire;
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	@Override
	protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return simpleCodec(p -> new BorneBlock(empire, p)); }

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }

	public Lignee lignee() { return empire ? Lignee.EMPIRE : Lignee.ECHO; }

	public Block partie() { return empire ? AirainMod.BORNE_PARTIE_IMPERIALE.get() : AirainMod.BORNE_PARTIE_ARCANIQUE.get(); }

	// ------------------------------------------------------------------ géométrie
	/** Cases autres que le cœur, en coordonnées locales (lx de -1 à 1, ly de 0 à 1, lz de 0 à -3 vers l'avant). */
	static final int[][] CASES;
	static {
		java.util.List<int[]> l = new java.util.ArrayList<>();
		for (int lx = -1; lx <= 1; lx++) for (int ly = 0; ly <= 1; ly++) if (lx != 0 || ly != 0) l.add(new int[]{lx, ly, 0});
		for (int lz = -1; lz >= -3; lz--) for (int lx = -1; lx <= 1; lx++) l.add(new int[]{lx, 0, lz});
		CASES = l.toArray(new int[0][]);
	}

	/** Passe du repère de la borne (avant = -z quand elle regarde au nord) au monde. */
	public static BlockPos monde(BlockPos coeur, Direction f, int lx, int ly, int lz) {
		int dx, dz;
		switch (f) {
			case EAST -> { dx = -lz; dz = lx; }
			case SOUTH -> { dx = -lx; dz = -lz; }
			case WEST -> { dx = lz; dz = -lx; }
			default -> { dx = lx; dz = lz; }
		}
		return coeur.offset(dx, ly, dz);
	}

	/** Centre de la zone d'arrivage. */
	public static BlockPos zone(BlockPos coeur, Direction f) { return monde(coeur, f, 0, 0, -2); }

	// ------------------------------------------------------------------ pose / retrait
	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		Level l = ctx.getLevel();
		BlockPos pos = ctx.getClickedPos();
		Direction f = ctx.getHorizontalDirection().getOpposite();
		if (pos.getY() + 2 > l.getMaxBuildHeight()) return refus(ctx);
		for (int[] c : CASES) if (!l.getBlockState(monde(pos, f, c[0], c[1], c[2])).canBeReplaced(ctx)) return refus(ctx);
		return defaultBlockState().setValue(FACING, f);
	}

	private BlockState refus(BlockPlaceContext ctx) {
		if (ctx.getPlayer() != null && !ctx.getLevel().isClientSide)
			ctx.getPlayer().displayClientMessage(Component.translatable("airain.borne.place"), true);
		return null;
	}

	@Override
	public void setPlacedBy(Level l, BlockPos pos, BlockState s, LivingEntity qui, ItemStack pile) {
		if (l.isClientSide) return;
		if (!lignee().autorisee(l.getServer())) {
			l.destroyBlock(pos, !(qui instanceof Player p && p.isCreative()));
			if (qui instanceof Player p) p.displayClientMessage(Component.translatable("airain.borne.refus_" + lignee().cle()), true);
			return;
		}
		Direction f = s.getValue(FACING);
		for (int[] c : CASES)
			l.setBlock(monde(pos, f, c[0], c[1], c[2]), partie().defaultBlockState().setValue(BornePartieBlock.FACING, f)
				.setValue(BornePartieBlock.PX, c[0] + 1).setValue(BornePartieBlock.PY, c[1]).setValue(BornePartieBlock.PZ, -c[2]), 3);
	}

	@Override
	protected void onRemove(BlockState s, Level l, BlockPos pos, BlockState n, boolean deplace) {
		if (!s.is(n.getBlock()) && !l.isClientSide) {
			if (l.getBlockEntity(pos) instanceof BorneBlockEntity be) be.rendre();
			Direction f = s.getValue(FACING);
			for (int[] c : CASES) {
				BlockPos p = monde(pos, f, c[0], c[1], c[2]);
				if (l.getBlockState(p).getBlock() instanceof BornePartieBlock)
					l.setBlock(p, Blocks.AIR.defaultBlockState(), 3 | Block.UPDATE_SUPPRESS_DROPS);
			}
		}
		super.onRemove(s, l, pos, n, deplace);
	}

	// ------------------------------------------------------------------ usage
	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos pos, Player p, BlockHitResult h) {
		return ouvrir(l, pos, p);
	}

	static InteractionResult ouvrir(Level l, BlockPos coeur, Player p) {
		if (l.isClientSide) return InteractionResult.SUCCESS;
		if (p instanceof ServerPlayer sp && l.getBlockEntity(coeur) instanceof BorneBlockEntity be) be.ouvrir(sp);
		return InteractionResult.CONSUME;
	}

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return Shapes.block(); }

	@Override
	public void appendHoverText(ItemStack s, Item.TooltipContext c, List<Component> l, TooltipFlag f) {
		String k = empire ? "borne_imperiale" : "borne_arcanique";
		for (int i = 1; i <= 3; i++) l.add(Component.translatable("block.airain." + k + ".l" + i)
			.withStyle(i == 1 ? (empire ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE) : ChatFormatting.GRAY));
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new BorneBlockEntity(pos, state); }

	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
		if (l.isClientSide || t != AirainMod.BORNE_BE.get()) return null;
		return (lv, p, st, be) -> ((BorneBlockEntity) be).tick();
	}
}
