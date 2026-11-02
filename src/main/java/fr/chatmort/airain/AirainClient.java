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
		bus.addListener(fr.chatmort.airain.gardien.Loupe::touches);
		bus.addListener(fr.chatmort.airain.reliure.LectureClient::touches);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.reliure.LectureClient::tick);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.reliure.Onglets::rendu);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.reliure.Onglets::clic);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Loupe::tick);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Loupe::champ);
		bus.addListener((EntityRenderersEvent.RegisterLayerDefinitions e) ->
			{ e.registerLayerDefinition(fr.chatmort.airain.gardien.CouronneModele.COUCHE, fr.chatmort.airain.gardien.CouronneModele::creer);
			  e.registerLayerDefinition(fr.chatmort.airain.gardien.CouronneModele.COUCHE_CASQUE, fr.chatmort.airain.gardien.CouronneModele::creerCasque); });
		bus.addListener((net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent e) ->
			{ e.registerItem(fr.chatmort.airain.gardien.CouronneModele.EXTENSION, AirainMod.COURONNE.get());
			  e.registerItem(fr.chatmort.airain.gardien.CouronneModele.EXTENSION_CASQUE, AirainMod.CASQUE_COURONNE.get()); });
		bus.addListener((net.neoforged.neoforge.client.event.RegisterGuiLayersEvent e) -> e.registerAboveAll(
			net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(AirainMod.ID, "fondation"), fr.chatmort.airain.fondation.HudFondation::rendre));
		bus.addListener((net.neoforged.neoforge.client.event.RegisterGuiLayersEvent e) -> e.registerAboveAll(
			net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(AirainMod.ID, "socle"), fr.chatmort.airain.trophee.HudSocle::rendre));
	}

	private void rendus(EntityRenderersEvent.RegisterRenderers event) {
		event.registerBlockEntityRenderer(AirainMod.BANC_BE.get(), BancEntretienRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.DESENCH_BE.get(), DesenchanteurRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.TABLE_BE.get(), fr.chatmort.airain.enchant.TableEmpireRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.SOCLE_BE.get(), fr.chatmort.airain.trophee.SocleRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.FONDATION_BE.get(), fr.chatmort.airain.fondation.EtendardRenderer::new);
		event.registerBlockEntityRenderer(AirainMod.BALISE_BE.get(), fr.chatmort.airain.balise.BaliseRenderer::new);
		event.registerEntityRenderer(AirainMod.GARDIEN.get(), fr.chatmort.airain.gardien.GardienRenderer::new);
	}

	private void setup(FMLClientSetupEvent event) {
		// Gardien des Cieux : rendu translucide pour que la lumière traverse les vitraux de ses ailes
		event.enqueueWork(() -> net.minecraft.client.renderer.entity.EnderDragonRenderer.RENDER_TYPE =
			net.minecraft.client.renderer.RenderType.entityTranslucent(
				net.minecraft.resources.ResourceLocation.withDefaultNamespace("textures/entity/enderdragon/dragon.png")));
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
		event.register(AirainMod.BANC_MENU.get(), fr.chatmort.airain.banc.BancScreen::new);
		event.register(AirainMod.RELIURE_MENU.get(), fr.chatmort.airain.reliure.ReliureMenuScreen::new);
	}
}
