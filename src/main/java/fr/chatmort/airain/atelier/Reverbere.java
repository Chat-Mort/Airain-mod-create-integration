package fr.chatmort.airain.atelier;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Réverbère impérial : on empile autant de blocs qu'on veut ; le socle se pose seul en bas, la tête (lanterne rouge)
 * en haut. La clé de Create sur la tête passe d'une lanterne à deux (sur une traverse, dans l'axe de la pose).
 */
public class Reverbere extends BlocPatine implements IWrenchable {
	public static final BooleanProperty BAS = BooleanProperty.create("bottom");
	public static final BooleanProperty HAUT = BooleanProperty.create("top");
	public static final BooleanProperty DOUBLE = BooleanProperty.create("double");
	private static final VoxelShape FUT = Block.box(6.5, 0, 6.5, 9.5, 16, 9.5), SOCLE = Block.box(3, 0, 3, 13, 5, 13), TETE = Block.box(6, 10, 6, 10, 16, 10);
	public Reverbere(WeatherState etat, Properties p) {
		super(etat, p);
		registerDefaultState(defaultBlockState().setValue(BAS, true).setValue(HAUT, true).setValue(DOUBLE, false).setValue(BlockStateProperties.HORIZONTAL_AXIS, Direction.Axis.X));
	}
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BAS, HAUT, DOUBLE, BlockStateProperties.HORIZONTAL_AXIS); }
	private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) {
		return s.setValue(BAS, !(l.getBlockState(p.below()).getBlock() instanceof Reverbere)).setValue(HAUT, !(l.getBlockState(p.above()).getBlock() instanceof Reverbere));
	}
	@Override
	public BlockState getStateForPlacement(BlockPlaceContext c) {
		return ajuster(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_AXIS, c.getHorizontalDirection().getClockWise().getAxis()), c.getLevel(), c.getClickedPos());
	}
	@Override
	protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
		return d.getAxis() == Direction.Axis.Y ? ajuster(s, l, p) : s;
	}
	// clé sur la tête : une lanterne ou deux
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		if (!s.getValue(HAUT)) return InteractionResult.PASS;
		if (!c.getLevel().isClientSide) {
			c.getLevel().setBlock(c.getClickedPos(), s.setValue(DOUBLE, !s.getValue(DOUBLE)), Block.UPDATE_ALL);
			c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
		}
		return InteractionResult.SUCCESS;
	}
	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
		VoxelShape v = FUT;
		if (s.getValue(BAS)) v = Shapes.or(v, SOCLE);
		if (s.getValue(HAUT)) v = Shapes.or(v, TETE);
		return v;
	}
}
