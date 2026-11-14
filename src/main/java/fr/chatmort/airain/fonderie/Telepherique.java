package fr.chatmort.airain.fonderie;

import com.simibubi.create.content.kinetics.base.HorizontalKineticBlock;
import com.simibubi.create.content.kinetics.base.IRotate;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import fr.chatmort.airain.AirainMod;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Le téléphérique impérial (1.58) et son laminoir.
 *
 * Une ligne : une gare, 0 à 8 têtes de pylône, une autre gare, reliées deux à deux par du câble d'airain (clic droit avec le
 * câble sur un nœud, puis sur le suivant, à 32 blocs au plus). Une nacelle (objet posé sur une gare) fait la navette sur le
 * brin droit ; une gare entraînée par un arbre de Create règle sa vitesse. Clic droit dans la nacelle : elle part vers l'autre
 * gare ; clic droit sur une gare : elle vient. La nacelle tient seule sa route (elle garde ses points de passage) et charge
 * les tronçons qu'elle traverse.
 *
 * Laminoir : une machine de Create ; un lingot d'airain passé entre ses rouleaux donne deux fils d'airain.
 */
public final class Telepherique {
	private Telepherique() {}

	public static final int PORTEE = 32, NOEUDS_MAX = 10;
	/** Écart du brin (de part et d'autre de l'axe de la ligne) et hauteur du câble au-dessus du bas du nœud. */
	public static final double BRIN = 1.5, HAUT_GARE = 1.9, HAUT_TETE = 0.75;
	/** La plateforme pend sous le chariot. */
	public static final double SUSPENTE = 1.85;

	// ====================================================================== nœuds de ligne (gare, tête de pylône)
	/** Ce que gardent une gare et une tête de pylône : le nœud d'avant et le nœud d'après sur la ligne. */
	public interface Noeud {
		@Nullable BlockPos precedent();
		@Nullable BlockPos suivant();
		void lier(@Nullable BlockPos precedent, @Nullable BlockPos suivant);
		double hauteurCable();
		boolean estGare();
	}
	public static Noeud noeud(BlockGetter l, @Nullable BlockPos p) {
		if (p == null) return null;
		return l.getBlockEntity(p) instanceof Noeud n ? n : null;
	}
	/** Les nœuds de la ligne qui passe par p, de la gare de départ à celle d'arrivée (liste vide si la ligne n'est pas complète). */
	public static List<BlockPos> ligne(Level l, BlockPos p) {
		BlockPos debut = p; int garde = 0;
		Noeud n = noeud(l, p);
		while (n != null && n.precedent() != null && garde++ < NOEUDS_MAX + 2) { debut = n.precedent(); n = noeud(l, debut); }
		List<BlockPos> r = new ArrayList<>();
		BlockPos c = debut; n = noeud(l, c); garde = 0;
		while (n != null && garde++ < NOEUDS_MAX + 2) { r.add(c); if (n.suivant() == null) break; c = n.suivant(); n = noeud(l, c); }
		if (r.size() < 2 || !noeud(l, r.get(0)).estGare() || !noeud(l, r.get(r.size() - 1)).estGare()) return List.of();
		return r;
	}
	/** Point d'attache du câble au nœud p (centre, à la hauteur du câble). */
	public static Vec3 centre(Level l, BlockPos p) {
		Noeud n = noeud(l, p);
		return new Vec3(p.getX() + 0.5, p.getY() + (n != null ? n.hauteurCable() : 1), p.getZ() + 0.5);
	}
	/** Vers la droite de la ligne, au nœud i (moyenne des deux travées), à plat. */
	public static Vec3 droite(Vec3 avant, Vec3 ici, Vec3 apres) {
		Vec3 d = Vec3.ZERO;
		if (avant != null) d = d.add(norm(ici.subtract(avant)));
		if (apres != null) d = d.add(norm(apres.subtract(ici)));
		d = norm(d);
		return new Vec3(-d.z, 0, d.x);
	}
	private static Vec3 norm(Vec3 v) { Vec3 h = new Vec3(v.x, 0, v.z); double n = h.length(); return n < 1e-6 ? new Vec3(1, 0, 0) : h.scale(1 / n); }
	/** Points du brin droit (où roule le chariot), un par nœud. */
	public static List<Vec3> brin(Level l, List<BlockPos> ligne, double cote) {
		List<Vec3> c = new ArrayList<>();
		for (BlockPos p : ligne) c.add(centre(l, p));
		List<Vec3> r = new ArrayList<>();
		for (int i = 0; i < c.size(); i++)
			r.add(c.get(i).add(droite(i > 0 ? c.get(i - 1) : null, c.get(i), i + 1 < c.size() ? c.get(i + 1) : null).scale(cote)));
		return r;
	}
	/** Le câble entre a et b, avec son affaissement (t de 0 à 1). */
	public static Vec3 chainette(Vec3 a, Vec3 b, double t) {
		double fl = 0.035 * Math.hypot(b.x - a.x, b.z - a.z);
		return a.lerp(b, t).subtract(0, fl * 4 * t * (1 - t), 0);
	}

	// ====================================================================== la gare (deux blocs : le bas porte la machine, le haut la poulie)
	public static final BooleanProperty HAUT = BooleanProperty.create("upper");
	public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;

	public static class Gare extends HorizontalDirectionalBlock implements EntityBlock, IRotate {
		public static final com.mojang.serialization.MapCodec<Gare> CODEC = simpleCodec(Gare::new);
		private static final VoxelShape BAS = Shapes.or(Block.box(0, 0, 0, 16, 8, 16), Block.box(4, 8, 4, 12, 16, 12));
		private static final VoxelShape DESSUS = Shapes.or(Block.box(5, 0, 5, 11, 10, 11), Block.box(2, 10, 2, 14, 16, 14));
		public Gare(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH).setValue(HAUT, false)); }
		@Override protected com.mojang.serialization.MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING, HAUT); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			if (!c.getLevel().getBlockState(c.getClickedPos().above()).canBeReplaced(c)) return null;
			return defaultBlockState().setValue(FACING, c.getHorizontalDirection());
		}
		@Override
		public void setPlacedBy(Level l, BlockPos p, BlockState s, @Nullable LivingEntity qui, ItemStack st) {
			l.setBlock(p.above(), s.setValue(HAUT, true), Block.UPDATE_ALL);
		}
		@Override
		protected BlockState updateShape(BlockState s, Direction d, BlockState v, LevelAccessor l, BlockPos p, BlockPos np) {
			boolean haut = s.getValue(HAUT);
			if (d == (haut ? Direction.DOWN : Direction.UP) && !(v.getBlock() instanceof Gare && v.getValue(HAUT) != haut)) return net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
			return s;
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return s.getValue(HAUT) ? DESSUS : BAS; }
		// Create : l'arbre arrive par-dessous
		@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return !s.getValue(HAUT) && d == Direction.DOWN; }
		@Override public Direction.Axis getRotationAxis(BlockState s) { return Direction.Axis.Y; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return s.getValue(HAUT) ? null : new GareBlockEntity(GARE_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return t == GARE_BE.get() ? (lv, p, st, be) -> ((GareBlockEntity) be).tick() : null;
		}
		@Override
		protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
			super.onPlace(s, l, p, ancien, deplace);
			if (l.getBlockEntity(p) instanceof KineticBlockEntity k) { k.preventSpeedUpdate = 0; if (ancien.getBlock() == s.getBlock()) k.preventSpeedUpdate = 2; }
		}
		@Override
		protected void updateIndirectNeighbourShapes(BlockState s, LevelAccessor l, BlockPos p, int flags, int count) {
			if (l.isClientSide() || !(l.getBlockEntity(p) instanceof KineticBlockEntity k) || k.preventSpeedUpdate > 0) return;
			k.warnOfMovement(); k.clearKineticInformation(); k.updateSpeed = true;
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && !s.getValue(HAUT)) delier(l, p);
			super.onRemove(s, l, p, n, deplace);
		}
		// clic droit main nue : appeler la nacelle
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			BlockPos bas = s.getValue(HAUT) ? p.below() : p;
			if (!l.isClientSide && l.getBlockEntity(bas) instanceof GareBlockEntity g) g.appeler(j);
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand m, BlockHitResult h) {
			BlockPos bas = s.getValue(HAUT) ? p.below() : p;
			if (st.is(CABLE.get())) return Cable.relier(st, l, bas, j);
			if (st.is(NACELLE_ITEM.get())) {
				if (!l.isClientSide && l.getBlockEntity(bas) instanceof GareBlockEntity g) { if (g.installer(j) && !j.getAbilities().instabuild) st.shrink(1); }
				return ItemInteractionResult.sidedSuccess(l.isClientSide);
			}
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		}
	}

	/** Défait les liens d'un nœud (câbles rendus), et retire la nacelle de la ligne. */
	static void delier(Level l, BlockPos p) {
		if (l.isClientSide) return;
		Noeud n = noeud(l, p);
		if (n == null) return;
		int cables = 0;
		for (BlockPos q : new BlockPos[]{n.precedent(), n.suivant()}) {
			Noeud m = noeud(l, q);
			if (m == null) continue;
			cables++;
			if (p.equals(m.precedent())) m.lier(null, m.suivant());
			if (p.equals(m.suivant())) m.lier(m.precedent(), null);
		}
		n.lier(null, null);
		if (cables > 0) Block.popResource(l, p, new ItemStack(CABLE.get(), cables));
		Nacelle.retirerDe(l, p);
	}

	public static class GareBlockEntity extends KineticBlockEntity implements Noeud {
		private BlockPos precedent, suivant;
		@Nullable public UUID nacelle;
		/** Côté client : la nacelle bouge (la poulie tourne) ; angle de la poulie. */
		public boolean tourne; public float angle, angleAvant;
		private int relance;
		public GareBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }
		@Override public BlockPos precedent() { return precedent; }
		@Override public BlockPos suivant() { return suivant; }
		@Override public void lier(BlockPos a, BlockPos b) { precedent = a; suivant = b; setChanged(); sendData(); }
		@Override public double hauteurCable() { return HAUT_GARE; }
		@Override public boolean estGare() { return true; }

		/** Pose une nacelle (objet en main) sur la ligne complète, à cette gare. */
		boolean installer(Player j) {
			List<BlockPos> L = ligne(level, worldPosition);
			if (L.isEmpty()) { j.displayClientMessage(Component.translatable("airain.telepherique.incomplete").withStyle(ChatFormatting.RED), true); return false; }
			if (trouverNacelle() != null || autreGare(L) instanceof GareBlockEntity g && g.trouverNacelle() != null) {
				j.displayClientMessage(Component.translatable("airain.telepherique.deja").withStyle(ChatFormatting.RED), true); return false;
			}
			Nacelle n = Nacelle.creer(level, L, worldPosition.equals(L.get(0)) ? 0 : 1);
			if (n == null) return false;
			for (BlockPos g : new BlockPos[]{L.get(0), L.get(L.size() - 1)}) if (level.getBlockEntity(g) instanceof GareBlockEntity ge) { ge.nacelle = n.getUUID(); ge.setChanged(); }
			level.playSound(null, worldPosition, SoundEvents.ANVIL_PLACE, SoundSource.BLOCKS, 0.5f, 1.4f);
			return true;
		}
		private BlockEntity autreGare(List<BlockPos> L) {
			BlockPos o = worldPosition.equals(L.get(0)) ? L.get(L.size() - 1) : L.get(0);
			return level.getBlockEntity(o);
		}
		@Nullable Nacelle trouverNacelle() {
			if (nacelle == null || !(level instanceof ServerLevel sl)) return null;
			return sl.getEntity(nacelle) instanceof Nacelle n && n.isAlive() ? n : null;
		}
		/** Clic droit sur la gare : la nacelle vient (on charge son tronçon si elle est loin). */
		void appeler(Player j) {
			Nacelle n = trouverNacelle();
			if (n == null) {
				if (nacelle == null) { j.displayClientMessage(Component.translatable("airain.telepherique.sans_nacelle").withStyle(ChatFormatting.RED), true); return; }
				// la nacelle dort dans un tronçon non chargé : on réveille l'autre gare et on réessaie
				List<BlockPos> L = ligne(level, worldPosition);
				if (!L.isEmpty() && level instanceof ServerLevel sl) {
					BlockPos o = worldPosition.equals(L.get(0)) ? L.get(L.size() - 1) : L.get(0);
					sl.getChunkSource().addRegionTicket(net.minecraft.server.level.TicketType.PORTAL, new net.minecraft.world.level.ChunkPos(o), 3, o);
					relance = 40;
				}
				j.displayClientMessage(Component.translatable("airain.telepherique.appel").withStyle(ChatFormatting.GOLD), true);
				return;
			}
			if (n.vers(worldPosition, j)) j.displayClientMessage(Component.translatable("airain.telepherique.appel").withStyle(ChatFormatting.GOLD), true);
		}
		public float vitesse() { return Math.abs(getSpeed()); }

		@Override
		public void tick() {
			super.tick();
			if (level == null) return;
			if (level.isClientSide) {
				angleAvant = angle;
				if (tourne) angle += Math.max(2f, Math.abs(getSpeed()) / 256f * 16f);
				return;
			}
			if (relance > 0 && --relance % 10 == 0) {
				Nacelle n = trouverNacelle();
				if (n != null) { n.vers(worldPosition, null); relance = 0; }
			}
		}
		void tourne(boolean t) { if (t != tourne) { tourne = t; sendData(); } }

		@Override
		protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			if (precedent != null) t.putLong("precedent", precedent.asLong());
			if (suivant != null) t.putLong("suivant", suivant.asLong());
			if (nacelle != null) t.putUUID("nacelle", nacelle);
			t.putBoolean("tourne", tourne);
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			precedent = t.contains("precedent") ? BlockPos.of(t.getLong("precedent")) : null;
			suivant = t.contains("suivant") ? BlockPos.of(t.getLong("suivant")) : null;
			nacelle = t.hasUUID("nacelle") ? t.getUUID("nacelle") : null;
			tourne = t.getBoolean("tourne");
		}
		@Override public AABB getRenderBoundingBox() { return new AABB(worldPosition).inflate(PORTEE + 4); }

		@Override
		public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
			super.addToGoggleTooltip(t, accroupi);
			t.add(Component.literal("    ").append(Component.translatable("block.airain.airain_cable_station")).withStyle(ChatFormatting.GOLD));
			List<BlockPos> L = level == null ? List.of() : ligne(level, worldPosition);
			if (L.isEmpty()) t.add(Component.literal("    ").append(Component.translatable("airain.telepherique.incomplete")).withStyle(ChatFormatting.RED));
			else {
				double lg = 0;
				for (int i = 1; i < L.size(); i++) lg += Math.sqrt(L.get(i).distSqr(L.get(i - 1)));
				t.add(Component.literal("    ").append(Component.translatable("airain.telepherique.ligne", L.size() - 2, Math.round(lg))).withStyle(ChatFormatting.GRAY));
				if (nacelle == null) t.add(Component.literal("    ").append(Component.translatable("airain.telepherique.sans_nacelle")).withStyle(ChatFormatting.GRAY));
			}
			return true;
		}
	}

	// ====================================================================== pylône (fût empilable) et tête de pylône (nœud)
	public static class Pylone extends Block {
		private static final VoxelShape FORME = Block.box(2, 0, 2, 14, 16, 14);
		public Pylone(Properties p) { super(p); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
	}
	public static class TetePylone extends HorizontalDirectionalBlock implements EntityBlock {
		public static final com.mojang.serialization.MapCodec<TetePylone> CODEC = simpleCodec(TetePylone::new);
		private static final VoxelShape FORME = Shapes.or(Block.box(0, 0, 0, 16, 3, 16), Block.box(2, 3, 2, 14, 8, 14));
		public TetePylone(Properties p) { super(p); registerDefaultState(defaultBlockState().setValue(FACING, Direction.NORTH)); }
		@Override protected com.mojang.serialization.MapCodec<? extends HorizontalDirectionalBlock> codec() { return CODEC; }
		@Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(FACING); }
		@Override public BlockState getStateForPlacement(BlockPlaceContext c) { return defaultBlockState().setValue(FACING, c.getHorizontalDirection()); }
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORME; }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new TeteBlockEntity(TETE_BE.get(), p, s); }
		@Override
		protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand m, BlockHitResult h) {
			if (st.is(CABLE.get())) return Cable.relier(st, l, p, j);
			return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
		}
		@Override
		protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock())) delier(l, p);
			super.onRemove(s, l, p, n, deplace);
		}
	}
	public static class TeteBlockEntity extends BlockEntity implements Noeud {
		private BlockPos precedent, suivant;
		public TeteBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }
		@Override public BlockPos precedent() { return precedent; }
		@Override public BlockPos suivant() { return suivant; }
		@Override public void lier(BlockPos a, BlockPos b) {
			precedent = a; suivant = b; setChanged();
			if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
		}
		@Override public double hauteurCable() { return HAUT_TETE; }
		@Override public boolean estGare() { return false; }
		@Override
		protected void saveAdditional(CompoundTag t, HolderLookup.Provider r) {
			super.saveAdditional(t, r);
			if (precedent != null) t.putLong("precedent", precedent.asLong());
			if (suivant != null) t.putLong("suivant", suivant.asLong());
		}
		@Override
		protected void loadAdditional(CompoundTag t, HolderLookup.Provider r) {
			super.loadAdditional(t, r);
			precedent = t.contains("precedent") ? BlockPos.of(t.getLong("precedent")) : null;
			suivant = t.contains("suivant") ? BlockPos.of(t.getLong("suivant")) : null;
		}
		@Override public CompoundTag getUpdateTag(HolderLookup.Provider r) { return saveWithoutMetadata(r); }
		@Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
	}

	// ====================================================================== le câble (objet) : relie deux nœuds
	public static class Cable extends Item {
		public Cable(Properties p) { super(p); }
		/** Premier clic : le nœud est retenu ; second clic sur un autre nœud : les deux sont reliés (un câble consommé). */
		static ItemInteractionResult relier(ItemStack st, Level l, BlockPos p, Player j) {
			if (l.isClientSide) return ItemInteractionResult.SUCCESS;
			CompoundTag t = st.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
			Noeud ici = noeud(l, p);
			if (ici == null) return ItemInteractionResult.FAIL;
			if (!t.contains("depart")) {
				if (ici.suivant() != null && ici.precedent() != null) { j.displayClientMessage(Component.translatable("airain.telepherique.plein").withStyle(ChatFormatting.RED), true); return ItemInteractionResult.FAIL; }
				t.putLong("depart", p.asLong()); st.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
				j.displayClientMessage(Component.translatable("airain.telepherique.depart").withStyle(ChatFormatting.GOLD), true);
				l.playSound(null, p, SoundEvents.CHAIN_HIT, SoundSource.BLOCKS, 0.8f, 1.2f);
				return ItemInteractionResult.SUCCESS;
			}
			BlockPos a = BlockPos.of(t.getLong("depart"));
			t.remove("depart"); st.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
			if (a.equals(p)) { j.displayClientMessage(Component.translatable("airain.telepherique.annule").withStyle(ChatFormatting.GRAY), true); return ItemInteractionResult.SUCCESS; }
			Noeud na = noeud(l, a);
			double dh = Math.hypot(a.getX() - p.getX(), a.getZ() - p.getZ());
			String erreur = na == null ? "perdu" : dh > PORTEE ? "loin" : dh < 3 ? "pres" : null;
			// on relie dans le sens où c'est possible : a → p, sinon p → a
			if (erreur == null) {
				if (peutRelier(l, a, na, p, ici)) { }
				else if (peutRelier(l, p, ici, a, na)) { BlockPos x = a; a = p; p = x; Noeud y = na; na = ici; ici = y; }
				else erreur = "plein";
			}
			if (erreur == null && compter(l, a) + compter(l, p) > NOEUDS_MAX) erreur = "long";
			if (erreur != null) { j.displayClientMessage(Component.translatable("airain.telepherique." + erreur).withStyle(ChatFormatting.RED), true); return ItemInteractionResult.FAIL; }
			na.lier(na.precedent(), p);
			ici.lier(a, ici.suivant());
			orienter(l, a); orienter(l, p);
			if (!j.getAbilities().instabuild) st.shrink(1);
			l.playSound(null, p, SoundEvents.CHAIN_PLACE, SoundSource.BLOCKS, 1f, 0.8f);
			boolean complete = !ligne(l, p).isEmpty();
			j.displayClientMessage(Component.translatable(complete ? "airain.telepherique.complete_ok" : "airain.telepherique.relie").withStyle(ChatFormatting.GOLD), true);
			return ItemInteractionResult.SUCCESS;
		}
		/** Une tête de pylône se tourne dans l'axe de sa ligne (bras et galets de travers). */
		private static void orienter(Level l, BlockPos p) {
			BlockState s = l.getBlockState(p);
			Noeud n = noeud(l, p);
			if (!(s.getBlock() instanceof TetePylone) || n == null) return;
			BlockPos a = n.precedent() != null ? n.precedent() : p, b = n.suivant() != null ? n.suivant() : p;
			int dx = b.getX() - a.getX(), dz = b.getZ() - a.getZ();
			if (dx == 0 && dz == 0) return;
			Direction d = Direction.getNearest(dx, 0, dz);
			if (d.getAxis().isHorizontal() && s.getValue(TetePylone.FACING) != d) l.setBlock(p, s.setValue(TetePylone.FACING, d), Block.UPDATE_ALL);
		}
		private static int compter(Level l, BlockPos p) {
			int n = 0; BlockPos c = p; Noeud x = noeud(l, c);
			while (x != null && x.precedent() != null && n < NOEUDS_MAX + 2) { c = x.precedent(); x = noeud(l, c); }
			int k = 0;
			while (x != null && k < NOEUDS_MAX + 2) { k++; if (x.suivant() == null) break; x = noeud(l, x.suivant()); }
			return k;
		}
		/** x → y possible ? x n'a pas de suivant, y pas de précédent ; une gare reste un bout de ligne ; pas de boucle. */
		private static boolean peutRelier(Level l, BlockPos x, Noeud nx, BlockPos y, Noeud ny) {
			if (nx.suivant() != null || ny.precedent() != null) return false;
			if (nx.estGare() && nx.precedent() != null) return false;
			if (ny.estGare() && ny.suivant() != null) return false;
			BlockPos c = y; Noeud n = ny; int k = 0;
			while (n != null && k++ < NOEUDS_MAX + 2) { if (c.equals(x)) return false; c = n.suivant(); if (c == null) break; n = noeud(l, c); }
			return true;
		}
		@Override
		public void appendHoverText(ItemStack st, TooltipContext c, List<Component> t, net.minecraft.world.item.TooltipFlag f) {
			t.add(Component.translatable("airain.telepherique.cable_aide").withStyle(ChatFormatting.GRAY));
		}
		@Override public boolean isFoil(ItemStack st) { return st.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().contains("depart"); }
	}

	/** La nacelle, en objet : on la pose sur une gare d'une ligne complète. */
	public static class NacelleItem extends Item {
		public NacelleItem(Properties p) { super(p); }
		@Override
		public void appendHoverText(ItemStack st, TooltipContext c, List<Component> t, net.minecraft.world.item.TooltipFlag f) {
			t.add(Component.translatable("airain.telepherique.nacelle_aide").withStyle(ChatFormatting.GRAY));
		}
	}

	// ====================================================================== le laminoir
	public static class Laminoir extends HorizontalKineticBlock implements EntityBlock {
		private static final java.util.Map<Direction.Axis, VoxelShape> FORMES = new java.util.EnumMap<>(Direction.Axis.class);
		static {
			FORMES.put(Direction.Axis.Z, Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(1, 4, 1, 15, 16, 15)));
			FORMES.put(Direction.Axis.X, FORMES.get(Direction.Axis.Z));
		}
		public Laminoir(Properties p) { super(p); }
		// les rouleaux tournent sur l'axe perpendiculaire au passage du métal (FACING : côté sortie)
		@Override public Direction.Axis getRotationAxis(BlockState s) { return s.getValue(HORIZONTAL_FACING).getClockWise().getAxis(); }
		@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return d.getAxis() == getRotationAxis(s); }
		@Override
		public BlockState getStateForPlacement(BlockPlaceContext c) {
			return defaultBlockState().setValue(HORIZONTAL_FACING, c.getHorizontalDirection().getOpposite());
		}
		@Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return FORMES.get(Direction.Axis.Z); }
		@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new LaminoirBlockEntity(LAMINOIR_BE.get(), p, s); }
		@Override
		public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
			return t == LAMINOIR_BE.get() ? (lv, p, st, be) -> ((LaminoirBlockEntity) be).tick() : null;
		}
		@Override
		protected ItemInteractionResult useItemOn(ItemStack st, BlockState s, Level l, BlockPos p, Player j, InteractionHand m, BlockHitResult h) {
			if (!(l.getBlockEntity(p) instanceof LaminoirBlockEntity be)) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			if (!LaminoirBlockEntity.accepte(st)) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
			if (!l.isClientSide) {
				ItemStack reste = be.entree.insertItem(0, st.copy(), false);
				if (!j.getAbilities().instabuild) j.setItemInHand(m, reste);
				l.playSound(null, p, SoundEvents.ITEM_FRAME_ADD_ITEM, SoundSource.BLOCKS, 0.8f, 1f);
			}
			return ItemInteractionResult.sidedSuccess(l.isClientSide);
		}
		// main nue : on reprend le fil (sinon le lingot)
		@Override
		protected InteractionResult useWithoutItem(BlockState s, Level l, BlockPos p, Player j, BlockHitResult h) {
			if (!l.isClientSide && l.getBlockEntity(p) instanceof LaminoirBlockEntity be) {
				ItemStack o = be.sortie.extractItem(0, 64, false);
				if (o.isEmpty()) o = be.entree.extractItem(0, 64, false);
				if (!o.isEmpty()) { j.getInventory().placeItemBackInInventory(o); l.playSound(null, p, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.4f, 1f); }
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}
		@Override
		public void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
			if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof LaminoirBlockEntity be) {
				Block.popResource(l, p, be.entree.getStackInSlot(0)); Block.popResource(l, p, be.sortie.getStackInSlot(0));
			}
			super.onRemove(s, l, p, n, deplace);
		}
	}

	public static class LaminoirBlockEntity extends KineticBlockEntity {
		public static final int TRAVAIL = 120;
		public final ItemStackHandler entree = new ItemStackHandler(1) {
			@Override protected void onContentsChanged(int s) { setChanged(); sendData(); }
			@Override public boolean isItemValid(int s, ItemStack st) { return accepte(st); }
		};
		public final ItemStackHandler sortie = new ItemStackHandler(1) { @Override protected void onContentsChanged(int s) { setChanged(); sendData(); } };
		public int progres;
		public LaminoirBlockEntity(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }
		static boolean accepte(ItemStack st) { return st.is(MetalAirain.LINGOT.get()); }
		@Override
		public void tick() {
			super.tick();
			if (level == null) return;
			float v = Math.abs(getSpeed());
			if (v == 0 || isOverStressed() || entree.getStackInSlot(0).isEmpty()) { if (progres > 0 && !level.isClientSide && level.getGameTime() % 10 == 0) { progres = 0; sendData(); } return; }
			ItemStack fil = new ItemStack(FIL.get(), 2);
			if (!sortie.insertItem(0, fil, true).isEmpty()) return;          // sortie pleine : il attend
			progres += Math.max(1, (int) (v / 16));
			if (level.isClientSide) {
				if (level.random.nextInt(6) == 0) level.addParticle(net.minecraft.core.particles.ParticleTypes.SMOKE, worldPosition.getX() + 0.5, worldPosition.getY() + 0.8, worldPosition.getZ() + 0.5, 0, 0.02, 0);
				return;
			}
			if (progres >= TRAVAIL) {
				progres = 0;
				entree.extractItem(0, 1, false);
				sortie.insertItem(0, fil, false);
				level.playSound(null, worldPosition, SoundEvents.CHAIN_PLACE, SoundSource.BLOCKS, 0.6f, 1.3f);
			}
		}
		/** Ce que voient entonnoirs et tapis : on verse les lingots, on reprend le fil. */
		public final net.neoforged.neoforge.items.IItemHandler acces = new net.neoforged.neoforge.items.IItemHandler() {
			@Override public int getSlots() { return 2; }
			@Override public ItemStack getStackInSlot(int s) { return s == 0 ? entree.getStackInSlot(0) : sortie.getStackInSlot(0); }
			@Override public ItemStack insertItem(int s, ItemStack st, boolean sim) { return s == 0 ? entree.insertItem(0, st, sim) : st; }
			@Override public ItemStack extractItem(int s, int n, boolean sim) { return s == 1 ? sortie.extractItem(0, n, sim) : ItemStack.EMPTY; }
			@Override public int getSlotLimit(int s) { return 64; }
			@Override public boolean isItemValid(int s, ItemStack st) { return s == 0 && accepte(st); }
		};
		@Override
		protected void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			t.put("entree", entree.serializeNBT(r)); t.put("sortie", sortie.serializeNBT(r)); t.putInt("progres", progres);
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			entree.deserializeNBT(r, t.getCompound("entree")); sortie.deserializeNBT(r, t.getCompound("sortie")); progres = t.getInt("progres");
		}
		@Override
		public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
			super.addToGoggleTooltip(t, accroupi);
			t.add(Component.literal("    ").append(Component.translatable("block.airain.airain_rolling_mill")).withStyle(ChatFormatting.GOLD));
			int n = entree.getStackInSlot(0).getCount(), f = sortie.getStackInSlot(0).getCount();
			t.add(Component.literal("    ").append(Component.translatable("airain.laminoir.etat", n, f)).withStyle(ChatFormatting.GRAY));
			if (n > 0 && getSpeed() != 0) t.add(Component.literal("    ").append(Component.translatable("airain.laminoir.progres", progres * 100 / TRAVAIL)).withStyle(ChatFormatting.DARK_GRAY));
			return true;
		}
	}

	// ====================================================================== enregistrement
	private static BlockBehaviour.Properties airain() {
		return BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).requiresCorrectToolForDrops().strength(3f, 6f).sound(SoundType.COPPER).noOcclusion();
	}
	public static final DeferredBlock<Gare> GARE = AirainMod.BLOCKS.register("airain_cable_station", () -> new Gare(airain().strength(4f, 8f)));
	public static final DeferredBlock<Pylone> PYLONE = AirainMod.BLOCKS.register("airain_pylon", () -> new Pylone(airain()));
	public static final DeferredBlock<TetePylone> TETE = AirainMod.BLOCKS.register("airain_pylon_head", () -> new TetePylone(airain()));
	public static final DeferredBlock<Laminoir> LAMINOIR = AirainMod.BLOCKS.register("airain_rolling_mill", () -> new Laminoir(airain()));
	public static final DeferredItem<Item> FIL = AirainMod.ITEMS.register("airain_wire", () -> new Item(new Item.Properties()));
	public static final DeferredItem<Cable> CABLE = AirainMod.ITEMS.register("airain_cable", () -> new Cable(new Item.Properties().stacksTo(16)));
	public static final DeferredItem<NacelleItem> NACELLE_ITEM = AirainMod.ITEMS.register("airain_gondola", () -> new NacelleItem(new Item.Properties().stacksTo(1)));
	static {
		AirainMod.ITEMS.register("airain_cable_station", () -> new BlockItem(GARE.get(), new Item.Properties()));
		AirainMod.ITEMS.register("airain_pylon", () -> new BlockItem(PYLONE.get(), new Item.Properties()));
		AirainMod.ITEMS.register("airain_pylon_head", () -> new BlockItem(TETE.get(), new Item.Properties()));
		AirainMod.ITEMS.register("airain_rolling_mill", () -> new BlockItem(LAMINOIR.get(), new Item.Properties()));
	}
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<GareBlockEntity>> GARE_BE = AirainMod.BLOCK_ENTITIES.register("airain_cable_station",
		() -> BlockEntityType.Builder.of((p, s) -> new GareBlockEntity(Telepherique.GARE_BE.get(), p, s), GARE.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TeteBlockEntity>> TETE_BE = AirainMod.BLOCK_ENTITIES.register("airain_pylon_head",
		() -> BlockEntityType.Builder.of((p, s) -> new TeteBlockEntity(Telepherique.TETE_BE.get(), p, s), TETE.get()).build(null));
	@SuppressWarnings("DataFlowIssue")
	public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<LaminoirBlockEntity>> LAMINOIR_BE = AirainMod.BLOCK_ENTITIES.register("airain_rolling_mill",
		() -> BlockEntityType.Builder.of((p, s) -> new LaminoirBlockEntity(Telepherique.LAMINOIR_BE.get(), p, s), LAMINOIR.get()).build(null));
	public static final DeferredHolder<EntityType<?>, EntityType<Nacelle>> NACELLE = AirainMod.ENTITES.register("airain_gondola",
		() -> EntityType.Builder.<Nacelle>of(Nacelle::new, MobCategory.MISC).sized(2.0f, 0.125f).clientTrackingRange(16).updateInterval(2).build("airain_gondola"));

	public static void charger() {}
}
