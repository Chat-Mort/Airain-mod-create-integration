package fr.chatmort.airain.atelier;

import com.mojang.serialization.MapCodec;
import com.simibubi.create.content.equipment.wrench.IWrenchable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Borne de carrefour : un poteau qui porte jusqu'à deux flèches par bloc (en haut, en bas), chacune dans une des
 * huit directions. Clic droit avec une borne : ajoute une flèche là où l'on regarde. Clé de Create : tourne la flèche
 * visée de 45°. Clic droit avec une étiquette renommée à l'enclume : écrit ce nom sur la flèche visée.
 */
public class Borne extends BaseEntityBlock implements IWrenchable {
	public enum Dir8 implements StringRepresentable {
		AUCUNE("none"), N("n"), NE("ne"), E("e"), SE("se"), S("s"), SO("sw"), O("w"), NO("nw");
		private final String nom;
		Dir8(String n) { nom = n; }
		@Override public String getSerializedName() { return nom; }
		/** Rang de 0 (nord) à 7 (nord-ouest), dans le sens des aiguilles d'une montre. */
		public int rang() { return ordinal() - 1; }
		public static Dir8 regard(float yaw) { return values()[1 + (Mth.floor((yaw + 180f) / 45f + 0.5f) & 7)]; }
		public Dir8 suivante() { return this == AUCUNE ? N : values()[1 + (rang() + 1) % 8]; }
	}
	public static final MapCodec<Borne> CODEC = simpleCodec(Borne::new);
	public static final EnumProperty<Dir8> FLECHE_HAUT = EnumProperty.create("upper", Dir8.class);
	public static final EnumProperty<Dir8> FLECHE_BAS = EnumProperty.create("lower", Dir8.class);
	public static final BooleanProperty BAS = BooleanProperty.create("bottom");
	public static final BooleanProperty HAUT = BooleanProperty.create("top");
	private static final VoxelShape FUT = Block.box(6.5, 0, 6.5, 9.5, 16, 9.5), SOCLE = Block.box(4, 0, 4, 12, 2, 12);

	public Borne(Properties p) {
		super(p);
		registerDefaultState(defaultBlockState().setValue(FLECHE_HAUT, Dir8.AUCUNE).setValue(FLECHE_BAS, Dir8.AUCUNE).setValue(BAS, true).setValue(HAUT, true));
	}
	@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
	@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FLECHE_HAUT, FLECHE_BAS, BAS, HAUT); }
	@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
	private static BlockState ajuster(BlockState s, BlockGetter l, BlockPos p) {
		return s.setValue(BAS, !(l.getBlockState(p.below()).getBlock() instanceof Borne)).setValue(HAUT, !(l.getBlockState(p.above()).getBlock() instanceof Borne));
	}
	// posée : une flèche en haut, dans la direction du regard
	@Override
	public BlockState getStateForPlacement(BlockPlaceContext c) {
		float yaw = c.getPlayer() != null ? c.getPlayer().getYRot() : 0;
		return ajuster(defaultBlockState().setValue(FLECHE_HAUT, Dir8.regard(yaw)), c.getLevel(), c.getClickedPos());
	}
	@Override
	protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
		return d.getAxis() == Direction.Axis.Y ? ajuster(s, l, p) : s;
	}
	private static boolean haut(BlockPos p, BlockHitResult h) { return h.getLocation().y - p.getY() >= 0.5; }

	@Override
	protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand m, BlockHitResult h) {
		// une autre borne : ajoute une flèche sur la place libre (haut d'abord)
		if (st.is(asItem()) && (s.getValue(FLECHE_HAUT) == Dir8.AUCUNE || s.getValue(FLECHE_BAS) == Dir8.AUCUNE)) {
			if (!l.isClientSide) {
				EnumProperty<Dir8> prop = s.getValue(FLECHE_HAUT) == Dir8.AUCUNE ? FLECHE_HAUT : FLECHE_BAS;
				l.setBlock(p, s.setValue(prop, Dir8.regard(j.getYRot())), Block.UPDATE_ALL);
				l.playSound(null, p, SoundEvents.COPPER_PLACE, SoundSource.BLOCKS, 1f, 1.2f);
				if (!j.getAbilities().instabuild) st.shrink(1);
			}
			return ItemInteractionResult.sidedSuccess(l.isClientSide);
		}
		// une étiquette renommée : le nom s'écrit sur la flèche visée
		if (st.is(Items.NAME_TAG) && st.has(DataComponents.CUSTOM_NAME)) {
			boolean b = haut(p, h);
			if ((b ? s.getValue(FLECHE_HAUT) : s.getValue(FLECHE_BAS)) == Dir8.AUCUNE) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			if (!l.isClientSide && l.getBlockEntity(p) instanceof BorneBlockEntity be) {
				be.ecrire(b, st.getHoverName().getString());
				l.playSound(null, p, SoundEvents.UI_CARTOGRAPHY_TABLE_TAKE_RESULT, SoundSource.BLOCKS, 0.8f, 1.2f);
			}
			return ItemInteractionResult.sidedSuccess(l.isClientSide);
		}
		return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
	}
	// clé de Create : la flèche visée tourne de 45°
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		boolean b = c.getClickLocation().y - c.getClickedPos().getY() >= 0.5;
		EnumProperty<Dir8> prop = b ? FLECHE_HAUT : FLECHE_BAS;
		if (s.getValue(prop) == Dir8.AUCUNE) return InteractionResult.PASS;
		if (!c.getLevel().isClientSide) {
			c.getLevel().setBlock(c.getClickedPos(), s.setValue(prop, s.getValue(prop).suivante()), Block.UPDATE_ALL);
			c.getLevel().playSound(null, c.getClickedPos(), SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 1.2f);
		}
		return InteractionResult.SUCCESS;
	}
	// chaque flèche rend une borne quand on casse le poteau (la première est la borne elle-même)
	@Override
	protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
		if (!n.is(this) && s.getValue(FLECHE_HAUT) != Dir8.AUCUNE && s.getValue(FLECHE_BAS) != Dir8.AUCUNE) Block.popResource(l, p, new ItemStack(this));
		super.onRemove(s, l, p, n, deplace);
	}
	@Override
	protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
		return s.getValue(BAS) ? Shapes.or(FUT, SOCLE) : FUT;
	}
	@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new BorneBlockEntity(p, s); }

	/** Les textes écrits sur les deux flèches. */
	public static class BorneBlockEntity extends BlockEntity {
		public String texteHaut = "", texteBas = "";
		public BorneBlockEntity(BlockPos p, BlockState s) { super(Atelier.BORNE_BE.get(), p, s); }
		void ecrire(boolean haut, String t) {
			if (t.length() > 24) t = t.substring(0, 24);
			if (haut) texteHaut = t; else texteBas = t;
			setChanged();
			if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
		}
		@Override protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); t.putString("haut", texteHaut); t.putString("bas", texteBas); }
		@Override protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); texteHaut = t.getString("haut"); texteBas = t.getString("bas"); }
		@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
		@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
	}
}
