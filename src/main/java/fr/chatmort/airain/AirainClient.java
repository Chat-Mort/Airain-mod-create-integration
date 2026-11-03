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
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(net.neoforged.bus.api.EventPriority.LOWEST, fr.chatmort.airain.armure.TourbillonClient::avant);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.armure.TourbillonClient::apres);
		net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(fr.chatmort.airain.gardien.Loupe::champ);
		bus.addListener((EntityRenderersEvent.RegisterLayerDefinitions e) ->
			{ e.registerLayerDefinition(fr.chatmort.airain.gardien.CouronneModele.COUCHE, fr.chatmort.airain.gardien.CouronneModele::creer);
			  e.registerLayerDefinition(fr.chatmort.airain.gardien.CouronneModele.COUCHE_CASQUE, fr.chatmort.airain.gardien.CouronneModele::creerCasque);
			  e.registerLayerDefinition(fr.chatmort.airain.gardien.ModulesCouche.COUCHE, fr.chatmort.airain.gardien.ModulesCouche::creer);
			  e.registerLayerDefinition(fr.chatmort.airain.gardien.EliteCouche.COUCHE, fr.chatmort.airain.gardien.EliteCouche::creer);
			  e.registerLayerDefinition(fr.chatmort.airain.armure.DiademeModele.COUCHE, fr.chatmort.airain.armure.DiademeModele::creer);
			  for (int i = 0; i < 3; i++) { final int k = i; e.registerLayerDefinition(fr.chatmort.airain.armure.CoiffesModele.COUCHES[k], () -> fr.chatmort.airain.armure.CoiffesModele.creer(k)); }
			  e.registerLayerDefinition(fr.chatmort.airain.armure.CoiffesModele.HALO, fr.chatmort.airain.armure.CoiffesModele::creerHalo);
			  for (int i = 0; i < 4; i++) { final int k = i; e.registerLayerDefinition(fr.chatmort.airain.armure.ArcaniqueModele.COUCHES[k], () -> fr.chatmort.airain.armure.ArcaniqueModele.creer(k)); }
			  for (int i = 0; i < 4; i++) { final int k = i; e.registerLayerDefinition(fr.chatmort.airain.armure.ImperialeModele.COUCHES[k], () -> fr.chatmort.airain.armure.ImperialeModele.creer(k)); } });
		bus.addListener((net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent e) ->
			{ e.registerItem(fr.chatmort.airain.gardien.CouronneModele.EXTENSION, AirainMod.COURONNE.get());
			  e.registerItem(fr.chatmort.airain.gardien.CouronneModele.EXTENSION_CASQUE, AirainMod.CASQUE_COURONNE.get(), AirainMod.CASQUE_COURONNE_SACREE.get());
			  e.registerItem(fr.chatmort.airain.armure.ImperialeModele.extension(0), AirainMod.CASQUE_IMPERIAL.get());
			  e.registerItem(fr.chatmort.airain.armure.DiademeModele.EXTENSION, AirainMod.DIADEME.get());
			  e.registerItem(fr.chatmort.airain.armure.CoiffesModele.extension(0), AirainMod.CASQUE_DIADEME.get());
			  e.registerItem(fr.chatmort.airain.armure.TourbillonClient.MAIN, AirainMod.TWINBLADE_IMPERIALE.get(), AirainMod.TWINBLADE_ARCANIQUE.get());
			  e.registerItem(fr.chatmort.airain.armure.CoiffesModele.extension(1), AirainMod.CASQUE_RUNIQUE.get());
			  e.registerItem(fr.chatmort.airain.armure.CoiffesModele.extension(2), AirainMod.CASQUE_ARCANIQUE.get());
			  e.registerItem(fr.chatmort.airain.armure.ArcaniqueModele.extension(1), AirainMod.PLASTRON_ARCANIQUE.get());
			  e.registerItem(fr.chatmort.airain.armure.ArcaniqueModele.extension(2), AirainMod.JAMBIERES_ARCANIQUES.get());
			  e.registerItem(fr.chatmort.airain.armure.ArcaniqueModele.extension(3), AirainMod.BOTTES_ARCANIQUES.get());
			  e.registerItem(fr.chatmort.airain.armure.ImperialeModele.extension(1), AirainMod.PLASTRON_IMPERIAL.get());
			  e.registerItem(fr.chatmort.airain.armure.ImperialeModele.extension(2), AirainMod.JAMBIERES_IMPERIALES.get());
			  e.registerItem(fr.chatmort.airain.armure.ImperialeModele.extension(3), AirainMod.BOTTES_IMPERIALES.get()); });
		bus.addListener((EntityRenderersEvent.AddLayers e) -> {
			for (var m : e.getSkins())
				if (e.getSkin(m) instanceof net.minecraft.client.renderer.entity.player.PlayerRenderer r)
					r.addLayer(new fr.chatmort.airain.armure.CoiffesHalo(r, e.getEntityModels()));
		});
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
		event.registerEntityRenderer(AirainMod.ASSISE.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
	}

	private void setup(FMLClientSetupEvent event) {
		// couronne et casque couronné sacrés : icône noire et or
		event.enqueueWork(() -> {
			var prop = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "sacree");
			for (var it : new net.minecraft.world.item.Item[] {AirainMod.COURONNE.get(), AirainMod.CASQUE_COURONNE.get()})
				net.minecraft.client.renderer.item.ItemProperties.register(it, prop, (s, l, e, n) -> fr.chatmort.airain.Sacre.sacree(s) ? 1f : 0f);
		});
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
