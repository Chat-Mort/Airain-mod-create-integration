package fr.chatmort.airain;

import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.ShapelessRecipe;

import com.mojang.serialization.MapCodec;

/**
 * Monter une couronne ou un diadème sur un casque de netherite à l'établi : une recette sans forme ordinaire (visible dans
 * JEI et EMI), mais le casque garde ses enchantements, son usure et son nom.
 */
public class Monture extends ShapelessRecipe {
	public Monture(String groupe, CraftingBookCategory cat, ItemStack resultat, NonNullList<Ingredient> ingredients) {
		super(groupe, cat, resultat, ingredients);
	}

	@Override
	public ItemStack assemble(CraftingInput entree, HolderLookup.Provider r) {
		ItemStack sortie = super.assemble(entree, r);
		for (int i = 0; i < entree.size(); i++) {
			ItemStack s = entree.getItem(i);
			if (s.is(Items.NETHERITE_HELMET)) { sortie.applyComponents(s.getComponentsPatch()); break; }
		}
		return sortie;
	}

	@Override
	public RecipeSerializer<?> getSerializer() { return SERIALISEUR; }

	private static Monture de(ShapelessRecipe r) {
		return new Monture(r.getGroup(), r.category(), r.getResultItem(null), r.getIngredients());
	}

	public static final RecipeSerializer<Monture> SERIALISEUR = new RecipeSerializer<>() {
		private final MapCodec<Monture> codec = RecipeSerializer.SHAPELESS_RECIPE.codec().xmap(Monture::de, m -> m);
		private final StreamCodec<RegistryFriendlyByteBuf, Monture> flux = RecipeSerializer.SHAPELESS_RECIPE.streamCodec().map(Monture::de, m -> m);

		@Override
		public MapCodec<Monture> codec() { return codec; }

		@Override
		public StreamCodec<RegistryFriendlyByteBuf, Monture> streamCodec() { return flux; }
	};
}
