package fr.chatmort.airain.balise;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Une case de la tour de défense, autre que le cœur : invisible (la tour est dessinée par le cœur), solide selon la
 * silhouette de la tour. PX, PY, PZ : position dans la tour (le cœur est en 1, 0, 1). LUMIERE : la case du phare éclaire
 * pendant l'alerte.
 */
public class BalisePartieBlock extends Block {
	public static final IntegerProperty PX = IntegerProperty.create("px", 0, 2);
	public static final IntegerProperty PY = IntegerProperty.create("py", 0, 7);
	public static final IntegerProperty PZ = IntegerProperty.create("pz", 0, 2);
	public static final BooleanProperty LUMIERE = BooleanProperty.create("lumiere");

	public BalisePartieBlock(Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(PX, 0).setValue(PY, 0).setValue(PZ, 0).setValue(LUMIERE, false));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(PX, PY, PZ, LUMIERE); }

	public static BlockPos coeur(BlockState s, BlockPos pos) {
		return pos.offset(1 - s.getValue(PX), -s.getValue(PY), 1 - s.getValue(PZ));
	}

	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		VoxelShape f = BaliseFormes.de(s.getValue(PX), s.getValue(PY), s.getValue(PZ));
		return f == null ? Shapes.empty() : f;
	}

	@Override
	protected RenderShape getRenderShape(BlockState state) { return RenderShape.INVISIBLE; }

	/** Casser une case abat toute la tour ; le cœur rend l'objet. */
	@Override
	public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player joueur) {
		BlockPos c = coeur(state, pos);
		if (!level.isClientSide && level.getBlockState(c).is(AirainMod.BALISE.get()))
			level.destroyBlock(c, !joueur.isCreative(), joueur);
		return super.playerWillDestroy(level, pos, state, joueur);
	}

	@Override
	public ItemStack getCloneItemStack(BlockState state, HitResult cible, LevelReader level, BlockPos pos, Player joueur) {
		return new ItemStack(AirainMod.BALISE_ITEM.get());
	}

	/** Une case orpheline (cœur disparu) s'efface d'elle-même au premier passage. */
	@Override
	protected void tick(BlockState state, net.minecraft.server.level.ServerLevel level, BlockPos pos, net.minecraft.util.RandomSource r) {
		if (!level.getBlockState(coeur(state, pos)).is(AirainMod.BALISE.get()))
			level.removeBlock(pos, false);
	}

	@Override
	protected BlockState updateShape(BlockState state, net.minecraft.core.Direction d, BlockState voisin, net.minecraft.world.level.LevelAccessor level,
									 BlockPos pos, BlockPos posVoisin) {
		level.scheduleTick(pos, this, 2);
		return state;
	}
}
