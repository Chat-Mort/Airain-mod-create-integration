package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.serialization.MapCodec;
import com.simibubi.create.content.kinetics.base.IRotate;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import com.simibubi.create.foundation.blockEntity.SmartBlockEntity;
import com.simibubi.create.foundation.blockEntity.behaviour.BlockEntityBehaviour;
import com.simibubi.create.foundation.blockEntity.behaviour.ValueBoxTransform;
import com.simibubi.create.foundation.blockEntity.behaviour.ValueSettingsBoard;
import com.simibubi.create.foundation.blockEntity.behaviour.ValueSettingsFormatter;
import com.simibubi.create.foundation.blockEntity.behaviour.scrollValue.ScrollValueBehaviour;
import dev.engine_room.flywheel.lib.transform.TransformStack;
import fr.chatmort.airain.AirainMod;
import net.createmod.catnip.math.AngleHelper;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.FaceAttachedHorizontalDirectionalBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.ArrayList;
import java.util.List;

/**
 * Le monte-charge d'airain : un treuil (rotation de Create) au pied d'un mât à crémaillère (jusqu'à 32 blocs), une cabine
 * qui monte et descend contre le mât. Chaque passerelle basse posée en face du mât (de l'autre côté de la cabine) est un
 * étage ; le pied du mât est le rez-de-chaussée. Les paliers gardent leur rambarde tant que la cabine n'y est pas arrêtée.
 * Dans la cabine : clic droit = étage du dessus, accroupi = étage du dessous ; clic droit maintenu sur le panneau du
 * boîtier = tableau de Create pour choisir l'étage. Boîtier d'appel : fait venir la cabine à son étage.
 */
public final class MonteCharge {
	private MonteCharge() {}

	public static final int HAUTEUR_MAX = 32;
	static String nom(int i) { return i == 0 ? Component.translatable("airain.ascenseur.rdc").getString() : String.valueOf(i); }

	/** (x, z) d'une pièce décrite face au nord, tournée vers f (repère du bloc, en blocs). */
	static Vec3 tourne(Direction f, double x, double y, double z) {
		return switch (f) { case EAST -> new Vec3(1 - z, y, x); case SOUTH -> new Vec3(1 - x, y, 1 - z); case WEST -> new Vec3(z, y, 1 - x); default -> new Vec3(x, y, z); };
	}
	static Direction tourne(Direction f, Direction d) {
		int k = switch (f) { case EAST -> 1; case SOUTH -> 2; case WEST -> 3; default -> 0; };
		for (int i = 0; i < k; i++) d = d.getClockWise();
		return d;
	}

	// ====================================================================== le mât (FACING : côté de la cabine)
	public static class Mat extends Block {
		private static final VoxelShape FORME = Block.box(1, 0, 1, 15, 16, 15);
		public Mat(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING); }
		// la cabine passe du côté du joueur ; sur un mât existant, on garde son orientation
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			BlockState dessous = c.getLevel().getBlockState(c.getClickedPos().below());
			Direction f = dessous.getBlock() instanceof Mat ? dessous.getValue(BlockStateProperties.HORIZONTAL_FACING) : c.getHorizontalDirection().getOpposite();
			return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, f);
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	}

	// ====================================================================== le treuil (sous le mât ; l'arbre entre par les côtés)
	public static class Treuil extends Block implements EntityBlock, IRotate {
		public Treuil(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_AXIS, Direction.Axis.X)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_AXIS); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_AXIS, c.getHorizontalDirection().getAxis()); }
		@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return d.getAxis() == s.getValue(BlockStateProperties.HORIZONTAL_AXIS); }
		@Override public Direction.Axis getRotationAxis(BlockState s) { return s.getValue(BlockStateProperties.HORIZONTAL_AXIS); }
		@Override
		protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
			super.onPlace(s, l, p, ancien, deplace);
			if (l.getBlockEntity(p) instanceof KineticBlockEntity k) { k.preventSpeedUpdate = 0; if (ancien.getBlock() == s.getBlock() && ancien.getValue(BlockStateProperties.HORIZONTAL_AXIS) == s.getValue(BlockStateProperties.HORIZONTAL_AXIS)) k.preventSpeedUpdate = 2; }
		}
		@Override
		protected void updateIndirectNeighbourShapes(BlockState s, LevelAccessor l, BlockPos p, int flags, int count) {
			if (l.isClientSide() || !(l.getBlockEntity(p) instanceof KineticBlockEntity k) || k.preventSpeedUpdate > 0) return;
			k.warnOfMovement(); k.clearKineticInformation(); k.updateSpeed = true;
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof TreuilBlockEntity t) t.demonter();
			super.onRemove(s, l, p, n, deplace);
		}
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new TreuilBlockEntity(TREUIL_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return t == TREUIL_BE.get() ? (lv, p, st, be) -> ((TreuilBlockEntity) be).tick() : null;
		}
	}

	// ====================================================================== le treuil : il connaît le mât, les étages, et déplace la cabine
	public static class TreuilBlockEntity extends KineticBlockEntity {
		public float pos = 1, posAvant = 1;
		private int cible = 1;
		public boolean mouvement;
		public Direction face = Direction.NORTH;
		private final List<Integer> etages = new ArrayList<>();
		private int attente;

		public TreuilBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); etages.add(1); }

		BlockPos colonne(int o) { return worldPosition.above(o).relative(face); }
		public List<Integer> etages() { return etages; }
		public int etageCourant() { int i = etages.indexOf(Math.round(pos)); return Math.max(0, i); }

		/** Relit le mât (hauteur, côté de la cabine) et ses paliers. */
		private int lire() {
			int h = 0;
			while (h < HAUTEUR_MAX && level.getBlockState(worldPosition.above(h + 1)).getBlock() instanceof Mat) h++;
			if (h == 0) return 0;
			face = level.getBlockState(worldPosition.above(1)).getValue(BlockStateProperties.HORIZONTAL_FACING);
			etages.clear(); etages.add(1);
			for (int o = 2; o <= h; o++) {
				BlockState s = level.getBlockState(worldPosition.above(o).relative(face, 2));
				if (s.getBlock() instanceof Passerelle.Plancher && !s.getValue(Passerelle.HAUT) && !s.getValue(Passerelle.RENTRE)) etages.add(o);
			}
			return h;
		}
		/** Commandes (côté serveur). */
		public void allerA(int o, Player qui) {
			if (mouvement || !etages.contains(o) || o == Math.round(pos)) return;
			if (getSpeed() == 0) { if (qui != null) qui.displayClientMessage(Component.translatable("airain.ascenseur.immobile").withStyle(ChatFormatting.RED), true); return; }
			int a = Math.round(pos), d = o > a ? 1 : -1;
			for (int y = a + d; y != o + d; y += d) {
				BlockState s = level.getBlockState(colonne(y));
				if (!s.isAir() && !(s.getBlock() instanceof Cabine)) { if (qui != null) qui.displayClientMessage(Component.translatable("airain.ascenseur.bloque").withStyle(ChatFormatting.RED), true); return; }
			}
			cible = o;
			BlockPos c = colonne(a);
			if (level.getBlockState(c).getBlock() instanceof Cabine) level.setBlock(c, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), Block.UPDATE_ALL);
			mouvement = true;
			level.playSound(null, c, SoundEvents.IRON_DOOR_CLOSE, SoundSource.BLOCKS, 0.7f, 0.7f);
			sendData();
		}
		public void monter(Player qui) { int i = etages.indexOf(Math.round(pos)); if (i >= 0 && i + 1 < etages.size()) allerA(etages.get(i + 1), qui); }
		public void descendre(Player qui) { int i = etages.indexOf(Math.round(pos)); if (i > 0) allerA(etages.get(i - 1), qui); }

		private void poserCabine() {
			BlockPos c = colonne(Math.round(pos));
			if (!level.getBlockState(c).isAir() && !(level.getBlockState(c).getBlock() instanceof Cabine)) return;
			level.setBlock(c, CABINE.get().defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, face), Block.UPDATE_ALL);
			if (level.getBlockEntity(c) instanceof CabineBlockEntity cb) cb.configurer(worldPosition, etages.size(), etageCourant());
		}
		void demonter() {
			if (level == null || level.isClientSide) return;
			BlockPos c = colonne(Math.round(pos));
			if (level.getBlockState(c).getBlock() instanceof Cabine) level.removeBlock(c, false);
		}

		@Override
		public void tick() {
			super.tick();
			if (level == null) return;
			if (!level.isClientSide && !mouvement && --attente <= 0) {
				attente = 20;
				int n = etages.size();
				int h = lire();
				if (h > 0) {
					if (pos > h) pos = posAvant = 1;
					BlockState ici = level.getBlockState(colonne(Math.round(pos)));
					if (!(ici.getBlock() instanceof Cabine)) poserCabine();
					else if (n != etages.size() && level.getBlockEntity(colonne(Math.round(pos))) instanceof CabineBlockEntity cb) cb.configurer(worldPosition, etages.size(), etageCourant());
				}
			}
			posAvant = pos;
			if (!mouvement) return;
			float v = Math.abs(getSpeed()) / 256f * 0.25f;
			if (v <= 0) return;
			float d = Math.signum(cible - pos);
			pos = d > 0 ? Math.min(cible, pos + v) : Math.max(cible, pos - v);
			porter(pos - posAvant);
			if (pos == cible && !level.isClientSide) {
				mouvement = false;
				poserCabine();
				level.playSound(null, colonne(cible), SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 0.7f, 0.8f);
				sendData();
			}
		}
		/** Ce qui est dans la cabine suit son plancher. */
		private void porter(float dy) {
			BlockPos c = colonne(0);
			double sol = worldPosition.getY() + pos + 3 / 16.0;
			AABB boite = new AABB(c.getX(), sol - 0.6, c.getZ(), c.getX() + 1, sol + 2, c.getZ() + 1);
			for (Entity e : level.getEntities((Entity) null, boite)) {
				if (e.isSpectator() || e.noPhysics) continue;
				if (level.isClientSide && !(e instanceof Player p && p.isLocalPlayer())) continue;
				if (!level.isClientSide && e instanceof Player) continue;            // le joueur se déplace chez lui
				Vec3 m = e.getDeltaMovement();
				double rattrape = (sol - e.getY()) * 0.5;
				e.setDeltaMovement(m.x * 0.5, dy + Math.max(0, rattrape) + (dy < 0 ? Math.min(0, rattrape) : 0), m.z * 0.5);
				if (e.getY() < sol) e.setPos(e.getX(), sol, e.getZ());
				e.fallDistance = 0;
				e.setOnGround(true);
			}
		}

		@Override
		public void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			t.putFloat("pos", pos); t.putInt("cible", cible); t.putBoolean("mouvement", mouvement); t.putInt("face", face.get2DDataValue());
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			boolean m = t.getBoolean("mouvement");
			cible = t.getInt("cible"); face = Direction.from2DDataValue(t.getInt("face"));
			if (!client || !m || !mouvement || Math.abs(t.getFloat("pos") - pos) > 1.5f) { pos = t.contains("pos") ? t.getFloat("pos") : 1; posAvant = pos; }
			mouvement = m;
			if (cible < 1) cible = 1;
		}
		@Override public AABB getRenderBoundingBox() { return new AABB(worldPosition).expandTowards(0, HAUTEUR_MAX + 1, 0).inflate(2); }
		@Override
		public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
			super.addToGoggleTooltip(t, accroupi);
			t.add(Component.literal("    ").append(Component.translatable("block.airain.airain_lift_winch")).withStyle(ChatFormatting.GOLD));
			t.add(Component.literal("    ").append(Component.translatable("airain.ascenseur.nb_etages", etages.size())).withStyle(ChatFormatting.GRAY));
			return true;
		}
	}

	// ====================================================================== la cabine (posée par le treuil à l'arrêt ; FACING : son portail)
	public static class Cabine extends Block implements EntityBlock {
		private static final java.util.Map<Direction, VoxelShape> FORMES = new java.util.EnumMap<>(Direction.class);
		static {
			for (Direction d : Direction.Plane.HORIZONTAL)
				FORMES.put(d, Shapes.or(Block.box(0, 1, 0, 16, 3, 16), ConduitAir.boiteVers(d, 0, 3, 0, 1, 16, 16), ConduitAir.boiteVers(d, 15, 3, 0, 16, 16, 16), ConduitAir.boiteVers(d, 0, 3, 15, 16, 16, 16)));
		}
		public Cabine(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH)); }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(BlockStateProperties.HORIZONTAL_FACING); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(s.getValue(BlockStateProperties.HORIZONTAL_FACING)); }
		// ailleurs que sur le panneau : clic droit = étage du dessus, accroupi = étage du dessous
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!l.isClientSide && l.getBlockEntity(p) instanceof CabineBlockEntity cb && cb.treuil() != null) {
				if (j.isShiftKeyDown()) cb.treuil().descendre(j); else cb.treuil().monter(j);
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new CabineBlockEntity(CABINE_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return t == CABINE_BE.get() ? (lv, p, st, be) -> ((CabineBlockEntity) be).tick() : null;
		}
	}

	/** Le boîtier de la cabine : un panneau de valeur de Create (clic maintenu : tableau des étages ; clic court : monter). */
	public static class CabineBlockEntity extends SmartBlockEntity {
		private BlockPos treuil;
		private int nEtages = 1;
		private Selecteur selecteur;
		public CabineBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }
		@Override
		public void addBehaviours(List<BlockEntityBehaviour> b) {
			selecteur = new Selecteur(this);
			b.add(selecteur);
		}
		TreuilBlockEntity treuil() { return treuil != null && level != null && level.getBlockEntity(treuil) instanceof TreuilBlockEntity t ? t : null; }
		void configurer(BlockPos t, int n, int ici) {
			treuil = t; nEtages = Math.max(1, n);
			selecteur.between(0, nEtages - 1);
			selecteur.value = Math.min(ici, nEtages - 1);
			setChanged(); sendData();
		}
		@Override
		protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			if (treuil != null) t.putLong("treuil", treuil.asLong());
			t.putInt("etages", nEtages);
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			treuil = t.contains("treuil") ? BlockPos.of(t.getLong("treuil")) : null;
			nEtages = Math.max(1, t.getInt("etages"));
			if (selecteur != null) selecteur.between(0, nEtages - 1);
		}

		class Selecteur extends ScrollValueBehaviour {
			Selecteur(CabineBlockEntity be) {
				super(Component.translatable("airain.ascenseur.etage"), be, new Panneau());
				withFormatter(MonteCharge::nom);
				withCallback(i -> { TreuilBlockEntity t = treuil(); if (t != null && i < t.etages().size()) t.allerA(t.etages().get(i), null); });
			}
			@Override
			public ValueSettingsBoard createBoard(Player p, BlockHitResult h) {
				return new ValueSettingsBoard(label, max, 1, List.of(Component.translatable("airain.ascenseur.etage")),
					new ValueSettingsFormatter(vs -> Component.literal(nom(vs.value()))));
			}
			// clic court sur le panneau : un étage plus haut
			@Override
			public void onShortInteract(Player p, InteractionHand m, Direction cote, BlockHitResult h) {
				if (getWorld().isClientSide) return;
				TreuilBlockEntity t = treuil();
				if (t != null) t.monter(p);
			}
		}
	}
	/** Position du panneau : sur le boîtier, côté intérieur de la rambarde droite de la cabine. */
	static class Panneau extends ValueBoxTransform {
		@Override
		public Vec3 getLocalOffset(LevelAccessor l, BlockPos p, BlockState s) {
			return tourne(s.getValue(BlockStateProperties.HORIZONTAL_FACING), 12.9 / 16, 9.5 / 16, 4.5 / 16);
		}
		@Override
		public void rotate(LevelAccessor l, BlockPos p, BlockState s, PoseStack ms) {
			Direction cote = tourne(s.getValue(BlockStateProperties.HORIZONTAL_FACING), Direction.WEST);
			TransformStack.of(ms).rotateYDegrees(AngleHelper.horizontalAngle(cote) + 180);
		}
	}

	// ====================================================================== le boîtier d'appel (sur un mur ou un poteau, près du mât)
	public static class Appel extends FaceAttachedHorizontalDirectionalBlock {
		public static final MapCodec<Appel> CODEC = simpleCodec(Appel::new);
		public Appel(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(FACE, AttachFace.WALL)); }
		@Override protected MapCodec<? extends FaceAttachedHorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, FACE); }
		@Override protected boolean canSurvive(BlockState s, LevelReader l, BlockPos p) { return !l.getBlockState(p.relative(getConnectedDirection(s).getOpposite())).isAir(); }
		@Override
		protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) {
			if (s.getValue(FACE) == AttachFace.FLOOR) return Block.box(5, 0, 5, 11, 4, 11);
			if (s.getValue(FACE) == AttachFace.CEILING) return Block.box(5, 12, 5, 11, 16, 11);
			return ConduitAir.boiteVers(s.getValue(FACING), 5, 4, 13, 11, 12, 16);
		}
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (l.isClientSide) return InteractionResult.SUCCESS;
			TreuilBlockEntity t = chercher(l, p);
			if (t == null) { j.displayClientMessage(Component.translatable("airain.ascenseur.aucun").withStyle(ChatFormatting.RED), true); return InteractionResult.SUCCESS; }
			int o = p.getY() - t.getBlockPos().getY(), mieux = t.etages().get(0);
			for (int e : t.etages()) if (Math.abs(e - o) < Math.abs(mieux - o)) mieux = e;
			l.playSound(null, p, SoundEvents.STONE_BUTTON_CLICK_ON, SoundSource.BLOCKS, 0.6f, 1.2f);
			t.allerA(mieux, j);
			return InteractionResult.SUCCESS;
		}
		/** Un mât à moins de 2 blocs (à la même hauteur, ou un bloc plus haut ou plus bas), puis son treuil. */
		static TreuilBlockEntity chercher(Level l, BlockPos p) {
			for (int dy = 0; dy <= 2; dy++)
				for (int s : new int[]{0, 1, -1}) {
					int y = dy == 0 ? 0 : dy * s; if (dy > 0 && s == 0) continue;
					for (int dx = -2; dx <= 2; dx++) for (int dz = -2; dz <= 2; dz++) {
						BlockPos q = p.offset(dx, y, dz);
						if (!(l.getBlockState(q).getBlock() instanceof Mat)) continue;
						while (l.getBlockState(q).getBlock() instanceof Mat) q = q.below();
						if (l.getBlockEntity(q) instanceof TreuilBlockEntity t) return t;
					}
				}
			return null;
		}
	}

	// ====================================================================== enregistrement
	private static BlockBehaviour.Properties airain() {
		return BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion()
			.isValidSpawn((a, b, c, d) -> false).isRedstoneConductor((a, b, c) -> false).isSuffocating((a, b, c) -> false).isViewBlocking((a, b, c) -> false);
	}
	public static final DeferredBlock<Treuil> TREUIL = AirainMod.BLOCKS.register("airain_lift_winch", () -> new Treuil(airain()));
	public static final DeferredBlock<Mat> MAT = AirainMod.BLOCKS.register("airain_lift_mast", () -> new Mat(airain()));
	public static final DeferredBlock<Cabine> CABINE = AirainMod.BLOCKS.register("airain_lift_cabin", () -> new Cabine(airain().strength(-1f, 3600000f).noLootTable()));
	public static final DeferredBlock<Appel> APPEL = AirainMod.BLOCKS.register("airain_lift_call_box", () -> new Appel(airain().noCollission().strength(1.5f, 6f)));
	static {
		AirainMod.ITEMS.register("airain_lift_winch", () -> new BlockItem(TREUIL.get(), new Item.Properties()));
		AirainMod.ITEMS.register("airain_lift_mast", () -> new BlockItem(MAT.get(), new Item.Properties()));
		AirainMod.ITEMS.register("airain_lift_call_box", () -> new BlockItem(APPEL.get(), new Item.Properties()));
	}
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TreuilBlockEntity>> TREUIL_BE = AirainMod.BLOCK_ENTITIES.register("airain_lift_winch",
		() -> BlockEntityType.Builder.of((p, s) -> new TreuilBlockEntity(MonteCharge.TREUIL_BE.get(), p, s), TREUIL.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<CabineBlockEntity>> CABINE_BE = AirainMod.BLOCK_ENTITIES.register("airain_lift_cabin",
		() -> BlockEntityType.Builder.of((p, s) -> new CabineBlockEntity(MonteCharge.CABINE_BE.get(), p, s), CABINE.get()).build(null));

	public static void charger() {}
}
