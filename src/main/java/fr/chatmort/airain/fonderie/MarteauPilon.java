package fr.chatmort.airain.fonderie;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import fr.chatmort.airain.banc.BancEntretienBlockEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.IFluidHandlerItem;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * 1.69 : le marteau-pilon d'airain. Creuse en 3 × 3 sur la face visée (accroupi : un seul bloc).
 * Ctrl + clic droit : mode 5 × 5 (tête en airain rouge impérial), au prix de 20 mB d'huile de machine par bloc cassé,
 * prise sur le joueur (réserve du marteau, seaux, réservoirs, sacs à dos, burettes). Sans assez d'huile : 3 × 3.
 */
public final class MarteauPilon {
	private MarteauPilon() {}

	public static final int HUILE_PAR_BLOC = 20, BURETTE = BancEntretienBlockEntity.BURETTE;
	static final String MODE = "airain_marteau_5x5", RESERVE = "airain_marteau_huile";
	/** Ce que le marteau peut casser : ce que minent la pioche et la pelle. */
	public static final TagKey<Block> MINABLE = TagKey.create(net.minecraft.core.registries.Registries.BLOCK, ResourceLocation.fromNamespaceAndPath("airain", "mineable/steam_hammer"));

	// Palier : niveau du diamant, un peu plus lent (le poids), 2 400 coups, réparé à l'airain
	static final Tier PALIER = new Tier() {
		public int getUses() { return 2400; }
		public float getSpeed() { return 6f; }
		public float getAttackDamageBonus() { return 0f; }
		public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_DIAMOND_TOOL; }
		public int getEnchantmentValue() { return 12; }
		public Ingredient getRepairIngredient() { return Ingredient.of(MetalAirain.LINGOT.get()); }
	};

	public static final DeferredItem<Item> MARTEAU = AirainMod.ITEMS.register("airain_steam_hammer", () -> new Marteau(new Item.Properties()
		.attributes(DiggerItem.createAttributes(PALIER, 6f, -3.3f))));

	public static void charger() {}

	// ------------------------------------------------------------------ l'objet
	public static class Marteau extends DiggerItem {
		Marteau(Properties p) { super(PALIER, MINABLE, p); }

		// Ctrl + clic droit : c'est le jeu du joueur qui voit la touche Ctrl, il demande au serveur de changer de mode
		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
			ItemStack s = p.getItemInHand(main);
			if (level.isClientSide && FMLEnvironment.dist.isClient() && MarteauClient.ctrl()) {
				MarteauClient.basculer(main);
				return InteractionResultHolder.success(s);
			}
			return InteractionResultHolder.pass(s);
		}
		@Override
		public net.minecraft.world.InteractionResult useOn(net.minecraft.world.item.context.UseOnContext c) {
			if (c.getLevel().isClientSide && FMLEnvironment.dist.isClient() && MarteauClient.ctrl()) {
				MarteauClient.basculer(c.getHand());
				return net.minecraft.world.InteractionResult.SUCCESS;
			}
			return net.minecraft.world.InteractionResult.PASS;
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
			l.add(Component.translatable(cinq(s) ? "airain.marteau.mode5" : "airain.marteau.mode3").withStyle(cinq(s) ? ChatFormatting.RED : ChatFormatting.GOLD));
			l.add(Component.translatable("airain.marteau.aide").withStyle(ChatFormatting.GRAY));
			l.add(Component.translatable("airain.marteau.aide_huile", HUILE_PAR_BLOC).withStyle(ChatFormatting.GRAY));
			int r = reserve(s);
			if (r > 0) l.add(Component.translatable("airain.marteau.reserve", r).withStyle(ChatFormatting.DARK_GRAY));
		}
	}

	public static boolean cinq(ItemStack s) { CustomData d = s.get(DataComponents.CUSTOM_DATA); return d != null && d.copyTag().getBoolean(MODE); }
	static int reserve(ItemStack s) { CustomData d = s.get(DataComponents.CUSTOM_DATA); return d == null ? 0 : d.copyTag().getInt(RESERVE); }
	private static void ecrire(ItemStack s, String cle, int v, boolean b, boolean estBool) {
		CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { if (estBool) t.putBoolean(cle, b); else if (v <= 0) t.remove(cle); else t.putInt(cle, v); });
	}

	// ------------------------------------------------------------------ le changement de mode (paquet client -> serveur)
	public record Mode(boolean mainPrincipale) implements CustomPacketPayload {
		public static final Type<Mode> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "marteau_mode"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Mode> CODEC = StreamCodec.composite(ByteBufCodecs.BOOL, Mode::mainPrincipale, Mode::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Mode m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p)) return;
				ItemStack s = p.getItemInHand(m.mainPrincipale() ? InteractionHand.MAIN_HAND : InteractionHand.OFF_HAND);
				if (!s.is(MARTEAU.get())) return;
				boolean nouveau = !cinq(s);
				ecrire(s, MODE, 0, nouveau, true);
				p.level().playSound(null, p.blockPosition(), nouveau ? SoundEvents.PISTON_EXTEND : SoundEvents.PISTON_CONTRACT, SoundSource.PLAYERS, 0.6f, nouveau ? 0.7f : 0.9f);
				p.displayClientMessage(Component.translatable(nouveau ? "airain.marteau.mode5" : "airain.marteau.mode3").withStyle(nouveau ? ChatFormatting.RED : ChatFormatting.GOLD), true);
			});
		}
	}

	// ------------------------------------------------------------------ le coup : les blocs autour du bloc cassé
	/** Coups en cours (le marteau casse lui-même les blocs voisins : leurs événements ne doivent pas relancer le coup). */
	private static boolean enCours;

	public static void casse(BlockEvent.BreakEvent e) {
		if (enCours || !(e.getPlayer() instanceof ServerPlayer p) || p.isShiftKeyDown() || e.isCanceled()) return;
		ItemStack outil = p.getMainHandItem();
		if (!outil.is(MARTEAU.get())) return;
		BlockState centre = e.getState();
		if (!outil.isCorrectToolForDrops(centre)) return;
		HitResult h = p.pick(p.blockInteractionRange(), 0f, false);
		if (!(h instanceof BlockHitResult bh) || !bh.getBlockPos().equals(e.getPos())) return;
		Direction face = bh.getDirection();
		Level l = p.level();
		float durete = centre.getDestroySpeed(l, e.getPos());
		// les voisins que le coup cassera vraiment (ni air, ni plus durs, ni à inventaire, ni mauvais outil)
		List<BlockPos> cinq = voisins(l, e.getPos(), face, 2, outil, durete), trois = voisins(l, e.getPos(), face, 1, outil, durete);
		List<BlockPos> cibles = trois;
		if (cinq(outil)) {
			int besoin = (cinq.size() + 1) * HUILE_PAR_BLOC;               // le bloc visé compte aussi
			if (huile(p, outil, besoin, false) >= besoin) { huile(p, outil, besoin, true); cibles = cinq; }
			else p.displayClientMessage(Component.translatable("airain.marteau.sans_huile", besoin).withStyle(ChatFormatting.RED), true);
		}
		enCours = true;
		try {
			for (BlockPos q : cibles) {
				if (outil.isEmpty() || !p.getMainHandItem().is(MARTEAU.get())) break;    // marteau cassé en route
				p.gameMode.destroyBlock(q);                                   // comme si le joueur minait : protections, enchantements, usure
			}
		} finally { enCours = false; }
	}

	private static List<BlockPos> voisins(Level l, BlockPos c, Direction face, int r, ItemStack outil, float durete) {
		List<BlockPos> v = new ArrayList<>();
		Direction.Axis ax = face.getAxis();
		for (int i = -r; i <= r; i++)
			for (int j = -r; j <= r; j++) {
				if (i == 0 && j == 0) continue;
				BlockPos q = switch (ax) { case X -> c.offset(0, i, j); case Y -> c.offset(i, 0, j); default -> c.offset(i, j, 0); };
				BlockState s = l.getBlockState(q);
				if (s.isAir() || l.getBlockEntity(q) != null || !outil.isCorrectToolForDrops(s) || !s.is(MINABLE)) continue;
				float d = s.getDestroySpeed(l, q);
				if (d < 0 || d > durete + 0.01f) continue;
				v.add(q);
			}
		return v;
	}

	// ------------------------------------------------------------------ l'huile : réserve du marteau, récipients, sacs à dos, burettes
	/** Compte (executer = false) ou prend (executer = true) jusqu'à n mB d'huile ; renvoie ce qui est disponible / pris. */
	static int huile(ServerPlayer p, ItemStack marteau, int n, boolean executer) {
		int pris = Math.min(n, reserve(marteau));
		if (executer && pris > 0) ecrire(marteau, RESERVE, reserve(marteau) - pris, false, false);
		// récipients : tout objet qui contient un liquide (seaux, réservoirs portables, sacs à dos avec réservoir)
		IdentityHashMap<ItemStack, Boolean> vus = new IdentityHashMap<>();
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize() && pris < n; i++) {
			ItemStack s = inv.getItem(i);
			if (s.isEmpty() || estBurette(s) || s == marteau) continue;
			vus.put(s, true);
			IFluidHandlerItem fh = s.getCapability(Capabilities.FluidHandler.ITEM);
			if (fh == null) continue;
			int k = vider(fh, n - pris, executer);
			pris += k;
			if (executer && k > 0 && fh.getContainer() != s) inv.setItem(i, fh.getContainer());   // seau vidé : il redevient un seau vide
		}
		// sacs à dos portés ailleurs (emplacements d'accessoires) : Sophisticated Backpacks les connaît tous
		for (ItemStack sac : sacs(p)) {
			if (pris >= n) break;
			if (vus.containsKey(sac)) continue;
			IFluidHandlerItem fh = sac.getCapability(Capabilities.FluidHandler.ITEM);
			if (fh != null) pris += vider(fh, n - pris, executer);
		}
		// burettes : 500 mB chacune ; ce qui n'est pas utilisé reste dans la réserve du marteau
		for (int i = 0; i < inv.getContainerSize() && pris < n; i++) {
			ItemStack s = inv.getItem(i);
			if (!estBurette(s)) continue;
			int dispo = s.getCount() * BURETTE;
			if (!executer) { pris += Math.min(dispo, n - pris); continue; }
			while (pris < n && !s.isEmpty()) {
				s.shrink(1);
				int k = Math.min(BURETTE, n - pris);
				pris += k;
				if (k < BURETTE) ecrire(marteau, RESERVE, reserve(marteau) + BURETTE - k, false, false);
			}
		}
		return pris;
	}

	private static int vider(IFluidHandlerItem fh, int n, boolean executer) {
		int pris = 0;
		for (int t = 0; t < fh.getTanks() && pris < n; t++) {
			FluidStack f = fh.getFluidInTank(t);
			if (f.isEmpty() || !f.is(BancEntretienBlockEntity.HUILES)) continue;
			FluidStack d = fh.drain(f.copyWithAmount(n - pris), executer ? IFluidHandler.FluidAction.EXECUTE : IFluidHandler.FluidAction.SIMULATE);
			pris += d.getAmount();
		}
		return pris;
	}

	private static boolean estBurette(ItemStack s) { return !s.isEmpty() && BuiltInRegistries.ITEM.getKey(s.getItem()).equals(BancEntretienBlockEntity.BURETTE_ID); }

	/** Les sacs à dos du joueur, où qu'ils soient portés (inventaire, plastron, accessoires), via Sophisticated Backpacks s'il est là. */
	@SuppressWarnings("unchecked")
	private static List<ItemStack> sacs(Player p) {
		List<ItemStack> l = new ArrayList<>();
		try {
			Class<?> prov = Class.forName("net.p3pp3rf1y.sophisticatedbackpacks.util.PlayerInventoryProvider");
			Class<?> conso = Class.forName("net.p3pp3rf1y.sophisticatedbackpacks.util.PlayerInventoryProvider$BackpackInventorySlotConsumer");
			Object instance = prov.getMethod("get").invoke(null);
			Object c = java.lang.reflect.Proxy.newProxyInstance(conso.getClassLoader(), new Class<?>[] {conso}, (o, m, a) -> {
				if (m.getName().equals("accept")) { l.add((ItemStack) a[0]); return false; }   // false : on continue de chercher
				return m.getDeclaringClass() == Object.class ? m.invoke(l, a) : null;
			});
			prov.getMethod("runOnBackpacks", Player.class, conso).invoke(instance, p, c);
		} catch (Throwable t) { /* Sophisticated Backpacks absent ou changé : seuls les sacs de l'inventaire comptent */ }
		return l;
	}
}
