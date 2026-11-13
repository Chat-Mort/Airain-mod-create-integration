package fr.chatmort.airain.fonderie;

import com.mojang.serialization.MapCodec;
import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;

/** Les blocs du haut-fourneau impérial (structure de 3 × 3 × 4, voir HautFourneauBlockEntity). */
public final class FourneauBlocs {
	private FourneauBlocs() {}

	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	public static final BooleanProperty LIT = BlockStateProperties.LIT;

	/** Place d'une brique dans le fourneau monté : elle change d'habillage (socle riveté, cornières, couronne, blason). */
	public enum Partie implements StringRepresentable {
		AUCUNE("none"), SOCLE("base"), SOCLE_COIN("base_corner"), CORPS("body"), CORPS_COIN("body_corner"),
		COURONNE("crown"), COURONNE_COIN("crown_corner"), BLASON("emblem");
		private final String nom;
		Partie(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public static final EnumProperty<Partie> PARTIE = EnumProperty.create("part", Partie.class);

	// ---- briques réfractaires
	public static class Briques extends Block {
		public Briques(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(PARTIE, Partie.AUCUNE).setValue(FACING, Direction.NORTH)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(PARTIE, FACING); }
	}

	// ---- tuyère : la buse où souffle le ventilateur (FACING = vers l'extérieur)
	public static class Tuyere extends HorizontalDirectionalBlock {
		public static final MapCodec<Tuyere> CODEC = simpleCodec(Tuyere::new);
		public Tuyere(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH)); }
		@Override protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }
	}

	// ---- gueulard : l'entonnoir du sommet, où l'on verse la charge
	public static class Gueulard extends Block {
		public Gueulard(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(LIT, false)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(LIT); }
	}

	// ---- trou de coulée : le cœur du fourneau (son bloc-entité fait tout le travail)
	public static class TrouCoulee extends BaseEntityBlock {
		public static final MapCodec<TrouCoulee> CODEC = simpleCodec(TrouCoulee::new);
		public TrouCoulee(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(LIT, false)); }
		@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, LIT); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new HautFourneauBlockEntity(p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> type) {
			if (type != Fourneau.BE.get()) return null;
			return l.isClientSide ? (lv, p, st, be) -> ((HautFourneauBlockEntity) be).tickClient()
				: (lv, p, st, be) -> ((HautFourneauBlockEntity) be).tickServeur();
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!l.isClientSide && l.getBlockEntity(p) instanceof HautFourneauBlockEntity be) be.clic(j);
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof HautFourneauBlockEntity be) be.demonter();
			super.onRemove(s, l, p, n, deplace);
		}
	}
	@SuppressWarnings("unused") private static final Class<?> M = AirainMod.class;
}
