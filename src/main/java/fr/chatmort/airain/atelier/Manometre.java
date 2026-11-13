package fr.chatmort.airain.atelier;

import com.mojang.serialization.MapCodec;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import fr.chatmort.airain.fonderie.BoucheAirBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.FaceAttachedHorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;

/**
 * Manomètre : posé sur un tuyau, une machine, un réservoir ou une bouche d'air (dessus, dessous ou sur le côté).
 * Son aiguille suit la vitesse d'une machine de Create, le courant d'une bouche d'air, ou le remplissage d'un réservoir.
 */
public class Manometre extends FaceAttachedHorizontalDirectionalBlock implements EntityBlock {
	public static final MapCodec<Manometre> CODEC = simpleCodec(Manometre::new);
	public Manometre(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(FACE, AttachFace.WALL)); }
	@Override protected MapCodec<? extends FaceAttachedHorizontalDirectionalBlock> codec() { return CODEC; }
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, FACE); }

	/** Le bloc qui porte le manomètre. */
	public static BlockPos support(BlockState s, BlockPos p) { return p.relative(getConnectedDirection(s).getOpposite()); }
	// tient sur n'importe quel bloc (un tuyau n'a pas de face pleine)
	@Override protected boolean canSurvive(BlockState s, LevelReader l, BlockPos p) { return !l.getBlockState(support(s, p)).isAir(); }

	/** Valeur lue (0 à 1) sur le bloc porteur. */
	public static float lecture(Level l, BlockState s, BlockPos p) {
		BlockPos q = support(s, p);
		BlockEntity be = l.getBlockEntity(q);
		if (be instanceof KineticBlockEntity k) return Math.min(1f, Math.abs(k.getSpeed()) / 256f);
		if (be instanceof BoucheAirBlockEntity b) return Math.min(1f, Math.abs(b.getSpeed()) / 256f);
		IFluidHandler f = l.getCapability(Capabilities.FluidHandler.BLOCK, q, getConnectedDirection(s));
		if (f != null) {
			long a = 0, c = 0;
			for (int i = 0; i < f.getTanks(); i++) { a += f.getFluidInTank(i).getAmount(); c += f.getTankCapacity(i); }
			if (c > 0) return Math.min(1f, (float) a / c);
		}
		return 0f;
	}

	private static final VoxelShape MUR_N = Block.box(4.5, 4.5, 12.5, 11.5, 11.5, 16);
	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
		AttachFace f = s.getValue(FACE);
		if (f == AttachFace.FLOOR) return Block.box(4.5, 0, 4.5, 11.5, 9.5, 11.5);
		if (f == AttachFace.CEILING) return Block.box(4.5, 6.5, 4.5, 11.5, 16, 11.5);
		return fr.chatmort.airain.fonderie.ConduitAir.boiteVers(s.getValue(FACING), 4.5, 4.5, 12.5, 11.5, 11.5, 16);
	}
	@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new ManometreBlockEntity(p, s); }

	/** Bloc-entité : garde la position lissée de l'aiguille (côté client). */
	public static class ManometreBlockEntity extends BlockEntity {
		public float aiguille, avant;
		public ManometreBlockEntity(BlockPos p, BlockState s) { super(Atelier.MANOMETRE_BE.get(), p, s); }
	}
	@SuppressWarnings("unused") private static final VoxelShape INUTILE = MUR_N;
}
