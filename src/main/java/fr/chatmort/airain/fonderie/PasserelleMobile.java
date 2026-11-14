package fr.chatmort.airain.fonderie;

import com.simibubi.create.content.kinetics.base.IRotate;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.WeatheringCopper.WeatherState;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;

import java.util.List;

/**
 * Pièce-mécanisme de passerelle mobile : une passerelle ordinaire (on marche dessus, rambardes, portillons) avec un carter
 * suspendu dessous. Elle entraîne les 1 à 4 passerelles ordinaires qui la suivent dans son sens (rangé dans le bloc-entité) :
 * pont-levis (elles se relèvent autour de son bord) ou passerelle rétractable (elles rentrent en télescope dans le carter).
 * Commandes : un arbre de Create par-dessous (un sens déploie, l'autre relève ; la vitesse règle le mouvement),
 * ou la redstone quand l'arbre est à l'arrêt (signal : relevé / rentré).
 * Segments relevés ou rentrés : invisibles et sans collision ; les rambardes de bout se remettent seules des deux côtés.
 */
public class PasserelleMobile extends Passerelle.Plancher implements EntityBlock, IRotate {
	public final boolean pontLevis;

	// 1.55.3 : le sens et la longueur sont rangés dans le bloc-entité, plus dans l'état du bloc
	// (16 combinaisons de plus par état : des millions d'états en mémoire).
	public PasserelleMobile(WeatherState etat, Properties p, boolean pontLevis) {
		super(etat, p);
		this.pontLevis = pontLevis;
	}
	// posée en regardant vers le vide à franchir
	@Override
	public void setPlacedBy(Level l, BlockPos p, BlockState s, @javax.annotation.Nullable net.minecraft.world.entity.LivingEntity qui, net.minecraft.world.item.ItemStack st) {
		super.setPlacedBy(l, p, s, qui, st);
		if (qui != null && l.getBlockEntity(p) instanceof Mecanisme m) m.orienter(qui.getDirection());
	}

	// ---------------------------------------------------------------- Create : l'arbre entre par le dessous du carter
	@Override public boolean hasShaftTowards(LevelReader l, BlockPos p, BlockState s, Direction d) { return d == Direction.DOWN; }
	@Override public Direction.Axis getRotationAxis(BlockState s) { return Direction.Axis.Y; }
	// comme les blocs de Create : un changement d'état sans effet sur la rotation ne relance pas la propagation
	@Override
	protected void onPlace(BlockState s, Level l, BlockPos p, BlockState ancien, boolean deplace) {
		super.onPlace(s, l, p, ancien, deplace);
		if (l.getBlockEntity(p) instanceof KineticBlockEntity k) {
			k.preventSpeedUpdate = 0;
			if (ancien.getBlock() == s.getBlock()) k.preventSpeedUpdate = 2;
		}
	}
	@Override
	protected void updateIndirectNeighbourShapes(BlockState s, LevelAccessor l, BlockPos p, int flags, int count) {
		if (l.isClientSide() || !(l.getBlockEntity(p) instanceof KineticBlockEntity k) || k.preventSpeedUpdate > 0) return;
		k.warnOfMovement(); k.clearKineticInformation(); k.updateSpeed = true;
	}
	@Override
	protected void onRemove(BlockState s, Level l, BlockPos p, BlockState n, boolean deplace) {
		if (!s.is(n.getBlock()) && l.getBlockEntity(p) instanceof Mecanisme m) m.liberer(4);
		super.onRemove(s, l, p, n, deplace);
	}

	// clé sur le sol (au milieu) : longueur entraînée 1 → 2 → 3 → 4 ; sur un bord : rambarde comme une passerelle
	@Override
	public InteractionResult onWrenched(BlockState s, UseOnContext c) {
		Level l = c.getLevel(); BlockPos p = c.getClickedPos();
		double x = c.getClickLocation().x - p.getX(), z = c.getClickLocation().z - p.getZ();
		if (c.getClickedFace().getAxis() == Direction.Axis.Y && Math.min(Math.min(x, 1 - x), Math.min(z, 1 - z)) > 0.2) {
			if (!l.isClientSide && l.getBlockEntity(p) instanceof Mecanisme m) {
				m.liberer(4);
				int n = m.longueur() % 4 + 1;
				m.longueur = n; m.setChanged();
				m.resynchroniser();
				l.playSound(null, p, SoundEvents.COPPER_HIT, SoundSource.BLOCKS, 1f, 0.7f + 0.15f * n);
				if (c.getPlayer() != null) c.getPlayer().displayClientMessage(Component.translatable("airain.mobile.longueur", n).withStyle(ChatFormatting.GOLD), true);
			}
			return InteractionResult.SUCCESS;
		}
		return super.onWrenched(s, c);
	}

	@Override public BlockEntity newBlockEntity(BlockPos p, BlockState s) { return new Mecanisme(Passerelles.MOBILE_BE.get(), p, s); }
	@Override
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l, BlockState s, BlockEntityType<T> t) {
		return t == Passerelles.MOBILE_BE.get() ? (lv, p, st, be) -> ((Mecanisme) be).tick() : null;
	}

	// ====================================================================== le bloc-entité : avancement du mouvement
	public static class Mecanisme extends KineticBlockEntity {
		/** 1 = déployé (segments en place), 0 = relevé / rentré. */
		public float avance = 1, avanceAvant = 1;
		private int cible = 1;
		private boolean signal, fantome, pret;
		private Direction sens = Direction.NORTH;
		int longueur = 3;

		public Mecanisme(BlockEntityType<?> t, BlockPos p, BlockState s) { super(t, p, s); }

		public Direction sens() { return sens; }
		public int longueur() { return longueur; }
		/** Sens donné à la pose (vers le vide à franchir). */
		public void orienter(Direction d) {
			if (!d.getAxis().isHorizontal() || d == sens) return;
			liberer(4); sens = d; setChanged(); sendData();
		}
		public boolean pontLevis() { return getBlockState().getBlock() instanceof PasserelleMobile m && m.pontLevis; }
		/** Le segment i (1 à n) est-il une passerelle ordinaire au même niveau que le mécanisme ? */
		public boolean segment(int i) {
			if (level == null) return false;
			BlockState s = level.getBlockState(worldPosition.relative(sens(), i));
			return s.getBlock() instanceof Passerelle.Plancher && !(s.getBlock() instanceof PasserelleMobile)
				&& s.getValue(Passerelle.HAUT) == getBlockState().getValue(Passerelle.HAUT);
		}
		private void marquer(int n, boolean rentre) {
			for (int i = 1; i <= n; i++) {
				if (!segment(i)) break;
				BlockPos q = worldPosition.relative(sens(), i);
				BlockState s = level.getBlockState(q);
				if (s.getValue(Passerelle.RENTRE) == rentre) continue;
				BlockState ns = s.setValue(Passerelle.RENTRE, rentre);
				// segment qui revient : ses côtés sont recalculés (ses voisins le sont par la mise à jour du bloc)
				if (!rentre) ns = Passerelle.Plancher.recoter(ns, level, q);
				level.setBlock(q, ns, Block.UPDATE_ALL);
			}
		}
		/** Remet en place les segments (mécanisme cassé, longueur changée). */
		void liberer(int n) { if (level != null && !level.isClientSide) marquer(n, false); fantome = false; }
		void resynchroniser() { if (avance < 1) { marquer(longueur(), true); fantome = true; } sendData(); }

		@Override
		public void tick() {
			super.tick();
			if (level == null) return;
			float v = getSpeed();
			if (!level.isClientSide && !pret) {                     // au chargement : les segments suivent l'état sauvegardé
				pret = true; fantome = avance < 1; marquer(longueur(), fantome);
			}
			if (!level.isClientSide) {
				boolean sg = level.hasNeighborSignal(worldPosition);
				int c = cible;
				if (v != 0) c = v > 0 ? 1 : 0;                         // l'arbre décide quand il tourne
				else if (sg != signal) c = sg ? 0 : 1;                  // sinon la redstone (à chaque changement)
				signal = sg;
				if (c != cible) { cible = c; sendData(); }
			}
			float pas = v != 0 ? 0.01f + Math.abs(v) / 256f * 0.06f : 0.035f;
			avanceAvant = avance;
			if (avance < cible) avance = Math.min(cible, avance + pas);
			else if (avance > cible) avance = Math.max(cible, avance - pas);
			if (!level.isClientSide) {
				if (avance < 1 && !fantome) { marquer(longueur(), true); fantome = true; son(false); }
				if (avance >= 1 && fantome) { marquer(longueur(), false); fantome = false; son(true); }
			}
		}
		private void son(boolean fin) {
			level.playSound(null, worldPosition, fin ? SoundEvents.IRON_DOOR_CLOSE : SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 0.8f, 0.6f);
		}

		@Override
		public void write(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.write(t, r, client);
			t.putFloat("avance", avance); t.putInt("cible", cible); t.putBoolean("signal", signal); t.putBoolean("fantome", fantome);
			t.putInt("sens", sens.get2DDataValue()); t.putInt("longueur", longueur);
		}
		@Override
		protected void read(CompoundTag t, HolderLookup.Provider r, boolean client) {
			super.read(t, r, client);
			cible = t.getInt("cible"); signal = t.getBoolean("signal");
			if (t.contains("sens")) sens = Direction.from2DDataValue(t.getInt("sens"));
			if (t.contains("longueur")) longueur = Math.max(1, Math.min(4, t.getInt("longueur")));
			if (!client) { avance = t.contains("avance") ? t.getFloat("avance") : 1; fantome = t.getBoolean("fantome"); }
			else if (!t.contains("avance")) avance = 1;
			else if (Math.abs(t.getFloat("avance") - avance) > 0.5f) avance = t.getFloat("avance");
		}
		@Override
		public AABB getRenderBoundingBox() { return new AABB(worldPosition).inflate(5.5); }

		@Override
		public boolean addToGoggleTooltip(List<Component> t, boolean accroupi) {
			super.addToGoggleTooltip(t, accroupi);
			t.add(Component.literal("    ").append(Component.translatable(pontLevis() ? "block.airain.airain_catwalk_drawbridge" : "block.airain.airain_catwalk_telescopic")).withStyle(ChatFormatting.GOLD));
			t.add(Component.literal("    ").append(Component.translatable("airain.mobile.longueur", longueur())).withStyle(ChatFormatting.GRAY));
			String e = avance >= 1 ? "deploye" : avance <= 0 ? (pontLevis() ? "releve" : "rentre") : "mouvement";
			t.add(Component.literal("    ").append(Component.translatable("airain.mobile." + e)).withStyle(ChatFormatting.GRAY));
			return true;
		}
	}
}
