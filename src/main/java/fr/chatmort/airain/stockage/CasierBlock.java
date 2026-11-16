package fr.chatmort.airain.stockage;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * 1.62 : le casier du rayonnage impérial. Les casiers voisins se raccordent (montants en bout de rang, entretoises,
 * couronnement en haut) et forment un seul inventaire qui range chaque objet dans le casier qui le contient déjà.
 * Main : clic droit avec un objet pour déposer (deux fois vite : tout déposer), clic gauche pour prendre une pile
 * (accroupi : une seule). Clé : réserver le casier à son objet. Renfort en main : capacité doublée.
 */
public class CasierBlock extends Block implements EntityBlock, IWrenchable {
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	/** Pas de casier à gauche / à droite (vu de face) : montants et entretoises de bout ; rien au-dessus : couronnement. */
	public static final BooleanProperty BOUT_G = BooleanProperty.create("left_end"), BOUT_D = BooleanProperty.create("right_end"), SOMMET = BooleanProperty.create("top");
	private static final VoxelShape FORME = Shapes.or(Block.box(0, 0, 0, 16, 3, 16), Block.box(0, 3, 0, 1.5, 16, 16), Block.box(14.5, 3, 0, 16, 16, 16));

	public CasierBlock(Properties p) {
		super(p);
		registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(BOUT_G, true).setValue(BOUT_D, true).setValue(SOMMET, true));
	}
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, BOUT_G, BOUT_D, SOMMET); }
	/** La droite de celui qui regarde le casier. */
	static Direction droite(Direction f) { return f.getCounterClockWise(); }
	private static BlockState ajuster(BlockState s, LevelAccessor l, BlockPos p) {
		Direction f = s.getValue(FACING), d = droite(f);
		return s.setValue(BOUT_G, !(l.getBlockState(p.relative(d.getOpposite())).getBlock() instanceof CasierBlock))
			.setValue(BOUT_D, !(l.getBlockState(p.relative(d)).getBlock() instanceof CasierBlock))
			.setValue(SOMMET, !(l.getBlockState(p.above()).getBlock() instanceof CasierBlock));
	}
	@Override
	public BlockState getStateForPlacement(BlockPlaceContext c) {
		return ajuster(defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()), c.getLevel(), c.getClickedPos());
	}
	@Override
	protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
		Reseau.changement();
		return ajuster(s, l, p);
	}
	@Override protected void onPlace(BlockState s, Level l, BlockPos p, BlockState a, boolean m) { Reseau.changement(); super.onPlace(s, l, p, a, m); }
	@Override protected BlockState rotate(BlockState s, Rotation r) { return s.setValue(FACING, r.rotate(s.getValue(FACING))); }
	@Override protected BlockState mirror(BlockState s, Mirror m) { return s.rotate(m.getRotation(s.getValue(FACING))); }
	@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return Shapes.block(); }
	@Override protected VoxelShape getCollisionShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return Shapes.block(); }
	@Override protected VoxelShape getVisualShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new CasierBlockEntity(Rayonnage.BE.get(), p, s); }

	// ---------------------------------------------------------------- mains
	@Override
	protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand h, BlockHitResult hit) {
		if (!(l.getBlockEntity(p) instanceof CasierBlockEntity c)) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (st.getItem() instanceof RenfortItem r) {
			if (!l.isClientSide) c.renforcer(j, st, r.niveau);
			return ItemInteractionResult.sidedSuccess(l.isClientSide);
		}
		if (st.getItem() instanceof com.simibubi.create.content.equipment.wrench.WrenchItem) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (!l.isClientSide) c.deposer(j, h);
		return ItemInteractionResult.sidedSuccess(l.isClientSide);
	}
	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult hit) {
		if (!l.isClientSide && l.getBlockEntity(p) instanceof CasierBlockEntity c) c.deposer(j, null);   // double clic main nue : tout déposer
		return InteractionResult.sidedSuccess(l.isClientSide);
	}
	@Override
	protected void attack(BlockState s, Level l, BlockPos p, Player j) {
		if (!l.isClientSide && l.getBlockEntity(p) instanceof CasierBlockEntity c) c.prendre(j, j.isShiftKeyDown());
	}
	/** Clé de Create : réserver le casier à son objet (ou le libérer). Accroupi : démonter, avec son contenu. */
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		if (!c.getLevel().isClientSide && c.getLevel().getBlockEntity(c.getClickedPos()) instanceof CasierBlockEntity e) e.verrouiller(c.getPlayer());
		return InteractionResult.SUCCESS;
	}
	@Override
	public void setPlacedBy(Level l, BlockPos p, BlockState s, LivingEntity e, ItemStack st) { super.setPlacedBy(l, p, s, e, st); Reseau.changement(); }
	@Override
	protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean m) { Reseau.changement(); super.onRemove(s, l, p, n, m); }
}
