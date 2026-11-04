package fr.chatmort.airain.borne;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Une case de la borne autre que le cœur. PX (lx + 1), PY, PZ (-lz) : position dans le repère de la borne.
 * La case (1, 0, 2) dessine la zone d'arrivage entière ; les autres sont invisibles.
 */
public class BornePartieBlock extends Block {
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	public static final IntegerProperty PX = IntegerProperty.create("px", 0, 2);
	public static final IntegerProperty PY = IntegerProperty.create("py", 0, 1);
	public static final IntegerProperty PZ = IntegerProperty.create("pz", 0, 3);
	private static final VoxelShape DALLE = Block.box(0, 0, 0, 16, 2, 16);
	private static final VoxelShape HAUT = Block.box(0, 0, 0, 16, 12, 16);
	private static final VoxelShape COTE_HAUT = Block.box(3, 0, 3, 13, 15, 13);
	public final boolean empire;

	public BornePartieBlock(boolean empire, Properties p) {
		super(p);
		this.empire = empire;
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(PX, 0).setValue(PY, 0).setValue(PZ, 0));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, PX, PY, PZ); }

	public static BlockPos coeur(BlockState s, BlockPos pos) {
		Direction f = s.getValue(FACING);
		BlockPos o = BorneBlock.monde(BlockPos.ZERO, f, s.getValue(PX) - 1, s.getValue(PY), -s.getValue(PZ));
		return pos.subtract(o);
	}

	public static boolean zone(BlockState s) { return s.getValue(PZ) > 0; }

	private Block borne() { return empire ? AirainMod.BORNE_IMPERIALE.get() : AirainMod.BORNE_ARCANIQUE.get(); }

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos pos, CollisionContext c) {
		if (zone(s)) return DALLE;
		if (s.getValue(PY) == 0) return Shapes.block();
		return s.getValue(PX) == 1 ? HAUT : COTE_HAUT;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos pos, Player p, BlockHitResult h) {
		if (zone(s)) return InteractionResult.PASS;
		return BorneBlock.ouvrir(l, coeur(s, pos), p);
	}

	@Override
	public BlockState playerWillDestroy(Level l, BlockPos pos, BlockState s, Player p) {
		BlockPos c = coeur(s, pos);
		if (!l.isClientSide && l.getBlockState(c).is(borne())) l.destroyBlock(c, !p.isCreative(), p);
		return super.playerWillDestroy(l, pos, s, p);
	}

	@Override
	public ItemStack getCloneItemStack(BlockState s, HitResult h, LevelReader l, BlockPos pos, Player p) { return new ItemStack(borne()); }

	@Override
	protected void tick(BlockState s, ServerLevel l, BlockPos pos, RandomSource r) {
		if (!l.getBlockState(coeur(s, pos)).is(borne())) l.removeBlock(pos, false);
	}

	@Override
	protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos pos, BlockPos pv) {
		l.scheduleTick(pos, this, 2);
		return s;
	}

	@Override
	protected boolean propagatesSkylightDown(BlockState s, BlockGetter l, BlockPos p) { return true; }

	@Override
	protected float getShadeBrightness(BlockState s, BlockGetter l, BlockPos p) { return 1f; }
}
