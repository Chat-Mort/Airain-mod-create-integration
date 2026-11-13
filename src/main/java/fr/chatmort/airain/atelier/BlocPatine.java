package fr.chatmort.airain.atelier;

import fr.chatmort.airain.fonderie.Passerelle;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.WeatheringCopper;
import net.minecraft.world.level.block.state.BlockState;

/** Base des pièces d'atelier qui se patinent comme l'airain (etat == null : version cirée). */
public abstract class BlocPatine extends Block implements Passerelle.Patinable {
	private final WeatheringCopper.WeatherState etat;
	protected BlocPatine(WeatheringCopper.WeatherState etat, Properties p) { super(p); this.etat = etat; }
	@Override public WeatheringCopper.WeatherState etat() { return etat; }
	@Override protected void randomTick(BlockState s, ServerLevel l, BlockPos p, RandomSource r) { if (etat != null) changeOverTime(s, l, p, r); }
	@Override protected boolean isRandomlyTicking(BlockState s) { return etat != null && WeatheringCopper.getNext(s.getBlock()).isPresent(); }
}
