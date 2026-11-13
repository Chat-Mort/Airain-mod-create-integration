package fr.chatmort.airain.atelier;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.Map;

/**
 * Toboggan d'airain : une goulotte à 45° qui descend d'un bloc vers FACING ; ce qui s'y pose glisse vers le bas.
 * La clé de Create en fait un bac plat (le bout du toboggan).
 */
public class Toboggan extends BlocPatine implements IWrenchable {
	public static final BooleanProperty PLAT = BooleanProperty.create("flat");
	private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();
	public Toboggan(WeatherState etat, Properties p) { super(etat, p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH).setValue(PLAT, false)); }
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING, PLAT); }
	@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, c.getHorizontalDirection()); }
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		if (!c.getLevel().isClientSide) {
			c.getLevel().setBlock(c.getClickedPos(), s.setValue(PLAT, !s.getValue(PLAT)), Block.UPDATE_ALL);
			c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1f);
		}
		return InteractionResult.SUCCESS;
	}
	// on glisse : poussée vers le bas de la pente (ou vers la sortie du bac)
	@Override
	public void stepOn(Level l, BlockPos p, BlockState s, Entity e) {
		Direction f = s.getValue(BlockStateProperties.HORIZONTAL_FACING);
		double force = s.getValue(PLAT) ? 0.03 : 0.09, max = s.getValue(PLAT) ? 0.25 : 0.7;
		Vec3 v = e.getDeltaMovement();
		double vf = v.x * f.getStepX() + v.z * f.getStepZ();
		if (vf < max) e.setDeltaMovement(v.add(f.getStepX() * force, 0, f.getStepZ() * force));
		e.fallDistance = 0;
		super.stepOn(l, p, s, e);
	}
	@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.computeIfAbsent(s, Toboggan::forme); }
	private static VoxelShape forme(BlockState s) {
		Direction f = s.getValue(BlockStateProperties.HORIZONTAL_FACING);
		VoxelShape v = Shapes.empty();
		if (s.getValue(PLAT)) {
			v = Shapes.or(Block.box(0, 0, 0, 16, 1, 16), versF(f, 1, 1, 0, 2, 4, 16), versF(f, 14, 1, 0, 15, 4, 16));
		} else {
			// décrit pour une pente qui descend vers le nord (bas au nord, haut au sud), en marches de 2 px
			for (int i = 0; i < 8; i++) v = Shapes.or(v, versF(f, 2, 0, 2 * i, 14, 2 * i + 2, 2 * i + 2));
			v = Shapes.or(v, versF(f, 1, 0, 0, 2, 16, 16), versF(f, 14, 0, 0, 15, 16, 16));
		}
		return v.optimize();
	}
	private static VoxelShape versF(Direction f, double x0, double y0, double z0, double x1, double y1, double z1) {
		return fr.chatmort.airain.fonderie.ConduitAir.boiteVers(f, x0, y0, z0, x1, y1, z1);
	}
}
