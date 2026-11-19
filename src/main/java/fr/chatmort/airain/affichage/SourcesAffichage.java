package fr.chatmort.airain.affichage;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.simibubi.create.api.behaviour.display.DisplaySource;
import com.simibubi.create.api.registry.CreateRegistries;
import com.simibubi.create.content.redstone.displayLink.DisplayLinkContext;
import com.simibubi.create.content.redstone.displayLink.source.PercentOrProgressBarDisplaySource;
import com.simibubi.create.content.redstone.displayLink.target.DisplayTargetStats;
import com.simibubi.create.foundation.gui.ModularGuiLineBuilder;

import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.fonderie.Fourneau;
import fr.chatmort.airain.fonderie.HautFourneauBlockEntity;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 1.66.4 : nouvelles sources de la liaison d'affichage, la liaison posée directement sur le bloc :
 * contenu (objets) et remplissage des coffres-forts de Create et des stockages Sophisticated, fluides et remplissage des
 * réservoirs de Create, et le haut fourneau d'airain (état, coulée, airain fondu, charge).
 */
public final class SourcesAffichage {
	public static final DeferredRegister<DisplaySource> SOURCES = DeferredRegister.create(CreateRegistries.DISPLAY_SOURCE, AirainMod.ID);
	public static final DeferredHolder<DisplaySource, Objets> OBJETS = SOURCES.register("contents", Objets::new);
	public static final DeferredHolder<DisplaySource, Fluides> FLUIDES = SOURCES.register("fluids", Fluides::new);
	public static final DeferredHolder<DisplaySource, Remplissage> REMPLISSAGE = SOURCES.register("fill_level", Remplissage::new);
	public static final DeferredHolder<DisplaySource, FourneauSource> FOURNEAU = SOURCES.register("blast_furnace", FourneauSource::new);

	private SourcesAffichage() {}

	private static String id(BlockEntityType<?> t) { ResourceLocation k = BuiltInRegistries.BLOCK_ENTITY_TYPE.getKey(t); return k == null ? "" : k.toString(); }
	private static boolean coffreFort(BlockEntityType<?> t) { return id(t).equals("create:item_vault"); }
	private static boolean reservoir(BlockEntityType<?> t) { String i = id(t); return i.equals("create:fluid_tank") || i.equals("create:creative_fluid_tank"); }
	private static boolean sophistique(BlockEntityType<?> t) { String i = id(t); return i.startsWith("sophisticatedstorage:") && !i.contains("decoration"); }

	/** Rattache les sources aux blocs, par leur type de bloc-entité (les mods absents ne gênent pas : leurs types n'existent pas). */
	public static void associer() {
		DisplaySource.BY_BLOCK_ENTITY.addProvider(t -> coffreFort(t) || sophistique(t) ? OBJETS.get() : null);
		DisplaySource.BY_BLOCK_ENTITY.addProvider(t -> coffreFort(t) || sophistique(t) || reservoir(t) ? REMPLISSAGE.get() : null);
		DisplaySource.BY_BLOCK_ENTITY.addProvider(t -> reservoir(t) ? FLUIDES.get() : null);
		DisplaySource.BY_BLOCK_ENTITY.add(Fourneau.BE.get(), FOURNEAU.get());
	}

	// ------------------------------------------------------------------ contenu en objets (coffre-fort, Sophisticated)
	public static class Objets extends SourceListe {
		@Override
		protected List<Entree> entrees(DisplayLinkContext ctx) {
			var h = ctx.level().getCapability(Capabilities.ItemHandler.BLOCK, ctx.getSourcePos(), null);
			if (h == null) return List.of();
			Map<String, Object[]> m = new LinkedHashMap<>();
			for (int i = 0; i < h.getSlots(); i++) {
				ItemStack s = h.getStackInSlot(i);
				if (s.isEmpty()) continue;
				String cle = BuiltInRegistries.ITEM.getKey(s.getItem()) + "|" + s.getComponentsPatch().hashCode();
				Object[] o = m.computeIfAbsent(cle, k -> new Object[] {s, new long[] {0}});
				((long[]) o[1])[0] += s.getCount();
			}
			List<Entree> l = new ArrayList<>();
			for (Object[] o : m.values()) { ItemStack s = (ItemStack) o[0]; l.add(new Entree(s.getHoverName(), BuiltInRegistries.ITEM.getKey(s.getItem()).toString(), ((long[]) o[1])[0], "")); }
			return l;
		}
		@Override protected String getTranslationKey() { return "contents"; }
	}

	// ------------------------------------------------------------------ fluides d'un réservoir
	public static class Fluides extends SourceListe {
		@Override
		protected List<Entree> entrees(DisplayLinkContext ctx) {
			var h = ctx.level().getCapability(Capabilities.FluidHandler.BLOCK, ctx.getSourcePos(), null);
			if (h == null) return List.of();
			Map<String, Object[]> m = new LinkedHashMap<>();
			for (int i = 0; i < h.getTanks(); i++) {
				FluidStack s = h.getFluidInTank(i);
				if (s.isEmpty()) continue;
				String cle = BuiltInRegistries.FLUID.getKey(s.getFluid()).toString();
				Object[] o = m.computeIfAbsent(cle, k -> new Object[] {s, new long[] {0}});
				((long[]) o[1])[0] += s.getAmount();
			}
			List<Entree> l = new ArrayList<>();
			for (var e : m.entrySet()) { FluidStack s = (FluidStack) e.getValue()[0]; l.add(new Entree(s.getHoverName(), e.getKey(), ((long[]) e.getValue()[1])[0], "mB")); }
			return l;
		}
		// abrégés, les fluides se comptent en seaux
		@Override protected String nombre(Entree e, boolean abrege) { return abrege ? arrondi(e.quantite() / 1000.0) + " B" : e.quantite() + " mB"; }
		@Override protected String getTranslationKey() { return "fluids"; }
	}

	// ------------------------------------------------------------------ remplissage (objets ou fluides), en % ou en barre
	public static class Remplissage extends PercentOrProgressBarDisplaySource {
		@Override
		protected Float getProgress(DisplayLinkContext ctx) {
			var f = ctx.level().getCapability(Capabilities.FluidHandler.BLOCK, ctx.getSourcePos(), null);
			var o = ctx.level().getCapability(Capabilities.ItemHandler.BLOCK, ctx.getSourcePos(), null);
			if (o != null) {
				long n = 0, max = 0;
				for (int i = 0; i < o.getSlots(); i++) {
					ItemStack s = o.getStackInSlot(i);
					int lim = Math.min(o.getSlotLimit(i), s.isEmpty() ? 64 : s.getMaxStackSize() * Math.max(1, o.getSlotLimit(i) / 64));
					n += s.getCount(); max += Math.max(1, lim);
				}
				return max <= 0 ? null : Math.min(1f, n / (float) max);
			}
			if (f != null) {
				long n = 0, max = 0;
				for (int i = 0; i < f.getTanks(); i++) { n += f.getFluidInTank(i).getAmount(); max += f.getTankCapacity(i); }
				return max <= 0 ? null : Math.min(1f, n / (float) max);
			}
			return null;
		}
		@Override protected boolean progressBarActive(DisplayLinkContext ctx) { return ctx.sourceConfig().getInt("Barre") == 1; }
		@Override protected String getTranslationKey() { return "fill_level"; }
		@Override protected boolean allowsLabeling(DisplayLinkContext ctx) { return true; }
		@Override
		@OnlyIn(Dist.CLIENT)
		public void initConfigurationWidgets(DisplayLinkContext ctx, ModularGuiLineBuilder b, boolean premiere) {
			super.initConfigurationWidgets(ctx, b, premiere);
			if (!premiere) return;
			b.addSelectionScrollInput(0, 120, (si, l) -> si.forOptions(List.of(Component.translatable("airain.display.remplissage.0"),
				Component.translatable("airain.display.remplissage.1"))).titled(Component.translatable("airain.display.remplissage")), "Barre");
		}
	}

	// ------------------------------------------------------------------ haut fourneau d'airain
	public static class FourneauSource extends DisplaySource {
		@Override
		public List<MutableComponent> provideText(DisplayLinkContext ctx, DisplayTargetStats stats) {
			if (!(ctx.getSourceBlockEntity() instanceof HautFourneauBlockEntity f)) return EMPTY;
			int quoi = ctx.sourceConfig().getInt("Valeur");
			return switch (quoi) {
				case 1 -> List.of(Component.literal(Math.round(f.avancement() * 100) + " %"));
				case 2 -> List.of(Component.literal(f.cuve.getFluidAmount() + " mB"));
				case 3 -> List.of(Component.literal(f.cuve.getFluidAmount() / HautFourneauBlockEntity.LINGOT + ""));
				case 4 -> List.of(Component.literal(Math.round(f.cuve.getFluidAmount() * 100f / HautFourneauBlockEntity.CUVE) + " %"));
				case 5 -> {
					List<MutableComponent> l = new ArrayList<>();
					for (int i = 0; i < f.charge.getSlots() && l.size() < Math.max(1, stats.maxRows()); i++) {
						ItemStack s = f.charge.getStackInSlot(i);
						if (!s.isEmpty()) l.add(s.getHoverName().copy().append(" " + s.getCount()));
					}
					yield l.isEmpty() ? List.of(Component.translatable("airain.display.fourneau.vide")) : l;
				}
				default -> {
					int e = f.etatAffichage();
					yield List.of(Component.translatable(e >= 10 ? "airain.display.fourneau.etat.coule" : "airain.display.fourneau.etat." + e));
				}
			};
		}
		@Override protected String getTranslationKey() { return "blast_furnace"; }
		@Override
		@OnlyIn(Dist.CLIENT)
		public void initConfigurationWidgets(DisplayLinkContext ctx, ModularGuiLineBuilder b, boolean premiere) {
			if (!premiere) return;
			List<Component> o = new ArrayList<>();
			for (int i = 0; i < 6; i++) o.add(Component.translatable("airain.display.fourneau.valeur." + i));
			b.addSelectionScrollInput(0, 137, (si, l) -> si.forOptions(o).titled(Component.translatable("airain.display.fourneau.valeur")), "Valeur");
		}
	}
}
