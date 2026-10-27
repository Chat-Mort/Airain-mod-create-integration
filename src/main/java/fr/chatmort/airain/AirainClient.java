package fr.chatmort.airain;

import com.simibubi.create.content.kinetics.base.SingleAxisRotatingVisual;

import dev.engine_room.flywheel.lib.visualization.SimpleBlockEntityVisualizer;
import fr.chatmort.airain.banc.BancEntretienRenderer;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@Mod(value = AirainMod.ID, dist = Dist.CLIENT)
public class AirainClient {
	public AirainClient(IEventBus bus) {
		bus.addListener(this::rendus);
		bus.addListener(this::setup);
	}

	private void rendus(EntityRenderersEvent.RegisterRenderers event) {
		event.registerBlockEntityRenderer(AirainMod.BANC_BE.get(), BancEntretienRenderer::new);
	}

	private void setup(FMLClientSetupEvent event) {
		// Avec Flywheel, l'arbre est dessiné par une instance ; le rendu classique reste actif pour les objets posés dessus.
		SimpleBlockEntityVisualizer.builder(AirainMod.BANC_BE.get())
			.factory(SingleAxisRotatingVisual::shaft)
			.skipVanillaRender(be -> false)
			.apply();
	}
}
