package fr.chatmort.airain.fonderie;

import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import com.simibubi.create.content.kinetics.base.KineticBlock;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.foundation.block.IBE;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * 1.69.1 : le projecteur de chantier. Une tête orientable sur une lyre, entraînée par un arbre de Create par-dessous :
 * dès qu'il tourne (sans surcharge), il s'allume (lumière 15) et aucun monstre n'apparaît naturellement à moins de 16 blocs.
 */
public final class Projecteur {
	private Projecteur() {}

	public static final int RAYON = 16;
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	public static final BooleanProperty LIT = BlockStateProperties.LIT;

	public static final DeferredBlock<Bloc> BLOC = AirainMod.BLOCKS.register("worksite_projector", () -> new Bloc(BlockBehaviour.Properties.of()
		.mapColor(MapColor.GOLD).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
		.lightLevel(s -> s.getValue(LIT) ? 15 : 0)));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<BE>> BE_TYPE = AirainMod.BLOCK_ENTITIES.register("worksite_projector",
		() -> BlockEntityType.Builder.of((p, s) -> new BE(Projecteur.BE_TYPE.get(), p, s), BLOC.get()).build(null));

	public static void charger() {
		AirainMod.ITEMS.register("worksite_projector", () -> new BlockItem(BLOC.get(), new Item.Properties()));
	}

	/** Projecteurs allumés, par dimension (remplis par les blocs eux-mêmes, vérifiés à chaque lecture). */
	private static final Map<ResourceKey<Level>, Set<BlockPos>> ALLUMES = new ConcurrentHashMap<>();

	// ------------------------------------------------------------------ le bloc
	public static class Bloc extends KineticBlock implements IBE<BE> {
		// socle plein, lyre et tête au-dessus
		private static final VoxelShape FORME = Shapes.or(Block.box(1, 0, 1, 15, 5, 15), Block.box(2, 5, 3, 14, 15, 13));

		public Bloc(Properties p) {
			super(p);
			registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(LIT, false));
		}
		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			b.add(FACING, LIT);
			super.createBlockStateDefinition(b);
		}
		// la tête éclaire dans la direction où regarde le joueur qui le pose
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection()); }
		@Override public BlockState rotate(BlockState s, Rotation r) { return s.setValue(FACING, r.rotate(s.getValue(FACING))); }
		// 1.69.5 : la clé le fait pivoter d'un quart de tour quelle que soit la face cliquée (Create ne le faisait que par le dessus)
		@Override public BlockState getRotatedBlockState(BlockState s, Direction face) { return s.setValue(FACING, s.getValue(FACING).getClockWise()); }
		@Override public BlockState mirror(BlockState s, Mirror m) { return s.rotate(m.getRotation(s.getValue(FACING))); }
		@Override public VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
		@Override public Direction.Axis getRotationAxis(BlockState s) { return Direction.Axis.Y; }
		@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return d == Direction.DOWN; }
		@Override public Class<BE> getBlockEntityClass() { return BE.class; }
		@Override public BlockEntityType<? extends BE> getBlockEntityType() { return BE_TYPE.get(); }
		@Override
		public void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!l.isClientSide && !n.is(this)) { Set<BlockPos> e = ALLUMES.get(l.dimension()); if (e != null) e.remove(p); }
			super.onRemove(s, l, p, n, deplace);
		}
	}

	// ------------------------------------------------------------------ l'entité : allumé tant que ça tourne sans surcharge
	public static class BE extends KineticBlockEntity {
		public BE(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }

		@Override
		public void tick() {
			super.tick();
			if (level == null || level.isClientSide || level.getGameTime() % 10 != 3) return;
			boolean on = getSpeed() != 0 && !isOverStressed();
			BlockState s = getBlockState();
			if (s.getValue(LIT) != on) level.setBlock(worldPosition, s.setValue(LIT, on), Block.UPDATE_ALL);
			Set<BlockPos> e = ALLUMES.computeIfAbsent(level.dimension(), k -> ConcurrentHashMap.newKeySet());
			if (on) e.add(worldPosition.immutable()); else e.remove(worldPosition);
		}
	}

	// ------------------------------------------------------------------ pas d'apparition naturelle de monstres autour
	public static void apparition(FinalizeSpawnEvent e) {
		if (e.getSpawnType() != MobSpawnType.NATURAL || !(e.getEntity() instanceof Enemy)) return;
		if (!(e.getLevel().getLevel() instanceof ServerLevel sl)) return;
		Set<BlockPos> ps = ALLUMES.get(sl.dimension());
		if (ps == null || ps.isEmpty()) return;
		double r2 = RAYON * RAYON;
		for (BlockPos p : ps) {
			if (p.distToCenterSqr(e.getX(), e.getY(), e.getZ()) > r2) continue;
			BlockState s = sl.getBlockState(p);
			if (s.is(BLOC.get()) && s.getValue(LIT)) { e.setSpawnCancelled(true); return; }
			ps.remove(p);   // entrée périmée (bloc déplacé ou éteint)
		}
	}

	public static void arret(ServerStoppedEvent e) { ALLUMES.clear(); }
}
