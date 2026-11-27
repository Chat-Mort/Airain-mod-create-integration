package fr.chatmort.airain.fonderie;

import com.mojang.serialization.MapCodec;
import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.pouvoir.Assise;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.CompoundContainer;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;


/**
 * 1.71 : mobilier impérial (noyer sombre, airain, cuir rouge capitonné, marbre veiné d'or).
 * Chaise, fauteuil de commandement, banc (se raccorde), table (se raccorde dans les quatre sens), bureau (seul ou sur
 * deux blocs), étagère (objets posés visibles), armoire (deux blocs, 27 cases).
 */
public final class Mobilier {
	private Mobilier() {}

	private static final net.minecraft.world.level.block.state.properties.DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
	private static final EnumProperty<DoubleBlockHalf> HALF = BlockStateProperties.DOUBLE_BLOCK_HALF;

	private static BlockBehaviour.Properties bois() {
		return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BROWN).strength(2f, 3f).sound(SoundType.WOOD).noOcclusion();
	}

	public static final DeferredBlock<Chaise> CHAISE = AirainMod.BLOCKS.register("imperial_chair", () -> new Chaise(bois()));
	public static final DeferredBlock<Fauteuil> FAUTEUIL = AirainMod.BLOCKS.register("command_armchair", () -> new Fauteuil(bois()));
	public static final DeferredBlock<Banc> BANC = AirainMod.BLOCKS.register("imperial_bench", () -> new Banc(bois()));
	public static final DeferredBlock<Table> TABLE = AirainMod.BLOCKS.register("imperial_table", () -> new Table(bois()));
	public static final DeferredBlock<Bureau> BUREAU = AirainMod.BLOCKS.register("imperial_desk", () -> new Bureau(bois()));
	public static final DeferredBlock<Etagere> ETAGERE = AirainMod.BLOCKS.register("imperial_shelf", () -> new Etagere(bois()));
	public static final DeferredBlock<Armoire> ARMOIRE = AirainMod.BLOCKS.register("imperial_wardrobe", () -> new Armoire(bois()));

	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Coffre>> BUREAU_BE = AirainMod.BLOCK_ENTITIES.register("imperial_desk",
		() -> BlockEntityType.Builder.of((p, s) -> new Coffre(Mobilier.BUREAU_BE.get(), p, s, 9), BUREAU.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Coffre>> ARMOIRE_BE = AirainMod.BLOCK_ENTITIES.register("imperial_wardrobe",
		() -> BlockEntityType.Builder.of((p, s) -> new Coffre(Mobilier.ARMOIRE_BE.get(), p, s, ArmoireMenu.CASES), ARMOIRE.get()).build(null));
	// 1.71.1 : écran de l'armoire (sets d'armure)
	public static final DeferredHolder<MenuType<?>, MenuType<ArmoireMenu>> ARMOIRE_MENU = AirainMod.MENUS.register("imperial_wardrobe",
		() -> new MenuType<>(ArmoireMenu::new, net.minecraft.world.flag.FeatureFlags.VANILLA_SET));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<Presentoir>> ETAGERE_BE = AirainMod.BLOCK_ENTITIES.register("imperial_shelf",
		() -> BlockEntityType.Builder.of(Presentoir::new, ETAGERE.get()).build(null));

	public static void charger() {
		for (DeferredBlock<?> b : java.util.List.of(CHAISE, FAUTEUIL, BANC, TABLE, BUREAU, ETAGERE, ARMOIRE))
			AirainMod.ITEMS.register(b.getId().getPath(), () -> new BlockItem(b.get(), new Item.Properties()));
	}

	// ------------------------------------------------------------------ formes : boîtes dessinées face au nord, tournées selon l'orientation
	private static VoxelShape tourne(Direction f, double[]... boites) {
		VoxelShape v = Shapes.empty();
		for (double[] b : boites) {
			double x1 = b[0], z1 = b[2], x2 = b[3], z2 = b[5], ax, az, bx, bz;
			switch (f) {
				case EAST -> { ax = 16 - z2; az = x1; bx = 16 - z1; bz = x2; }
				case SOUTH -> { ax = 16 - x2; az = 16 - z2; bx = 16 - x1; bz = 16 - z1; }
				case WEST -> { ax = z1; az = 16 - x2; bx = z2; bz = 16 - x1; }
				default -> { ax = x1; az = z1; bx = x2; bz = z2; }
			}
			v = Shapes.or(v, Block.box(ax, b[1], az, bx, b[4], bz));
		}
		return v;
	}
	private static java.util.Map<Direction, VoxelShape> formes(double[]... boites) {
		java.util.Map<Direction, VoxelShape> m = new java.util.EnumMap<>(Direction.class);
		for (Direction d : Direction.Plane.HORIZONTAL) m.put(d, tourne(d, boites));
		return m;
	}

	// ------------------------------------------------------------------ s'asseoir (même siège invisible que le trône)
	/** Meuble sur lequel on s'assoit : le siège invisible reste tant que le bloc est un de ceux-là. */
	public interface Assisable {}

	static InteractionResult asseoir(BlockState s, Level l, BlockPos pos, Player p) {
		if (l.isClientSide) return InteractionResult.SUCCESS;
		if (p.isPassenger() || p.isShiftKeyDown() || !(p instanceof ServerPlayer)) return InteractionResult.PASS;
		if (!l.getEntitiesOfClass(Assise.class, new net.minecraft.world.phys.AABB(pos)).isEmpty()) return InteractionResult.PASS;
		Assise a = AirainMod.ASSISE.get().create(l);
		if (a == null) return InteractionResult.PASS;
		a.setPos(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5);
		a.setYRot(s.getValue(FACING).toYRot());   // on regarde vers l'avant du meuble
		l.addFreshEntity(a);
		p.startRiding(a, true);
		return InteractionResult.CONSUME;
	}

	/** Base : meuble orienté vers le joueur. */
	public abstract static class Meuble extends HorizontalDirectionalBlock {
		protected Meuble(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }
	}

	// ------------------------------------------------------------------ chaise
	public static class Chaise extends Meuble implements Assisable {
		public static final MapCodec<Chaise> CODEC = simpleCodec(Chaise::new);
		private static final java.util.Map<Direction, VoxelShape> F = formes(new double[] {3, 0, 3, 13, 9.5, 13}, new double[] {3, 9.5, 11, 13, 16, 13});
		public Chaise(Properties p) { super(p); }
		@Override protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return F.get(s.getValue(FACING)); }
		@Override protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) { return asseoir(s, l, p, j); }
	}

	// ------------------------------------------------------------------ meubles sur deux blocs (fauteuil, armoire) : comme une porte
	public abstract static class Double extends Meuble {
		protected Double(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(HALF, DoubleBlockHalf.LOWER)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, HALF); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			BlockPos p = c.getClickedPos(); Level l = c.getLevel();
			if (p.getY() >= l.getMaxBuildHeight() - 1 || !l.getBlockState(p.above()).canBeReplaced(c)) return null;
			return super.getStateForPlacement(c).setValue(HALF, DoubleBlockHalf.LOWER);
		}
		@Override
		public void setPlacedBy(Level l, BlockPos p, BlockState s, LivingEntity e, ItemStack st) {
			l.setBlock(p.above(), s.setValue(HALF, DoubleBlockHalf.UPPER), 3);
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState n, LevelAccessor l, BlockPos p, BlockPos np) {
			DoubleBlockHalf h = s.getValue(HALF);
			if (d.getAxis() == Direction.Axis.Y && (h == DoubleBlockHalf.LOWER) == (d == Direction.UP))
				return n.is(this) && n.getValue(HALF) != h ? s.setValue(FACING, n.getValue(FACING)) : Blocks.AIR.defaultBlockState();
			return super.updateShape(s, d, n, l, p, np);
		}
		@Override
		public BlockState playerWillDestroy(Level l, BlockPos p, BlockState s, Player j) {
			// en créatif, casser le haut ne fait pas tomber l'objet du bas (comme une porte)
			if (!l.isClientSide && j.isCreative() && s.getValue(HALF) == DoubleBlockHalf.UPPER) {
				BlockPos b = p.below(); BlockState bs = l.getBlockState(b);
				if (bs.is(this) && bs.getValue(HALF) == DoubleBlockHalf.LOWER) { l.setBlock(b, Blocks.AIR.defaultBlockState(), 35); l.levelEvent(j, 2001, b, Block.getId(bs)); }
			}
			return super.playerWillDestroy(l, p, s, j);
		}
		/** Position du bas, quelle que soit la moitié cliquée. */
		protected static BlockPos bas(BlockState s, BlockPos p) { return s.getValue(HALF) == DoubleBlockHalf.UPPER ? p.below() : p; }
	}

	// ------------------------------------------------------------------ fauteuil de commandement
	public static class Fauteuil extends Double implements Assisable {
		public static final MapCodec<Fauteuil> CODEC = simpleCodec(Fauteuil::new);
		private static final java.util.Map<Direction, VoxelShape> BAS = formes(new double[] {0.5, 0, 1, 15.5, 10, 15}, new double[] {0, 10, 1, 2.5, 14, 14.5},
			new double[] {13.5, 10, 1, 16, 14, 14.5}, new double[] {1, 10, 12.5, 15, 16, 15});
		private static final java.util.Map<Direction, VoxelShape> HAUT = formes(new double[] {0.5, 0, 12, 15.5, 16, 15.5});
		public Fauteuil(Properties p) { super(p); }
		@Override protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			return (s.getValue(HALF) == DoubleBlockHalf.LOWER ? BAS : HAUT).get(s.getValue(FACING));
		}
		@Override protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			return asseoir(l.getBlockState(bas(s, p)), l, bas(s, p), j);
		}
	}

	// ------------------------------------------------------------------ banc : se raccorde à gauche et à droite ; pieds aux bouts et tous les trois blocs
	public static final BooleanProperty GAUCHE = BooleanProperty.create("left"), DROITE = BooleanProperty.create("right"), PIEDS = BooleanProperty.create("legs");
	public static final IntegerProperty RANG = IntegerProperty.create("rank", 0, 2);

	public static class Banc extends Meuble implements Assisable {
		public static final MapCodec<Banc> CODEC = simpleCodec(Banc::new);
		private static final java.util.Map<Direction, VoxelShape> F = formes(new double[] {0, 0, 3, 16, 9.5, 13});
		public Banc(Properties p) {
			super(p);
			registerDefaultState(defaultBlockState().setValue(GAUCHE, false).setValue(DROITE, false).setValue(PIEDS, false).setValue(RANG, 0));
		}
		@Override protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, GAUCHE, DROITE, PIEDS, RANG); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return F.get(s.getValue(FACING)); }
		@Override protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) { return asseoir(s, l, p, j); }

		private boolean voisin(BlockState s, BlockState n) { return n.is(this) && n.getValue(FACING) == s.getValue(FACING); }
		/** Recalcule les raccords ; le rang compte depuis le bout gauche (0, 1, 2, 0…) : des pieds au rang 0. */
		private BlockState relier(BlockState s, LevelAccessor l, BlockPos p) {
			Direction f = s.getValue(FACING);
			BlockState g = l.getBlockState(p.relative(f.getCounterClockWise())), d = l.getBlockState(p.relative(f.getClockWise()));
			boolean vg = voisin(s, g), vd = voisin(s, d);
			int rang = vg ? (g.getValue(RANG) + 1) % 3 : 0;
			return s.setValue(GAUCHE, vg).setValue(DROITE, vd).setValue(RANG, rang).setValue(PIEDS, vg && vd && rang == 0);
		}
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return relier(super.getStateForPlacement(c), c.getLevel(), c.getClickedPos()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState n, LevelAccessor l, BlockPos p, BlockPos np) {
			return d.getAxis().isHorizontal() ? relier(s, l, p) : s;
		}
	}

	// ------------------------------------------------------------------ table : se raccorde dans les quatre sens (plateau continu, pieds aux coins libres)
	public static class Table extends Block {
		public static final MapCodec<Table> CODEC = simpleCodec(Table::new);
		private static final BooleanProperty[] COTES = {BlockStateProperties.NORTH, BlockStateProperties.EAST, BlockStateProperties.SOUTH, BlockStateProperties.WEST};
		private static final VoxelShape PLATEAU = Block.box(0, 12, 0, 16, 16, 16);
		private static final VoxelShape[] PIEDS_ = {Block.box(1, 0, 1, 3, 12, 3), Block.box(13, 0, 1, 15, 12, 3), Block.box(13, 0, 13, 15, 12, 15), Block.box(1, 0, 13, 3, 12, 15)};
		public Table(Properties p) {
			super(p);
			BlockState s = defaultBlockState(); for (BooleanProperty c : COTES) s = s.setValue(c, false); registerDefaultState(s);
		}
		@Override protected MapCodec<? extends Block> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(COTES); }
		private BlockState relier(BlockState s, LevelAccessor l, BlockPos p) {
			for (int i = 0; i < 4; i++) s = s.setValue(COTES[i], l.getBlockState(p.relative(Direction.from2DDataValue((i + 2) % 4))).is(this));
			return s;
		}
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return relier(defaultBlockState(), c.getLevel(), c.getClickedPos()); }
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState n, LevelAccessor l, BlockPos p, BlockPos np) {
			return d.getAxis().isHorizontal() ? relier(s, l, p) : s;
		}
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			VoxelShape v = PLATEAU;
			// coin libre : nord-ouest, nord-est, sud-est, sud-ouest
			for (int i = 0; i < 4; i++)
				if (!s.getValue(COTES[i]) && !s.getValue(COTES[(i + 3) % 4])) v = Shapes.or(v, PIEDS_[i]);
			return v;
		}
	}

	// ------------------------------------------------------------------ bureau : seul (9 cases) ou sur deux blocs (18 cases, une seule fenêtre)
	public enum Partie implements StringRepresentable {
		SINGLE, LEFT, RIGHT;
		@Override public String getSerializedName() { return name().toLowerCase(java.util.Locale.ROOT); }
	}
	public static final EnumProperty<Partie> PARTIE = EnumProperty.create("part", Partie.class);

	public static class Bureau extends BaseEntityBlock {
		public static final MapCodec<Bureau> CODEC = simpleCodec(Bureau::new);
		public Bureau(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(PARTIE, Partie.SINGLE)); }
		@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, PARTIE); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new Coffre(BUREAU_BE.get(), p, s, 9); }

		/** Le bloc voisin qui ferait la paire (côté gauche : la moitié droite est à sa droite). */
		private static Direction cotePartenaire(BlockState s) {
			Direction f = s.getValue(FACING);
			return s.getValue(PARTIE) == Partie.LEFT ? f.getClockWise() : f.getCounterClockWise();
		}
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			Direction f = c.getHorizontalDirection().getOpposite();
			BlockState s = defaultBlockState().setValue(FACING, f);
			Level l = c.getLevel(); BlockPos p = c.getClickedPos();
			// un bureau seul, même orientation, à gauche ou à droite : on forme un bureau de deux blocs (jamais plus)
			BlockState g = l.getBlockState(p.relative(f.getCounterClockWise())), d = l.getBlockState(p.relative(f.getClockWise()));
			if (g.is(this) && g.getValue(FACING) == f && g.getValue(PARTIE) == Partie.SINGLE) return s.setValue(PARTIE, Partie.RIGHT);
			if (d.is(this) && d.getValue(FACING) == f && d.getValue(PARTIE) == Partie.SINGLE) return s.setValue(PARTIE, Partie.LEFT);
			return s;
		}
		@Override
		public void setPlacedBy(Level l, BlockPos p, BlockState s, LivingEntity e, ItemStack st) {
			if (s.getValue(PARTIE) == Partie.SINGLE) return;
			BlockPos q = p.relative(cotePartenaire(s));
			l.setBlock(q, l.getBlockState(q).setValue(PARTIE, s.getValue(PARTIE) == Partie.LEFT ? Partie.RIGHT : Partie.LEFT), 3);
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState n, LevelAccessor l, BlockPos p, BlockPos np) {
			if (s.getValue(PARTIE) != Partie.SINGLE && d == cotePartenaire(s)) {
				Partie attendue = s.getValue(PARTIE) == Partie.LEFT ? Partie.RIGHT : Partie.LEFT;
				if (!n.is(this) || n.getValue(FACING) != s.getValue(FACING) || n.getValue(PARTIE) != attendue) return s.setValue(PARTIE, Partie.SINGLE);
			}
			return s;
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (l.isClientSide || !(j instanceof ServerPlayer sp) || !(l.getBlockEntity(p) instanceof Coffre ici)) return InteractionResult.sidedSuccess(l.isClientSide);
			Container c = ici; int rangs = 1;
			if (s.getValue(PARTIE) != Partie.SINGLE && l.getBlockEntity(p.relative(cotePartenaire(s))) instanceof Coffre autre) {
				// la moitié gauche d'abord, comme on lit le bureau de face
				c = s.getValue(PARTIE) == Partie.LEFT ? new CompoundContainer(ici, autre) : new CompoundContainer(autre, ici); rangs = 2;
			}
			Container fc = c; int fr = rangs;
			sp.openMenu(new SimpleMenuProvider((id, inv, pl) -> new ChestMenu(fr == 1 ? MenuType.GENERIC_9x1 : MenuType.GENERIC_9x2, id, inv, fc, fr),
				Component.translatable("block.airain.imperial_desk")));
			l.playSound(null, p, SoundEvents.CHISELED_BOOKSHELF_PICKUP, SoundSource.BLOCKS, 0.6f, 0.8f);
			return InteractionResult.CONSUME;
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof Coffre c) Containers.dropContents(l, p, c);
			super.onRemove(s, l, p, n, deplace);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return Shapes.block(); }
	}

	// ------------------------------------------------------------------ armoire : deux blocs, 9 sets d'armure dans le bas (1.71.1)
	public static class Armoire extends Double implements net.minecraft.world.level.block.EntityBlock {
		public static final MapCodec<Armoire> CODEC = simpleCodec(Armoire::new);
		private static final java.util.Map<Direction, VoxelShape> F = formes(new double[] {0, 0, 0.5, 16, 16, 16});
		public Armoire(Properties p) { super(p); }
		@Override protected MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return F.get(s.getValue(FACING)); }
		@Override public @org.jetbrains.annotations.Nullable BlockEntity newBlockEntity(BlockPos p, BlockState s) {
			return s.getValue(HALF) == DoubleBlockHalf.LOWER ? new Coffre(ARMOIRE_BE.get(), p, s, ArmoireMenu.CASES) : null;
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			BlockPos b = bas(s, p);
			if (!l.isClientSide && j instanceof ServerPlayer sp && l.getBlockEntity(b) instanceof Coffre c) {
				sp.openMenu(new SimpleMenuProvider((id, inv, pl) -> new ArmoireMenu(id, inv, c), Component.translatable("block.airain.imperial_wardrobe")));
				l.playSound(null, b, SoundEvents.WOODEN_DOOR_OPEN, SoundSource.BLOCKS, 0.7f, 0.9f);
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof Coffre c) Containers.dropContents(l, p, c);
			super.onRemove(s, l, p, n, deplace);
		}
	}

	/** Rangement simple (bureau, armoire). */
	public static class Coffre extends BlockEntity implements Container {
		private final NonNullList<ItemStack> objets;
		public Coffre(BlockEntityType<?> t, BlockPos p, BlockState s, int n) { super(t, p, s); objets = NonNullList.withSize(n, ItemStack.EMPTY); }
		@Override public int getContainerSize() { return objets.size(); }
		@Override public boolean isEmpty() { for (ItemStack s : objets) if (!s.isEmpty()) return false; return true; }
		@Override public ItemStack getItem(int i) { return objets.get(i); }
		@Override public ItemStack removeItem(int i, int n) { ItemStack r = ContainerHelper.removeItem(objets, i, n); if (!r.isEmpty()) setChanged(); return r; }
		@Override public ItemStack removeItemNoUpdate(int i) { return ContainerHelper.takeItem(objets, i); }
		@Override public void setItem(int i, ItemStack s) { objets.set(i, s); setChanged(); }
		@Override public boolean stillValid(Player j) { return level != null && level.getBlockEntity(worldPosition) == this && j.distanceToSqr(worldPosition.getCenter()) < 64; }
		@Override public void clearContent() { objets.clear(); setChanged(); }
		@Override protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); ContainerHelper.saveAllItems(t, objets, r); }
		@Override protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) { super.loadAdditional(t, r); objets.clear(); ContainerHelper.loadAllItems(t, objets, r); }
	}

	// ------------------------------------------------------------------ étagère : 2 niveaux de 3 places ; on pose et on reprend à la main, les objets se voient
	public static class Etagere extends BaseEntityBlock {
		public static final MapCodec<Etagere> CODEC = simpleCodec(Etagere::new);
		private static final java.util.Map<Direction, VoxelShape> F = formes(new double[] {0, 0, 4, 1.5, 16, 16}, new double[] {14.5, 0, 4, 16, 16, 16},
			new double[] {1.5, 0, 15, 14.5, 16, 16}, new double[] {1.5, 0, 4, 14.5, 1.5, 15}, new double[] {1.5, 7, 4, 14.5, 8.5, 15}, new double[] {1.5, 14.5, 4, 14.5, 16, 15});
		public Etagere(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH)); }
		@Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection().getOpposite()); }
		@Override protected RenderShape getRenderShape(BlockState s) { return RenderShape.MODEL; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new Presentoir(p, s); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return F.get(s.getValue(FACING)); }

		/** Place visée : colonne selon la largeur (3), niveau selon la hauteur (2) ; -1 hors des niches. */
		static int place(BlockState s, BlockPos p, Vec3 hit) {
			double wx = hit.x - p.getX(), wz = hit.z - p.getZ(), y = (hit.y - p.getY()) * 16, mx;
			switch (s.getValue(FACING)) {
				case EAST -> mx = wz;
				case SOUTH -> mx = 1 - wx;
				case WEST -> mx = 1 - wz;
				default -> mx = wx;
			}
			int col = (int) Math.floor((mx * 16 - 1.5) / (13 / 3.0));
			if (col < 0 || col > 2 || y < 1 || y > 14.5) return -1;
			return (y < 7.75 ? 0 : 3) + col;
		}
		@Override
		protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand m, BlockHitResult h) {
			if (!(l.getBlockEntity(p) instanceof Presentoir pr)) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			int i = place(s, p, h.getLocation());
			if (i < 0 || !pr.objets.get(i).isEmpty()) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			if (!l.isClientSide) {
				pr.objets.set(i, st.copyWithCount(1)); if (!j.isCreative()) st.shrink(1); pr.maj();
				l.playSound(null, p, SoundEvents.CHISELED_BOOKSHELF_INSERT, SoundSource.BLOCKS, 0.8f, 1f);
			}
			return ItemInteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!(l.getBlockEntity(p) instanceof Presentoir pr)) return InteractionResult.PASS;
			int i = place(s, p, h.getLocation());
			if (i < 0 || pr.objets.get(i).isEmpty()) return InteractionResult.PASS;
			if (!l.isClientSide) {
				j.getInventory().placeItemBackInInventory(pr.objets.get(i).copy()); pr.objets.set(i, ItemStack.EMPTY); pr.maj();
				l.playSound(null, p, SoundEvents.CHISELED_BOOKSHELF_PICKUP, SoundSource.BLOCKS, 0.8f, 1f);
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof Presentoir pr)
				for (ItemStack st : pr.objets) Containers.dropItemStack(l, p.getX() + .5, p.getY() + .5, p.getZ() + .5, st);
			super.onRemove(s, l, p, n, deplace);
		}
	}

	public static class Presentoir extends BlockEntity {
		public final NonNullList<ItemStack> objets = NonNullList.withSize(6, ItemStack.EMPTY);
		public Presentoir(BlockPos p, BlockState s) { super(ETAGERE_BE.get(), p, s); }
		void maj() { setChanged(); if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3); }
		@Override protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) { super.saveAdditional(t, r); ContainerHelper.saveAllItems(t, objets, true, r); }
		@Override protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) {
			super.loadAdditional(t, r); java.util.Collections.fill(objets, ItemStack.EMPTY); ContainerHelper.loadAllItems(t, objets, r);
		}
		@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
		@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
	}

	/** Pour l'entité de siège : le bloc porte-t-il encore un meuble où s'asseoir ? */
	public static boolean assisable(BlockState s) { return s.getBlock() instanceof Assisable; }
}
