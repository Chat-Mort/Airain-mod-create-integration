package fr.chatmort.airain;

import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.SingleAxisRotatingVisual;

import dev.engine_room.flywheel.lib.visualization.SimpleBlockEntityVisualizer;
import fr.chatmort.airain.banc.BancEntretienRenderer;
import fr.chatmort.airain.enchant.DesenchanteurRenderer;
import fr.chatmort.airain.enchant.TableEmpireScreen;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@Mod(value = AirainMod.ID, dist = Dist.CLIENT)
public class AirainClient {
	public AirainClient(IEventBus bus) {
		AirainPartials.init();
		bus.addListener(this::rendus);
		bus.addListener(this::setup);
		bus.addListener(this::ecrans);
	}

	private void rendus(EntityRenderersEvent.RegisterRenderers event) {
		event.registerBlockEntityRenderer(AirainMod.BANC_BE.get(), BancEntretienRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.DESENCH_BE.get(), DesenchanteurRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.TABLE_BE.get(), fr.chatmort.airain.enchant.TableEmpireRenderer::new);
	}

	private void setup(FMLClientSetupEvent event) {
		// Avec Flywheel, le rouage (celui de la meule de Create) est une instance ;
		// le rendu classique reste actif pour la meule en pierre, la jauge et les objets.
		SimpleBlockEntityVisualizer.builder(AirainMod.BANC_BE.get())
			.factory(SingleAxisRotatingVisual.of(AllPartialModels.MILLSTONE_COG))
			.skipVanillaRender(be -> false)
			.apply();
		SimpleBlockEntityVisualizer.builder(AirainMod.DESENCH_BE.get())
			.factory(SingleAxisRotatingVisual.of(AllPartialModels.MILLSTONE_COG))
			.skipVanillaRender(be -> false)
			.apply();
	}

	private void ecrans(RegisterMenuScreensEvent event) {
		event.register(AirainMod.TABLE_MENU.get(), TableEmpireScreen::new);
	}
}
