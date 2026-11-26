package fr.chatmort.airain.fonderie;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import fr.chatmort.airain.AirainMod;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * 1.69.9 : le carton de motif. On construit un échantillon à la main, on prend ses deux coins au carton (les blocs visés eux-mêmes),
 * accroupi + molette pour l'épaisseur, puis un clic droit l'enregistre (jusqu'à 32 × 16 × 32, état complet de chaque bloc,
 * l'air = « ne rien poser »). Tenu dans l'autre main du cordeau, le volume part du piquet A et se répète dans les trois directions.
 */
public final class Motif {
	private Motif() {}

	public static final int COTE = 32, HAUT = 16, APERCU_MAX = 1000;
	static final String A = "airain_carton_a", B = "airain_carton_b", DIM = "airain_carton_dim", MOTIF = "airain_motif", ROT = "airain_motif_rot";

	public static final DeferredItem<Item> CARTON = AirainMod.ITEMS.register("pattern_card", () -> new Carton(new Item.Properties().stacksTo(16)));

	public static void charger() {}

	// ------------------------------------------------------------------ l'objet
	public static class Carton extends Item {
		Carton(Properties p) { super(p); }

		@Override
		public InteractionResult useOn(UseOnContext c) {
			if (c.getLevel().isClientSide && FMLEnvironment.dist.isClient())
				MotifClient.clic(c.getHand(), new BlockHitResult(c.getClickLocation(), c.getClickedFace(), c.getClickedPos(), c.isInside()));
			return InteractionResult.SUCCESS;
		}
		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
			if (level.isClientSide && FMLEnvironment.dist.isClient()) MotifClient.clic(main, null);
			return InteractionResultHolder.success(p.getItemInHand(main));
		}
		@Override
		public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
			Grille g = grille(s, null);
			if (g == null) l.add(Component.translatable("airain.motif.vierge").withStyle(ChatFormatting.GRAY));
			else {
				l.add(Component.translatable("airain.motif.taille", g.sx, g.sy, g.sz, g.pleins()).withStyle(ChatFormatting.GOLD));
				if (rot(s) > 0) l.add(Component.translatable("airain.motif.tourne", rot(s) * 90).withStyle(ChatFormatting.GOLD));
				int n = 0;
				for (Map.Entry<Item, Integer> e : g.besoins().entrySet()) {
					if (n++ == 6) { l.add(Component.literal("  …").withStyle(ChatFormatting.DARK_GRAY)); break; }
					l.add(Component.literal("  " + e.getValue() + " × ").append(e.getKey().getDescription()).withStyle(ChatFormatting.DARK_GRAY));
				}
			}
			l.add(Component.translatable("airain.motif.aide_prendre").withStyle(ChatFormatting.GRAY));
			l.add(Component.translatable("airain.motif.aide_poser").withStyle(ChatFormatting.GRAY));
		}
	}

	// ------------------------------------------------------------------ données
	private static CompoundTag lire(ItemStack s) { CustomData d = s.get(DataComponents.CUSTOM_DATA); return d == null ? null : d.getUnsafe(); }
	public static boolean enregistre(ItemStack s) { CompoundTag t = lire(s); return t != null && t.contains(MOTIF); }
	public static int rot(ItemStack s) { CompoundTag t = lire(s); return t == null ? 0 : t.getInt(ROT) & 3; }
	public static BlockPos a(ItemStack s, Level l) { CompoundTag t = lire(s); return t != null && t.contains(A) && t.getString(DIM).equals(l.dimension().location().toString()) ? BlockPos.of(t.getLong(A)) : null; }
	public static BlockPos b(ItemStack s, Level l) { CompoundTag t = lire(s); return t != null && t.contains(B) && t.getString(DIM).equals(l.dimension().location().toString()) ? BlockPos.of(t.getLong(B)) : null; }

	/** Le motif décodé : dimensions, palette d'états, cases (0 = ne rien poser, sinon index + 1 dans la palette). */
	public static final class Grille {
		public final int sx, sy, sz; public final BlockState[] palette; public final byte[] cases;
		Grille(int sx, int sy, int sz, BlockState[] p, byte[] c) { this.sx = sx; this.sy = sy; this.sz = sz; palette = p; cases = c; }
		BlockState brut(int x, int y, int z) { int i = cases[(y * sz + z) * sx + x] & 255; return i == 0 ? null : palette[i - 1]; }
		int pleins() { int n = 0; for (byte b : cases) if (b != 0) n++; return n; }
		Map<Item, Integer> besoins() {
			Map<Item, Integer> m = new LinkedHashMap<>();
			for (byte b : cases) { if (b == 0) continue; BlockState s = palette[(b & 255) - 1]; Item i = objet(s); if (i != Items.AIR) m.merge(i, 1, Integer::sum); }
			return m;
		}
	}
	private static final Map<CompoundTag, Grille> CACHE = new IdentityHashMap<>();

	/** Décode le motif du carton (mis en cache tant que les données de l'objet ne changent pas). */
	public static Grille grille(ItemStack s, Level l) {
		CompoundTag t = lire(s);
		if (t == null || !t.contains(MOTIF)) return null;
		synchronized (CACHE) {
			Grille g = CACHE.get(t);
			if (g != null) return g;
			if (CACHE.size() > 16) CACHE.clear();
			CompoundTag m = t.getCompound(MOTIF);
			ListTag pl = m.getList("palette", Tag.TAG_COMPOUND);
			BlockState[] p = new BlockState[pl.size()];
			var blocs = l != null ? l.holderLookup(Registries.BLOCK) : net.minecraft.core.registries.BuiltInRegistries.BLOCK.asLookup();
			for (int i = 0; i < p.length; i++) p[i] = NbtUtils.readBlockState(blocs, pl.getCompound(i));
			g = new Grille(m.getInt("sx"), m.getInt("sy"), m.getInt("sz"), p, m.getByteArray("cases"));
			if (g.cases.length != g.sx * g.sy * g.sz) return null;
			CACHE.put(t, g);
			return g;
		}
	}

	/**
	 * L'état à poser à (dx, dy, dz) du piquet A, motif tourné de rot quarts de tour (sens horaire vu du dessus) et répété.
	 * null : ne rien poser.
	 */
	public static BlockState etat(Grille g, int rot, int dx, int dy, int dz) {
		int rx = (rot & 1) == 1 ? g.sz : g.sx, rz = (rot & 1) == 1 ? g.sx : g.sz;
		int u = Math.floorMod(dx, rx), v = Math.floorMod(dy, g.sy), w = Math.floorMod(dz, rz);
		// on défait la rotation, quart de tour par quart de tour
		for (int k = 0; k < rot; k++) { int nu = w, nw = rx - 1 - u; int t = rx; rx = rz; rz = t; u = nu; w = nw; }
		BlockState s = g.brut(u, v, w);
		if (s == null) return null;
		return switch (rot & 3) { case 1 -> s.rotate(Rotation.CLOCKWISE_90); case 2 -> s.rotate(Rotation.CLOCKWISE_180); case 3 -> s.rotate(Rotation.COUNTERCLOCKWISE_90); default -> s; };
	}

	/** L'objet qui sert à poser cet état (Items.AIR : rien à payer, comme le haut d'une porte ou la tête d'un lit). */
	static Item objet(BlockState s) {
		if (s.hasProperty(BlockStateProperties.DOUBLE_BLOCK_HALF) && s.getValue(BlockStateProperties.DOUBLE_BLOCK_HALF) == DoubleBlockHalf.UPPER) return Items.AIR;
		if (s.hasProperty(BlockStateProperties.BED_PART) && s.getValue(BlockStateProperties.BED_PART) == BedPart.HEAD) return Items.AIR;
		return s.getBlock().asItem();
	}

	/** « Floor 12 × 8: 96 blocks (pattern) » ou « Volume 12 × 3 × 8: 168 blocks (pattern) ». */
	public static MutableComponent forme(BlockPos a, BlockPos b, ItemStack carton, Level l) {
		Grille g = grille(carton, l);
		int dx = Math.abs(a.getX() - b.getX()) + 1, dy = Math.abs(a.getY() - b.getY()) + 1, dz = Math.abs(a.getZ() - b.getZ()) + 1;
		if (!Cordeau.valide(a, b)) return Component.translatable("airain.cordeau.trop", Cordeau.LIGNE_MAX, Cordeau.COTE_MAX);
		int n = 0, r = rot(carton);
		if (g != null) for (BlockPos c : BlockPos.betweenClosed(a, b)) if (etat(g, r, c.getX() - a.getX(), c.getY() - a.getY(), c.getZ() - a.getZ()) != null) n++;
		MutableComponent m = dy > 1 ? Component.translatable("airain.cordeau.forme.volume", dx, dy, dz, n) : Component.translatable("airain.cordeau.forme.sol", dx, dz, n);
		return m.append(Component.translatable("airain.motif.suffixe"));
	}

	// ------------------------------------------------------------------ actions du carton en main (paquet du cordeau)
	static void action(Cordeau.Action m, ServerPlayer p, ServerLevel sl, ItemStack s) {
		String dim = sl.dimension().location().toString();
		BlockPos a = a(s, sl), b = b(s, sl);
		switch (m.quoi()) {
			case Cordeau.POINT -> {
				BlockPos c = m.pos();
				if (c.distToCenterSqr(p.getEyePosition()) > Cordeau.PORTEE * Cordeau.PORTEE || !sl.isLoaded(c)) return;
				if (a == null || b != null) {
					CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.putLong(A, c.asLong()); t.remove(B); t.putString(DIM, dim); });
					p.displayClientMessage(Component.translatable("airain.motif.coin_a").withStyle(ChatFormatting.GOLD), true);
				} else {
					if (!tailleOk(a, c)) { p.displayClientMessage(Component.translatable("airain.motif.trop", COTE, HAUT, COTE).withStyle(ChatFormatting.RED), true); return; }
					CustomData.update(DataComponents.CUSTOM_DATA, s, t -> t.putLong(B, c.asLong()));
					p.displayClientMessage(selection(a, c).append(Component.translatable("airain.motif.suite_enregistrer")).withStyle(ChatFormatting.GOLD), true);
				}
				sl.playSound(null, c, SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8f, 1.2f);
			}
			case Cordeau.POSER -> { if (a != null && b != null) enregistrer(p, sl, s, a, b); }
			case Cordeau.ANNULER -> {
				// clic gauche : d'abord la sélection en cours, sinon le motif
				if (a != null) CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.remove(A); t.remove(B); t.remove(DIM); });
				else CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.remove(MOTIF); t.remove(ROT); });
				p.displayClientMessage(Component.translatable(a != null ? "airain.motif.selection_effacee" : "airain.motif.efface").withStyle(ChatFormatting.GRAY), true);
			}
			case Cordeau.MODE -> { if (enregistre(s)) tourner(p, sl, s); }
			case Cordeau.TAILLE -> {
				if (a == null || b == null || m.pos().getX() < 0 || m.pos().getX() > 5) return;
				BlockPos[] n = Cordeau.agrandir(a, b, Direction.from3DDataValue(m.pos().getX()), m.pos().getY() > 0 ? 1 : -1);
				if (n == null || !tailleOk(n[0], n[1])) return;
				CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.putLong(A, n[0].asLong()); t.putLong(B, n[1].asLong()); });
				p.displayClientMessage(selection(n[0], n[1]).withStyle(ChatFormatting.GOLD), true);
			}
			default -> {}
		}
	}

	static boolean tailleOk(BlockPos a, BlockPos b) {
		return Math.abs(a.getX() - b.getX()) < COTE && Math.abs(a.getY() - b.getY()) < HAUT && Math.abs(a.getZ() - b.getZ()) < COTE;
	}
	static MutableComponent selection(BlockPos a, BlockPos b) {
		return Component.translatable("airain.motif.selection", Math.abs(a.getX() - b.getX()) + 1, Math.abs(a.getY() - b.getY()) + 1, Math.abs(a.getZ() - b.getZ()) + 1);
	}

	static void tourner(ServerPlayer p, ServerLevel sl, ItemStack carton) {
		int r = (rot(carton) + 1) & 3;
		CustomData.update(DataComponents.CUSTOM_DATA, carton, t -> t.putInt(ROT, r));
		p.displayClientMessage(Component.translatable("airain.motif.tourne", r * 90).withStyle(ChatFormatting.GOLD), true);
		sl.playSound(null, p.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8f, 0.9f);
	}

	/** Lit le monde entre A et B et l'écrit sur le carton. Une pile de cartons vierges : on n'en enregistre qu'un. */
	private static void enregistrer(ServerPlayer p, ServerLevel sl, ItemStack s, BlockPos a, BlockPos b) {
		if (!tailleOk(a, b)) return;
		BlockPos lo = new BlockPos(Math.min(a.getX(), b.getX()), Math.min(a.getY(), b.getY()), Math.min(a.getZ(), b.getZ()));
		int sx = Math.abs(a.getX() - b.getX()) + 1, sy = Math.abs(a.getY() - b.getY()) + 1, sz = Math.abs(a.getZ() - b.getZ()) + 1;
		List<BlockState> palette = new ArrayList<>();
		byte[] cases = new byte[sx * sy * sz];
		int pleins = 0;
		for (int y = 0; y < sy; y++)
			for (int z = 0; z < sz; z++)
				for (int x = 0; x < sx; x++) {
					BlockState st = sl.getBlockState(lo.offset(x, y, z));
					if (st.isAir() || st.getBlock() instanceof LiquidBlock) continue;
					int i = palette.indexOf(st);
					if (i < 0) { if (palette.size() == 255) { p.displayClientMessage(Component.translatable("airain.motif.trop_blocs").withStyle(ChatFormatting.RED), true); return; } palette.add(st); i = palette.size() - 1; }
					cases[(y * sz + z) * sx + x] = (byte) (i + 1);
					pleins++;
				}
		if (pleins == 0) { p.displayClientMessage(Component.translatable("airain.motif.vide").withStyle(ChatFormatting.RED), true); return; }
		CompoundTag m = new CompoundTag();
		m.putInt("sx", sx); m.putInt("sy", sy); m.putInt("sz", sz);
		ListTag pl = new ListTag();
		for (BlockState st : palette) pl.add(NbtUtils.writeBlockState(st));
		m.put("palette", pl); m.putByteArray("cases", cases);
		ItemStack cible = s;
		if (s.getCount() > 1) { cible = s.split(1); }
		CustomData.update(DataComponents.CUSTOM_DATA, cible, t -> { t.put(MOTIF, m); t.remove(ROT); t.remove(A); t.remove(B); t.remove(DIM); });
		if (cible != s && !p.getInventory().add(cible)) p.drop(cible, false);
		p.displayClientMessage(Component.translatable("airain.motif.enregistre", sx, sy, sz, pleins).withStyle(ChatFormatting.GOLD), true);
		sl.playSound(null, p.blockPosition(), SoundEvents.UI_CARTOGRAPHY_TABLE_TAKE_RESULT, SoundSource.PLAYERS, 0.9f, 1f);
	}

	/** Pose du motif répété entre les piquets du cordeau : états exacts, cases vides seulement, blocs de l'inventaire. */
	static void poser(ServerPlayer p, ServerLevel sl, ItemStack cordeau, ItemStack carton) {
		BlockPos a = Cordeau.a(cordeau, sl), b = Cordeau.b(cordeau, sl);
		Grille g = grille(carton, sl);
		if (a == null || b == null || g == null || !Cordeau.valide(a, b)) return;
		int r = rot(carton), poses = 0;
		boolean coupe = false;
		Map<Item, Integer> manque = new LinkedHashMap<>();
		List<BlockPos> plusTard = new ArrayList<>();
		// du bas vers le haut, pour que ce qui s'appuie sur un bloc du motif trouve son appui
		List<BlockPos> ordre = new ArrayList<>();
		for (BlockPos c : BlockPos.betweenClosed(a, b)) ordre.add(c.immutable());
		ordre.sort((u, v) -> Integer.compare(u.getY(), v.getY()));
		for (int passe = 0; passe < 2; passe++) {
			for (BlockPos c : passe == 0 ? ordre : plusTard) {
				if (poses >= Cordeau.POSE_MAX) { coupe = true; break; }
				BlockState st = etat(g, r, c.getX() - a.getX(), c.getY() - a.getY(), c.getZ() - a.getZ());
				if (st == null || !sl.isLoaded(c) || !sl.getBlockState(c).canBeReplaced() || !sl.mayInteract(p, c)) continue;
				if (!sl.getEntities((net.minecraft.world.entity.Entity) null, new net.minecraft.world.phys.AABB(c), e -> e.blocksBuilding).isEmpty()) continue;
				if (!st.canSurvive(sl, c)) { if (passe == 0) plusTard.add(c); continue; }
				Item it = objet(st);
				if (it != Items.AIR && !p.getAbilities().instabuild && !prendre(p, it)) { manque.merge(it, 1, Integer::sum); continue; }
				// 1 | 2 | 16 : voisins prévenus, mais sans recalculer les formes (marches, murets restent comme enregistrés)
				sl.setBlock(c, st, Block.UPDATE_ALL | Block.UPDATE_KNOWN_SHAPE);
				poses++;
			}
			if (coupe) break;
		}
		if (poses > 0) sl.playSound(null, b, SoundEvents.STONE_PLACE, SoundSource.BLOCKS, 1f, 1f);
		MutableComponent msg;
		if (coupe) msg = Component.translatable("airain.cordeau.suite", poses).withStyle(ChatFormatting.GOLD);
		else if (!manque.isEmpty()) {
			msg = Component.translatable("airain.motif.manque", poses).withStyle(ChatFormatting.RED);
			int n = 0;
			for (Map.Entry<Item, Integer> e : manque.entrySet()) {
				if (n++ == 3) { msg.append(", …"); break; }
				msg.append((n > 1 ? ", " : " ") + e.getValue() + " ").append(e.getKey().getDescription());
			}
		} else msg = Component.translatable("airain.motif.pose", poses).withStyle(ChatFormatting.GOLD);
		p.displayClientMessage(msg, true);
		if (!coupe && manque.isEmpty()) Cordeau.effacer(cordeau);
	}

	/** Retire un objet de l'inventaire du joueur (pas le cordeau ni les cartons). */
	private static boolean prendre(ServerPlayer p, Item it) {
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack x = inv.getItem(i);
			if (!x.isEmpty() && x.is(it) && !x.has(DataComponents.CUSTOM_DATA)) { x.shrink(1); return true; }
		}
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack x = inv.getItem(i);
			if (!x.isEmpty() && x.is(it)) { x.shrink(1); return true; }
		}
		return false;
	}
}
