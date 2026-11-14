package fr.chatmort.airain.atelier;

import com.simibubi.create.content.equipment.wrench.IWrenchable;
import fr.chatmort.airain.fonderie.Passerelle;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Plaque émaillée : contre un mur, ou contre la rambarde d'une passerelle (elle se cale alors à hauteur de rambarde).
 * La clé de Create fait défiler les pictogrammes.
 */
public class Plaque extends Block implements IWrenchable {
	public enum Picto implements StringRepresentable {
		DROITE("arrow_right"), GAUCHE("arrow_left"), HAUT("arrow_up"), FORGE("forge"), DANGER("danger"), SORTIE("exit"), STOCK("storage"), ENGRENAGE("gear");
		private final String nom;
		Picto(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public enum Niveau implements StringRepresentable {
		MILIEU("middle"), BAS("catwalk_low"), HAUT("catwalk_high");
		private final String nom;
		Niveau(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
	}
	public static final EnumProperty<Picto> PICTO = EnumProperty.create("picto", Picto.class);
	public static final EnumProperty<Niveau> NIVEAU = EnumProperty.create("level", Niveau.class);
	public Plaque(Properties p) {
		super(p);
		registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH).setValue(PICTO, Picto.DROITE).setValue(NIVEAU, Niveau.MILIEU));
	}
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING, PICTO, NIVEAU); }
	private static BlockPos support(BlockState s, BlockPos p) { return p.relative(s.getValue(BlockStateProperties.HORIZONTAL_FACING).getOpposite()); }
	private static Niveau niveau(BlockState porteur) {
		if (porteur.getBlock() instanceof Passerelle.Plancher) return porteur.getValue(Passerelle.HAUT) ? Niveau.HAUT : Niveau.BAS;
		if (porteur.getBlock() instanceof Passerelle.Palier) return Niveau.HAUT;
		return Niveau.MILIEU;
	}
	@Override
	public BlockState getStateForPlacement(BlockPlaceContext c) {
		if (!c.getClickedFace().getAxis().isHorizontal()) return null;
		BlockState s = defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, c.getClickedFace());
		return s.setValue(NIVEAU, niveau(c.getLevel().getBlockState(support(s, c.getClickedPos()))));
	}
	@Override protected boolean canSurvive(BlockState s, LevelReader l, BlockPos p) { return !l.getBlockState(support(s, p)).isAir(); }
	@Override
	protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
		if (d == s.getValue(BlockStateProperties.HORIZONTAL_FACING).getOpposite()) {
			if (!canSurvive(s, l, p)) return Blocks.AIR.defaultBlockState();
			return s.setValue(NIVEAU, niveau(v));
		}
		return s;
	}
	// clé de Create : pictogramme suivant
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		if (!c.getLevel().isClientSide) {
			Picto[] t = Picto.values();
			c.getLevel().setBlock(c.getClickedPos(), s.setValue(PICTO, t[(s.getValue(PICTO).ordinal() + 1) % t.length]), Block.UPDATE_ALL);
			c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 0.7f, 1.4f);
		}
		return InteractionResult.SUCCESS;
	}
	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
		double y0 = switch (s.getValue(NIVEAU)) { case BAS -> 7; case HAUT -> 15; default -> 4; };
		double y1 = s.getValue(NIVEAU) == Niveau.MILIEU ? 12 : y0 + 6;
		// contre une rambarde de passerelle, la plaque se pose sur sa face extérieure (la rambarde occupe le bord de ce bloc)
		double z0 = s.getValue(NIVEAU) == Niveau.MILIEU ? 15.5 : 13.5;
		return fr.chatmort.airain.fonderie.ConduitAir.boiteVers(s.getValue(BlockStateProperties.HORIZONTAL_FACING), 3, y0, z0, 13, Math.min(16, y1), z0 + 0.5);
	}
}
