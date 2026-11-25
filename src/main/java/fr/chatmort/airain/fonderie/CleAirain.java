package fr.chatmort.airain.fonderie;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import com.simibubi.create.AllTags;
import com.simibubi.create.content.equipment.wrench.IWrenchable;
import com.simibubi.create.content.equipment.wrench.WrenchItem;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.ChestType;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * 1.69.1 : la clé à molette d'airain, amélioration de la clé de Create. Elle garde tout ce que fait la clé de Create
 * (Create la reconnaît comme sa clé, voir CleCreateMixin) et, sur les blocs que Create ignore :
 * clic droit = tourner le bloc, clic droit accroupi = passer à la variante suivante (escalier, dalle, trappe, porte…).
 */
public final class CleAirain {
	private CleAirain() {}

	public static final DeferredItem<Item> CLE = AirainMod.ITEMS.register("airain_wrench", () -> new Cle(new Item.Properties().stacksTo(1)));

	public static void charger() {}

	public static boolean est(ItemStack s) { return s.is(CLE.get()); }

	public static class Cle extends WrenchItem {
		Cle(Properties p) { super(p); }

		// modèle ordinaire (celui de la clé de Create, retexturé) : pas le rendu animé de Create, qui dessinerait sa propre clé
		@Override
		public void initializeClient(Consumer<IClientItemExtensions> consumer) {}

		@Override
		public InteractionResult useOn(UseOnContext c) {
			Player p = c.getPlayer();
			Level l = c.getLevel();
			BlockPos pos = c.getClickedPos();
			BlockState s = l.getBlockState(pos);
			// ce que la clé de Create sait faire reste à Create (blocs de Create, rails et autres blocs à ramasser accroupi)
			if (p == null || !p.mayBuild() || s.getBlock() instanceof IWrenchable
				|| (p.isShiftKeyDown() && AllTags.AllBlockTags.WRENCH_PICKUP.matches(s)))
				return super.useOn(c);
			// 1.69.5 : murets, barrières, vitres et barreaux : accroupi, on relie ou délie le côté visé
			if (p.isShiftKeyDown() && (s.getBlock() instanceof net.minecraft.world.level.block.WallBlock || s.getBlock() instanceof net.minecraft.world.level.block.CrossCollisionBlock)) {
				Direction d = c.getClickedFace();
				if (d.getAxis().isVertical()) {      // clic dessus ou dessous : le côté le plus proche du point visé
					net.minecraft.world.phys.Vec3 v = c.getClickLocation().subtract(net.minecraft.world.phys.Vec3.atCenterOf(pos));
					d = Math.abs(v.x) > Math.abs(v.z) ? (v.x > 0 ? Direction.EAST : Direction.WEST) : (v.z > 0 ? Direction.SOUTH : Direction.NORTH);
				}
				BlockState m = lien(s, d);
				if (!l.isClientSide) {
					l.setBlock(pos, m, Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE);
					l.playSound(null, pos, SoundEvents.ITEM_FRAME_ROTATE_ITEM, SoundSource.BLOCKS, 0.8f, 0.8f + l.random.nextFloat() * 0.2f);
					p.displayClientMessage(s.getBlock().getName().copy().append(": ").append(Component.translatable(relie(m, d) ? "airain.cle.lie" : "airain.cle.delie",
						Component.translatable("airain.loupe.dir." + d.getName().charAt(0)))), true);
				}
				return InteractionResult.sidedSuccess(l.isClientSide);
			}
			BlockState n = p.isShiftKeyDown() ? variante(s) : tourner(s);
			if (n == null || n == s) return super.useOn(c);
			if (!n.canSurvive(l, pos)) return InteractionResult.FAIL;
			if (!l.isClientSide) {
				// 2 | 16 : sans recalculer la forme d'après les voisins (sinon l'escalier reprendrait aussitôt son angle automatique)
				l.setBlock(pos, n, Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE);
				if (s.hasProperty(BlockStateProperties.DOOR_HINGE) && s.hasProperty(BlockStateProperties.DOUBLE_BLOCK_HALF)) {
					BlockPos autre = s.getValue(BlockStateProperties.DOUBLE_BLOCK_HALF) == DoubleBlockHalf.LOWER ? pos.above() : pos.below();
					BlockState a = l.getBlockState(autre);
					if (a.is(s.getBlock())) l.setBlock(autre, a.setValue(BlockStateProperties.DOOR_HINGE, n.getValue(BlockStateProperties.DOOR_HINGE)), Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE);
				}
				l.playSound(null, pos, SoundEvents.ITEM_FRAME_ROTATE_ITEM, SoundSource.BLOCKS, 0.8f, 0.8f + l.random.nextFloat() * 0.2f);
				p.displayClientMessage(decrire(n, p.isShiftKeyDown()), true);
			}
			return InteractionResult.sidedSuccess(l.isClientSide);
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
			l.add(Component.translatable("airain.cle.aide_create").withStyle(net.minecraft.ChatFormatting.GRAY));
			l.add(Component.translatable("airain.cle.aide_tourner").withStyle(net.minecraft.ChatFormatting.GRAY));
			l.add(Component.translatable("airain.cle.aide_variante").withStyle(net.minecraft.ChatFormatting.GRAY));
		}
	}

	// ------------------------------------------------------------------ tourner
	/** Le bloc tourné d'un cran, ou null si on ne doit pas y toucher (porte, lit, double coffre, piston sorti…). */
	static BlockState tourner(BlockState s) {
		if (s.hasProperty(BlockStateProperties.DOUBLE_BLOCK_HALF) || s.hasProperty(BlockStateProperties.BED_PART)
			|| (s.hasProperty(BlockStateProperties.CHEST_TYPE) && s.getValue(BlockStateProperties.CHEST_TYPE) != ChestType.SINGLE)
			|| (s.hasProperty(BlockStateProperties.EXTENDED) && s.getValue(BlockStateProperties.EXTENDED))) return null;
		if (s.hasProperty(BlockStateProperties.AXIS)) {                                    // bûches, piliers, chaînes : debout, puis couchés
			Direction.Axis a = s.getValue(BlockStateProperties.AXIS);
			return s.setValue(BlockStateProperties.AXIS, a == Direction.Axis.Y ? Direction.Axis.X : a == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.Y);
		}
		if (s.hasProperty(BlockStateProperties.FACING)) {                                  // six faces
			Direction[] ordre = {Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST, Direction.UP, Direction.DOWN};
			Direction d = s.getValue(BlockStateProperties.FACING);
			for (int i = 0; i < ordre.length; i++) if (ordre[i] == d) return s.setValue(BlockStateProperties.FACING, ordre[(i + 1) % ordre.length]);
		}
		if (s.hasProperty(BlockStateProperties.HORIZONTAL_FACING))
			return s.setValue(BlockStateProperties.HORIZONTAL_FACING, s.getValue(BlockStateProperties.HORIZONTAL_FACING).getClockWise());
		if (s.hasProperty(BlockStateProperties.ROTATION_16))                               // panneaux, têtes : un seizième de tour
			return s.setValue(BlockStateProperties.ROTATION_16, (s.getValue(BlockStateProperties.ROTATION_16) + 1) % 16);
		BlockState r = s.rotate(Rotation.CLOCKWISE_90);
		return r == s ? null : r;
	}

	// ------------------------------------------------------------------ variantes
	/** Les propriétés de forme qu'on fait défiler (jamais la quantité de matière : une dalle double reste double). */
	private static final List<Property<?>> FORMES = List.of(BlockStateProperties.STAIRS_SHAPE, BlockStateProperties.HALF, BlockStateProperties.SLAB_TYPE,
		BlockStateProperties.DOOR_HINGE, BlockStateProperties.ATTACH_FACE);

	static BlockState variante(BlockState s) {
		List<Property<?>> l = new ArrayList<>();
		for (Property<?> p : FORMES) if (s.hasProperty(p)) l.add(p);
		if (l.isEmpty() || (s.hasProperty(BlockStateProperties.SLAB_TYPE) && s.getValue(BlockStateProperties.SLAB_TYPE) == SlabType.DOUBLE)) return null;
		// compteur : on avance la première propriété, et la suivante quand la première a fait le tour
		BlockState n = s;
		for (Property<?> p : l) {
			BlockState suivant = suivante(n, p);
			boolean tour = premiere(n, p);
			n = suivant;
			if (!tour) break;
		}
		return n;
	}
	/** Valeur suivante de la propriété (la dalle ne passe qu'entre haut et bas). */
	private static <T extends Comparable<T>> BlockState suivante(BlockState s, Property<T> p) {
		if (p == BlockStateProperties.SLAB_TYPE) return s.setValue(BlockStateProperties.SLAB_TYPE, s.getValue(BlockStateProperties.SLAB_TYPE) == SlabType.TOP ? SlabType.BOTTOM : SlabType.TOP);
		List<T> v = new ArrayList<>(p.getPossibleValues());
		return s.setValue(p, v.get((v.indexOf(s.getValue(p)) + 1) % v.size()));
	}
	/** La propriété est-elle sur sa dernière valeur (le prochain cran la ramène à la première et fait avancer la suivante) ? */
	private static <T extends Comparable<T>> boolean premiere(BlockState s, Property<T> p) {
		if (p == BlockStateProperties.SLAB_TYPE) return s.getValue(BlockStateProperties.SLAB_TYPE) == SlabType.TOP;
		List<T> v = new ArrayList<>(p.getPossibleValues());
		return v.indexOf(s.getValue(p)) == v.size() - 1;
	}

	// ------------------------------------------------------------------ 1.69.5 : liaisons des murets et des barrières
	private static net.minecraft.world.level.block.state.properties.EnumProperty<net.minecraft.world.level.block.state.properties.WallSide> cote(Direction d) {
		return switch (d) {
			case NORTH -> BlockStateProperties.NORTH_WALL; case SOUTH -> BlockStateProperties.SOUTH_WALL;
			case EAST -> BlockStateProperties.EAST_WALL; default -> BlockStateProperties.WEST_WALL;
		};
	}
	private static boolean relie(BlockState s, Direction d) {
		if (s.getBlock() instanceof net.minecraft.world.level.block.WallBlock) return s.getValue(cote(d)) != net.minecraft.world.level.block.state.properties.WallSide.NONE;
		return s.getValue(net.minecraft.world.level.block.PipeBlock.PROPERTY_BY_DIRECTION.get(d));
	}
	private static BlockState lien(BlockState s, Direction d) {
		if (!(s.getBlock() instanceof net.minecraft.world.level.block.WallBlock))
			return s.setValue(net.minecraft.world.level.block.PipeBlock.PROPERTY_BY_DIRECTION.get(d), !relie(s, d));
		var aucun = net.minecraft.world.level.block.state.properties.WallSide.NONE;
		BlockState n = s.setValue(cote(d), relie(s, d) ? aucun : net.minecraft.world.level.block.state.properties.WallSide.LOW);
		// poteau central comme en vanilla : absent seulement quand le muret file droit (deux côtés opposés, rien d'autre)
		boolean no = n.getValue(cote(Direction.NORTH)) != aucun, so = n.getValue(cote(Direction.SOUTH)) != aucun;
		boolean es = n.getValue(cote(Direction.EAST)) != aucun, ou = n.getValue(cote(Direction.WEST)) != aucun;
		boolean droit = (no && so && !es && !ou) || (es && ou && !no && !so);
		return n.setValue(BlockStateProperties.UP, !droit);
	}

	// ------------------------------------------------------------------ message
	private static Component decrire(BlockState s, boolean variante) {
		MutableComponent m = s.getBlock().getName().copy().append(": ");
		List<Component> parts = new ArrayList<>();
		if (variante) {
			for (Property<?> p : FORMES) if (s.hasProperty(p)) parts.add(Component.translatable("airain.cle." + p.getName() + "." + nom(s, p)));
		} else {
			if (s.hasProperty(BlockStateProperties.AXIS)) parts.add(Component.translatable("airain.cle.axis." + nom(s, BlockStateProperties.AXIS)));
			else if (s.hasProperty(BlockStateProperties.FACING)) parts.add(Component.translatable("airain.cle.facing." + nom(s, BlockStateProperties.FACING)));
			else if (s.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) parts.add(Component.translatable("airain.cle.facing." + nom(s, BlockStateProperties.HORIZONTAL_FACING)));
			else if (s.hasProperty(BlockStateProperties.ROTATION_16)) parts.add(Component.translatable("airain.cle.rotation", s.getValue(BlockStateProperties.ROTATION_16)));
			else parts.add(Component.translatable("airain.cle.tourne"));
		}
		for (int i = 0; i < parts.size(); i++) { if (i > 0) m.append(", "); m.append(parts.get(i)); }
		return m;
	}
	private static <T extends Comparable<T>> String nom(BlockState s, Property<T> p) { return p.getName(s.getValue(p)); }
}
