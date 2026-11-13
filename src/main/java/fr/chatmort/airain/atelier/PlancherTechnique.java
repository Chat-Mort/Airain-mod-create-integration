package fr.chatmort.airain.atelier;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import fr.chatmort.airain.fonderie.ConduitAir;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.Map;

/**
 * Plancher technique : une dalle d'airain sur quatre plots. La clé de Create relève ou rabat la dalle ; dalle relevée,
 * on y loge un tuyau d'airain ou un conduit d'air (clic droit avec l'objet), qu'on reprend main nue.
 * Le conduit logé fait partie du réseau de la conduite d'air, le tuyau se raccorde aux tuyaux voisins (dans son axe).
 */
public class PlancherTechnique extends BlocPatine implements IWrenchable {
	public enum Contenu implements StringRepresentable {
		RIEN("none"), TUYAU("pipe"), CONDUIT("duct");
		private final String nom;
		Contenu(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public static final EnumProperty<Contenu> CONTENU = EnumProperty.create("content", Contenu.class);
	private static final Map<BlockState, VoxelShape> FORMES = new java.util.concurrent.ConcurrentHashMap<>();

	public PlancherTechnique(WeatherState etat, Properties p) {
		super(etat, p);
		registerDefaultState(defaultBlockState().setValue(BlockStateProperties.OPEN, false).setValue(CONTENU, Contenu.RIEN).setValue(BlockStateProperties.HORIZONTAL_AXIS, Direction.Axis.X));
	}
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.OPEN, CONTENU, BlockStateProperties.HORIZONTAL_AXIS); }

	/** Le plancher n loge-t-il ce contenu dans cet axe ? */
	public static boolean loge(BlockState n, Contenu c, Direction.Axis a) {
		return n.getValue(CONTENU) == c && n.getValue(BlockStateProperties.HORIZONTAL_AXIS) == a;
	}
	private static Contenu contenuDe(ItemStack st) {
		if (st.is(ConduitAir.CONDUIT.get().asItem())) return Contenu.CONDUIT;
		if (st.getItem() instanceof BlockItem bi && bi.getBlock() instanceof Tuyaux.Tuyau) return Contenu.TUYAU;
		return null;
	}
	private static ItemStack objetDe(Contenu c) {
		return c == Contenu.CONDUIT ? new ItemStack(ConduitAir.CONDUIT.get()) : c == Contenu.TUYAU ? new ItemStack(Atelier.bloc("airain_pipe")) : ItemStack.EMPTY;
	}

	// dalle relevée : on y loge un tuyau ou un conduit, dans l'axe du regard
	@Override
	protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand h, BlockHitResult hit) {
		Contenu c = contenuDe(st);
		if (c == null || !s.getValue(BlockStateProperties.OPEN) || s.getValue(CONTENU) != Contenu.RIEN) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		if (!l.isClientSide) {
			l.setBlock(p, s.setValue(CONTENU, c).setValue(BlockStateProperties.HORIZONTAL_AXIS, j.getDirection().getAxis()), Block.UPDATE_ALL);
			l.playSound(null, p, SoundEvents.COPPER_PLACE, SoundSource.BLOCKS, 1f, 1f);
			if (!j.getAbilities().instabuild) st.shrink(1);
		}
		return ItemInteractionResult.sidedSuccess(l.isClientSide);
	}
	// main nue, dalle relevée : on reprend ce qui est logé
	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult hit) {
		if (!s.getValue(BlockStateProperties.OPEN) || s.getValue(CONTENU) == Contenu.RIEN) return InteractionResult.PASS;
		if (!l.isClientSide) {
			if (!j.getAbilities().instabuild) Block.popResource(l, p.above(), objetDe(s.getValue(CONTENU)));
			l.setBlock(p, s.setValue(CONTENU, Contenu.RIEN), Block.UPDATE_ALL);
			l.playSound(null, p, SoundEvents.COPPER_BREAK, SoundSource.BLOCKS, 1f, 1f);
		}
		return InteractionResult.sidedSuccess(l.isClientSide);
	}
	// clé de Create : relève ou rabat la dalle
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		if (!c.getLevel().isClientSide) {
			boolean o = !s.getValue(BlockStateProperties.OPEN);
			c.getLevel().setBlock(c.getClickedPos(), s.setValue(BlockStateProperties.OPEN, o), Block.UPDATE_ALL);
			c.getLevel().playSound(null, c.getClickedPos(), o ? SoundEvents.COPPER_TRAPDOOR_OPEN : SoundEvents.COPPER_TRAPDOOR_CLOSE, SoundSource.BLOCKS, 1f, 1f);
		}
		return InteractionResult.SUCCESS;
	}
	@Override
	protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
		if (!(n.getBlock() instanceof PlancherTechnique) && s.getValue(CONTENU) != Contenu.RIEN) Block.popResource(l, p, objetDe(s.getValue(CONTENU)));
		super.onRemove(s, l, p, n, deplace);
	}
	@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.computeIfAbsent(s, PlancherTechnique::forme); }
	private static VoxelShape forme(BlockState s) {
		VoxelShape v = Shapes.or(Block.box(1, 0, 1, 3, 13, 3), Block.box(13, 0, 1, 15, 13, 3), Block.box(1, 0, 13, 3, 13, 15), Block.box(13, 0, 13, 15, 13, 15));
		if (!s.getValue(BlockStateProperties.OPEN)) v = Shapes.or(v, Block.box(0, 13, 0, 16, 16, 16));
		boolean x = s.getValue(BlockStateProperties.HORIZONTAL_AXIS) == Direction.Axis.X;
		switch (s.getValue(CONTENU)) {
			case TUYAU -> v = Shapes.or(v, x ? Block.box(0, 5, 5, 16, 11, 11) : Block.box(5, 5, 0, 11, 11, 16));
			case CONDUIT -> v = Shapes.or(v, x ? Block.box(0, 3, 3, 16, 13, 13) : Block.box(3, 3, 0, 13, 13, 16));
			default -> {}
		}
		return v.optimize();
	}
}
