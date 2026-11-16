package fr.chatmort.airain.affichage;

import fr.chatmort.airain.fonderie.ConduitAir;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.Map;

/**
 * 1.60 : le tableau émaillé. Les blocs voisins de même orientation forment un seul tableau (rectangle, 16 × 8 au plus) :
 * le bloc du coin en haut à gauche garde les réglages et dessine tout. Clic droit main nue : le menu.
 */
public class EmailBlock extends Block implements EntityBlock {
	public enum Montage implements StringRepresentable {
		MUR("wall"), PENDU("hanging"), PIED("post");
		private final String nom;
		Montage(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	public static final EnumProperty<Montage> MONTAGE = EnumProperty.create("mount", Montage.class);
	/** Lumière émise (réglée par le tableau : intensité choisie quand il est allumé). */
	public static final IntegerProperty LUMIERE = IntegerProperty.create("light", 0, 15);
	private static final Map<Direction, VoxelShape[]> FORMES = new EnumMap<>(Direction.class);
	static {
		for (Direction d : Direction.Plane.HORIZONTAL)   // dessinées face au nord : le mur est au sud
			FORMES.put(d, new VoxelShape[] {ConduitAir.boiteVers(d, 0, 0, 10, 16, 16, 16), ConduitAir.boiteVers(d, 0, 0, 5, 16, 16, 11), ConduitAir.boiteVers(d, 0, 0, 5, 16, 16, 11)});
	}

	public EmailBlock(Properties p) {
		super(p);
		registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(MONTAGE, Montage.MUR).setValue(LUMIERE, 0));
	}
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, MONTAGE, LUMIERE); }
	/** La face émaillée regarde le joueur. */
	@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }
	@Override protected BlockState rotate(BlockState s, Rotation r) { return s.setValue(FACING, r.rotate(s.getValue(FACING))); }
	@Override protected BlockState mirror(BlockState s, Mirror m) { return s.rotate(m.getRotation(s.getValue(FACING))); }
	@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(FACING))[s.getValue(MONTAGE).ordinal()]; }
	// le dessin est fait par le rendu du bloc-entité (cadre, émail, texte)
	@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.ENTITYBLOCK_ANIMATED; }

	@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new EmailBlockEntity(Email.BE.get(), p, s); }
	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
		return t == Email.BE.get() ? (lv, p, st, be) -> ((EmailBlockEntity) be).tick() : null;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
		if (l.isClientSide && l.getBlockEntity(p) instanceof EmailBlockEntity e) EmailClient.ouvrir(e.controleur());
		return InteractionResult.sidedSuccess(l.isClientSide);
	}

	/** Le coin qui garde les réglages s'en va : il les confie à un voisin du tableau, qui les rendra au nouveau coin. */
	@Override
	protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
		if (!l.isClientSide && !n.is(this) && l.getBlockEntity(p) instanceof EmailBlockEntity e) e.confier();
		super.onRemove(s, l, p, n, deplace);
	}
}
