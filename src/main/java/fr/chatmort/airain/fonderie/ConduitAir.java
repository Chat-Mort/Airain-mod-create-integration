package fr.chatmort.airain.fonderie;

import com.mojang.serialization.MapCodec;
import com.simibubi.create.content.kinetics.fan.EncasedFanBlock;
import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.PipeBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.Map;

/**
 * La conduite d'air : un ventilateur de Create souffle (ou aspire) dans un réseau de conduits d'airain, et chaque bouche
 * d'air reproduit à l'autre bout exactement le même courant (même force, même portée, mêmes traitements), sans perte.
 */
public final class ConduitAir {
	private ConduitAir() {}

	/** Longueur maximale d'un réseau de conduits (au-delà, la bouche reste muette). */
	public static final int MAX_CONDUITS = 64;
	public static final DirectionProperty FACING = BlockStateProperties.FACING;

	private static BlockBehaviour.Properties airain() {
		return BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
			.isRedstoneConductor((a, b, c) -> false).isSuffocating((a, b, c) -> false).isViewBlocking((a, b, c) -> false);
	}

	/** Boîte décrite pour une pièce tournée vers le nord, tournée vers f (6 directions). */
	static VoxelShape boite(Direction f, double x0, double y0, double z0, double x1, double y1, double z1) {
		return switch (f) {
			case NORTH -> Block.box(x0, y0, z0, x1, y1, z1);
			case SOUTH -> Block.box(16 - x1, y0, 16 - z1, 16 - x0, y1, 16 - z0);
			case EAST -> Block.box(16 - z1, y0, x0, 16 - z0, y1, x1);
			case WEST -> Block.box(z0, y0, 16 - x1, z1, y1, 16 - x0);
			case UP -> Block.box(x0, 16 - z1, y0, x1, 16 - z0, y1);
			default -> Block.box(x0, z0, 16 - y1, x1, z1, 16 - y0);
		};
	}

	// ====================================================================== le conduit (se raccorde tout seul)
	public static class Conduit extends Block {
		private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();
		public Conduit(Properties p) {
			super(p);
			BlockState s = defaultBlockState();
			for (Direction d : Direction.values()) s = s.setValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d), false);
			registerDefaultState(s);
		}
		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			b.add(BlockStateProperties.NORTH, BlockStateProperties.SOUTH, BlockStateProperties.EAST, BlockStateProperties.WEST, BlockStateProperties.UP, BlockStateProperties.DOWN);
		}
		/** Le conduit se raccorde à un autre conduit, au dos d'une bouche, ou à l'avant d'un ventilateur. */
		static boolean raccorde(BlockGetter l, BlockPos p, Direction d) {
			BlockState n = l.getBlockState(p.relative(d));
			if (n.getBlock() instanceof Conduit) return true;
			if (n.getBlock() instanceof Bouche) return n.getValue(FACING) == d;
			return n.getBlock() instanceof EncasedFanBlock && n.getValue(BlockStateProperties.FACING) == d.getOpposite();
		}
		private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) {
			for (Direction d : Direction.values()) s = s.setValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d), raccorde(l, p, d));
			return s;
		}
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return ajuster(defaultBlockState(), c.getLevel(), c.getClickedPos()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			return s.setValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d), raccorde(l, p, d));
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.computeIfAbsent(s, Conduit::forme); }
		// conduit plein (10×10) : le courant du ventilateur s'y arrête net et repart de la bouche
		private static VoxelShape forme(BlockState s) {
			VoxelShape v = Block.box(3, 3, 3, 13, 13, 13);
			for (Direction d : Direction.values())
				if (s.getValue(PipeBlock.PROPERTY_BY_DIRECTION.get(d))) v = Shapes.joinUnoptimized(v, boite(d, 2, 2, 0, 14, 14, 3), BooleanOp.OR);
			return v.optimize();
		}
	}

	// ====================================================================== la bouche d'air (FACING : là où sort le courant)
	public static class Bouche extends BaseEntityBlock {
		public static final MapCodec<Bouche> CODEC = simpleCodec(Bouche::new);
		private static final Map<Direction, VoxelShape> FORMES = new java.util.EnumMap<>(Direction.class);
		static {
			for (Direction d : Direction.values())
				FORMES.put(d, Shapes.or(boite(d, 1, 1, 0, 15, 15, 6), boite(d, 3, 3, 6, 13, 13, 14), boite(d, 2, 2, 14, 14, 14, 16)));
		}
		public Bouche(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH)); }
		@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }
		// posée contre le bout d'un conduit, elle souffle à l'opposé
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getClickedFace()); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(FACING)); }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new BoucheAirBlockEntity(p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> type) {
			return type == BE.get() ? (lv, p, st, be) -> ((BoucheAirBlockEntity) be).tick() : null;
		}
	}

	public static final DeferredBlock<Conduit> CONDUIT = AirainMod.BLOCKS.register("airain_air_duct", () -> new Conduit(airain()));
	public static final DeferredBlock<Bouche> BOUCHE = AirainMod.BLOCKS.register("airain_air_vent", () -> new Bouche(airain()));
	static {
		AirainMod.ITEMS.register("airain_air_duct", () -> new BlockItem(CONDUIT.get(), new Item.Properties()));
		AirainMod.ITEMS.register("airain_air_vent", () -> new BlockItem(BOUCHE.get(), new Item.Properties()));
	}
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<BoucheAirBlockEntity>> BE = AirainMod.BLOCK_ENTITIES.register("airain_air_vent",
		() -> BlockEntityType.Builder.of(BoucheAirBlockEntity::new, BOUCHE.get()).build(null));

	public static void charger() {}
}
