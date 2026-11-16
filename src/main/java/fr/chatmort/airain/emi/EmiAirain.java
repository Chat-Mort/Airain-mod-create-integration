package fr.chatmort.airain.emi;

import dev.emi.emi.api.EmiEntrypoint;
import dev.emi.emi.api.EmiPlugin;
import dev.emi.emi.api.EmiRegistry;
import dev.emi.emi.api.recipe.BasicEmiRecipe;
import dev.emi.emi.api.recipe.EmiRecipeCategory;
import dev.emi.emi.api.render.EmiTexture;
import dev.emi.emi.api.stack.EmiIngredient;
import dev.emi.emi.api.stack.EmiStack;
import dev.emi.emi.api.widget.WidgetHolder;
import fr.chatmort.airain.fonderie.MetalAirain;
import fr.chatmort.airain.fonderie.Telepherique;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.List;

/**
 * 1.64 : les recettes du mod qu'EMI ne connaît pas (elles sont dans le code, pas dans des fichiers de recette) :
 * le haut-fourneau (alliage, refonte), le laminoir et la brume d'Écho (diffuseur devant un ventilateur).
 * EMI charge cette classe seul ; sans EMI, elle n'est jamais lue.
 */
@EmiEntrypoint
public class EmiAirain implements EmiPlugin {
	private static ResourceLocation rl(String p) { return ResourceLocation.fromNamespaceAndPath("airain", p); }
	private static Item objet(String id) { return BuiltInRegistries.ITEM.get(ResourceLocation.parse(id)); }
	private static EmiStack pile(String id, int n) { return EmiStack.of(new ItemStack(objet(id), n)); }
	private static boolean existe(String id) { return objet(id) != Items.AIR; }

	public static final EmiRecipeCategory FOURNEAU = new EmiRecipeCategory(rl("blast_furnace"), EmiStack.of(objet("airain:blast_furnace_taphole")));
	public static final EmiRecipeCategory LAMINOIR = new EmiRecipeCategory(rl("rolling_mill"), EmiStack.of(objet("airain:airain_rolling_mill")));
	public static final EmiRecipeCategory BRUME = new EmiRecipeCategory(rl("echo_mist"), EmiStack.of(objet("airain:echo_diffuser")));

	@Override
	public void register(EmiRegistry r) {
		r.addCategory(FOURNEAU); r.addCategory(LAMINOIR); r.addCategory(BRUME);
		r.addWorkstation(FOURNEAU, EmiStack.of(objet("airain:blast_furnace_taphole")));
		r.addWorkstation(FOURNEAU, EmiStack.of(objet("airain:blast_furnace_hopper")));
		r.addWorkstation(LAMINOIR, EmiStack.of(objet("airain:airain_rolling_mill")));
		r.addWorkstation(BRUME, EmiStack.of(objet("airain:echo_diffuser")));
		r.addWorkstation(BRUME, EmiStack.of(objet("create:encased_fan")));

		EmiIngredient cuivre = EmiIngredient.of(List.of(EmiIngredient.of(TagKey.create(Registries.ITEM, ResourceLocation.parse("c:ingots/copper")), 3), pile("create:crushed_raw_copper", 3)));
		EmiIngredient zinc = EmiIngredient.of(List.of(EmiIngredient.of(TagKey.create(Registries.ITEM, ResourceLocation.parse("c:ingots/zinc")), 1), pile("create:crushed_raw_zinc", 1)));
		EmiIngredient fondant = EmiIngredient.of(List.of(pile("minecraft:calcite", 1), pile("create:cinder_flour", 1), EmiStack.of(MetalAirain.LAITIER.get())));
		r.addRecipe(new Fourneau(rl("blast_furnace/alloy"), List.of(cuivre, zinc, fondant), 4 * 90, true, "airain.emi.surchauffe"));
		if (existe("kubejs:ferraille")) r.addRecipe(new Fourneau(rl("blast_furnace/scrap"), List.of(pile("kubejs:ferraille", 6)), 90, true, "airain.emi.chauffe"));
		if (existe("kubejs:rouage_brise")) r.addRecipe(new Fourneau(rl("blast_furnace/broken_cogs"), List.of(pile("kubejs:rouage_brise", 2)), 90, false, "airain.emi.chauffe"));

		r.addRecipe(new Simple(LAMINOIR, rl("rolling_mill/wire"), EmiStack.of(MetalAirain.LINGOT.get()), EmiStack.of(new ItemStack(Telepherique.FIL.get(), 2)), "airain.emi.laminoir"));

		String[][] brume = {{"minecraft:amethyst_shard", "ars_nouveau:source_gem", "1"}, {"minecraft:lapis_lazuli", "ars_nouveau:source_gem", "1"},
			{"minecraft:amethyst_block", "ars_nouveau:source_gem_block", "1"}, {"minecraft:sculk", "minecraft:echo_shard", "0.25"}};
		for (String[] b : brume) {
			if (!existe(b[1])) continue;
			EmiStack sortie = EmiStack.of(objet(b[1]));
			float c = Float.parseFloat(b[2]);
			if (c < 1) sortie.setChance(c);
			r.addRecipe(new Simple(BRUME, rl("echo_mist/" + ResourceLocation.parse(b[0]).getPath()), EmiStack.of(objet(b[0])), sortie, "airain.emi.brume"));
		}
	}

	/** Haut-fourneau : la charge au gueulard, la chaleur du brûleur, l'airain en fusion et le laitier au trou de coulée. */
	static class Fourneau extends BasicEmiRecipe {
		private final String chaleur;
		Fourneau(ResourceLocation id, List<EmiIngredient> charge, int mb, boolean laitier, String chaleur) {
			super(FOURNEAU, id, 130, 44);
			this.chaleur = chaleur;
			inputs.addAll(charge);
			outputs.add(EmiStack.of(MetalAirain.SOURCE.get(), mb));
			if (laitier) { EmiStack l = EmiStack.of(MetalAirain.LAITIER.get()); l.setChance(0.6f); outputs.add(l); }
		}
		@Override
		public void addWidgets(WidgetHolder w) {
			for (int i = 0; i < inputs.size(); i++) w.addSlot(inputs.get(i), i * 18, 4);
			w.addTexture(EmiTexture.EMPTY_ARROW, 58, 5);
			for (int i = 0; i < outputs.size(); i++) w.addSlot(outputs.get(i), 88 + i * 20, 4).recipeContext(this);
			w.addSlot(EmiStack.of(objet("create:blaze_burner")), 0, 25).drawBack(false);
			w.addText(Component.translatable(chaleur), 20, 30, 0x404040, false);
		}
	}
	/** Une entrée, une sortie, une ligne d'explication. */
	static class Simple extends BasicEmiRecipe {
		private final String aide;
		Simple(EmiRecipeCategory c, ResourceLocation id, EmiIngredient entree, EmiStack sortie, String aide) {
			super(c, id, 110, 38);
			this.aide = aide;
			inputs.add(entree); outputs.add(sortie);
		}
		@Override
		public void addWidgets(WidgetHolder w) {
			w.addSlot(inputs.get(0), 14, 2);
			w.addTexture(EmiTexture.EMPTY_ARROW, 42, 3);
			w.addSlot(outputs.get(0), 74, 2).recipeContext(this);
			w.addText(Component.translatable(aide), 0, 26, 0x404040, false);
		}
	}
}
