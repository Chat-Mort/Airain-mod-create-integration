package fr.chatmort.airain.fonderie;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.ChainBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.WeatheringCopper;
import net.minecraft.world.level.block.state.BlockState;
import org.joml.Vector3f;

/**
 * Les blocs d'airain qui n'ont pas d'équivalent « cuivre » dans Minecraft (pilier, barreaux, chaîne, lanterne).
 * Chacun existe en version qui se patine (implémente WeatheringCopper : même mécanique que le cuivre, le stade suivant
 * est donné par la data map neoforge:oxidizables) et en version cirée (la classe de base, qui ne change plus).
 */
public final class Patine {
	private Patine() {}

	// ---- pilier
	public static class Pilier extends RotatedPillarBlock implements WeatheringCopper {
		private final WeatherState etat;
		public Pilier(WeatherState etat, Properties p) { super(p); this.etat = etat; }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		@Override public WeatherState getAge() { return etat; }
	}

	// ---- barreaux
	public static class Barreaux extends IronBarsBlock implements WeatheringCopper {
		private final WeatherState etat;
		public Barreaux(WeatherState etat, Properties p) { super(p); this.etat = etat; }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		@Override public WeatherState getAge() { return etat; }
	}
	public static class BarreauxCires extends IronBarsBlock { public BarreauxCires(Properties p) { super(p); } }

	// ---- grille cirée (le constructeur de la classe de Minecraft n'est pas public)
	public static class GrilleCiree extends net.minecraft.world.level.block.WaterloggedTransparentBlock { public GrilleCiree(Properties p) { super(p); } }

	// ---- chaîne
	public static class Chaine extends ChainBlock implements WeatheringCopper {
		private final WeatherState etat;
		public Chaine(WeatherState etat, Properties p) { super(p); this.etat = etat; }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		@Override public WeatherState getAge() { return etat; }
	}

	// ---- lanterne : flamme rouge, petites étincelles rouges (Minecraft ne colore pas la lumière elle-même)
	public static class Lanterne extends LanternBlock {
		private static final DustParticleOptions ETINCELLE = new DustParticleOptions(new Vector3f(1f, 0.22f, 0.12f), 0.6f);
		public Lanterne(Properties p) { super(p); }
		@Override
		public void animateTick(BlockState s, Level l, BlockPos p, RandomSource r) {
			if (r.nextInt(3) != 0) return;
			double y = p.getY() + (s.getValue(HANGING) ? 0.45 : 0.35);
			l.addParticle(ETINCELLE, p.getX() + 0.5 + (r.nextDouble() - 0.5) * 0.2, y, p.getZ() + 0.5 + (r.nextDouble() - 0.5) * 0.2, 0, 0.02, 0);
		}
	}
	public static class LanternePatinable extends Lanterne implements WeatheringCopper {
		private final WeatherState etat;
		public LanternePatinable(WeatherState etat, Properties p) { super(p); this.etat = etat; }
		@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { changeOverTime(s, l, p, r); }
		@Override protected boolean isRandomlyTicking(BlockState s) { return WeatheringCopper.getNext(s.getBlock()).isPresent(); }
		@Override public WeatherState getAge() { return etat; }
	}
}
