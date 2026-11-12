package fr.chatmort.airain.fusion;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Diffuseur d'Écho : une coupe de laiton où brûle une flamme de source. Posé dans le souffle d'un ventilateur de Create,
 * comme le feu des âmes pour la hantise, il donne la « brume d'Écho » qui imprègne les objets (voir {@link Impregnation}).
 * Il puise la source des jarres à 6 blocs ; sans source, ou avec un signal de redstone, il s'éteint.
 * Aucune collision : le vent le traverse.
 */
public class DiffuseurEchoBlock extends BaseEntityBlock {
	public static final com.mojang.serialization.MapCodec<DiffuseurEchoBlock> CODEC = simpleCodec(DiffuseurEchoBlock::new);
	public static final BooleanProperty ALLUME = BooleanProperty.create("allume");
	private static final VoxelShape FORME = Block.box(3, 0, 3, 13, 9, 13);

	public DiffuseurEchoBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(ALLUME, false));
	}

	@Override
	protected com.mojang.serialization.MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(ALLUME); }

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }

	@Override
	protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new DiffuseurEchoBlockEntity(pos, state); }

	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> type) {
		return l.isClientSide || type != AirainMod.DIFFUSEUR_ECHO_BE.get() ? null : (lv, p, st, be) -> ((DiffuseurEchoBlockEntity) be).tickServeur();
	}

	/** La flamme de source. */
	@Override
	public void animateTick(BlockState s, Level l, BlockPos p, RandomSource r) {
		if (!s.getValue(ALLUME)) return;
		l.addParticle(ParticleTypes.SOUL_FIRE_FLAME, p.getX() + 0.5 + (r.nextDouble() - 0.5) * 0.25, p.getY() + 0.55, p.getZ() + 0.5 + (r.nextDouble() - 0.5) * 0.25, 0, 0.02, 0);
		if (r.nextInt(3) == 0) l.addParticle(ParticleTypes.WITCH, p.getX() + 0.5, p.getY() + 0.8, p.getZ() + 0.5, 0, 0.05, 0);
	}
}
