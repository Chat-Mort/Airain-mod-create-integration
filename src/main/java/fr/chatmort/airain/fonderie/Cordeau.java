package fr.chatmort.airain.fonderie;

import java.util.ArrayList;
import java.util.List;

import fr.chatmort.airain.AirainMod;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * 1.69.1 : le cordeau de maçon. Deux piquets A et B, puis la pose du bloc tenu dans l'autre main
 * en ligne (64 au plus) ou en plan (16 × 16 au plus), plein ou en contour. Seules les cases vides sont remplies.
 * Le jeu du joueur décide de l'action (il voit Ctrl et la case visée) et l'envoie au serveur, qui vérifie et pose.
 */
public final class Cordeau {
	private Cordeau() {}

	// 1.69.9 : volumes (accroupi + molette) ; côtés jusqu'à 32, 16 384 cases au plus, 4 096 blocs posés par clic
	public static final int LIGNE_MAX = 64, COTE_MAX = 32, VOLUME_MAX = 32 * 32 * 16, POSE_MAX = 4096, PORTEE = 10;
	static final String A = "airain_cordeau_a", B = "airain_cordeau_b", CONTOUR = "airain_cordeau_contour", DIM = "airain_cordeau_dim";

	public static final DeferredItem<Item> CORDEAU = AirainMod.ITEMS.register("chalk_line", () -> new Objet(new Item.Properties().stacksTo(1)));

	public static void charger() {}

	public static class Objet extends Item {
		Objet(Properties p) { super(p); }

		// toute la décision se prend côté client (Ctrl, case visée) ; le serveur ne fait rien ici et attend le paquet
		@Override
		public InteractionResult useOn(UseOnContext c) {
			if (c.getLevel().isClientSide && FMLEnvironment.dist.isClient())
				CordeauClient.clic(c.getHand(), new BlockHitResult(c.getClickLocation(), c.getClickedFace(), c.getClickedPos(), c.isInside()));
			return InteractionResult.SUCCESS;
		}

		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand main) {
			if (level.isClientSide && FMLEnvironment.dist.isClient()) CordeauClient.clic(main, null);
			return InteractionResultHolder.success(p.getItemInHand(main));
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext c, List<Component> l, TooltipFlag f) {
			l.add(Component.translatable(contour(s) ? "airain.cordeau.mode_contour" : "airain.cordeau.mode_plein").withStyle(ChatFormatting.GOLD));
			l.add(Component.translatable("airain.cordeau.aide_bloc").withStyle(ChatFormatting.GRAY));
			l.add(Component.translatable("airain.cordeau.aide_points").withStyle(ChatFormatting.GRAY));
			l.add(Component.translatable("airain.cordeau.aide_mode").withStyle(ChatFormatting.GRAY));
		}

	}

	// ------------------------------------------------------------------ données portées par l'objet
	private static net.minecraft.nbt.CompoundTag tag(ItemStack s) { CustomData d = s.get(DataComponents.CUSTOM_DATA); return d == null ? new net.minecraft.nbt.CompoundTag() : d.copyTag(); }
	public static BlockPos a(ItemStack s, Level l) { var t = tag(s); return t.contains(A) && t.getString(DIM).equals(l.dimension().location().toString()) ? BlockPos.of(t.getLong(A)) : null; }
	public static BlockPos b(ItemStack s, Level l) { var t = tag(s); return t.contains(B) && t.getString(DIM).equals(l.dimension().location().toString()) ? BlockPos.of(t.getLong(B)) : null; }
	public static boolean contour(ItemStack s) { return tag(s).getBoolean(CONTOUR); }
	static void effacer(ItemStack s) { CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.remove(A); t.remove(B); t.remove(DIM); }); }

	/** La case où irait le bloc : la case visée si elle se remplace (herbe, eau…), sinon celle devant la face visée. */
	public static BlockPos cellule(Level l, BlockHitResult h) {
		return l.getBlockState(h.getBlockPos()).canBeReplaced() ? h.getBlockPos() : h.getBlockPos().relative(h.getDirection());
	}

	/** La sélection entre A et B est-elle acceptable ? Ligne : 64 ; sinon côtés de 32 au plus et 16 384 cases. */
	public static boolean valide(BlockPos a, BlockPos b) {
		int dx = Math.abs(a.getX() - b.getX()), dy = Math.abs(a.getY() - b.getY()), dz = Math.abs(a.getZ() - b.getZ());
		int axes = (dx > 0 ? 1 : 0) + (dy > 0 ? 1 : 0) + (dz > 0 ? 1 : 0);
		if (axes <= 1) return Math.max(dx, Math.max(dy, dz)) + 1 <= LIGNE_MAX;
		return dx < COTE_MAX && dy < COTE_MAX && dz < COTE_MAX && (long) (dx + 1) * (dy + 1) * (dz + 1) <= VOLUME_MAX;
	}

	/** Les cases entre A et B (ligne, plan ou volume ; contour = le bord du plan ou l'enveloppe du volume), ou null si c'est trop grand. */
	public static List<BlockPos> cases(BlockPos a, BlockPos b, boolean contour) {
		int dx = Math.abs(a.getX() - b.getX()), dy = Math.abs(a.getY() - b.getY()), dz = Math.abs(a.getZ() - b.getZ());
		int axes = (dx > 0 ? 1 : 0) + (dy > 0 ? 1 : 0) + (dz > 0 ? 1 : 0);
		if (!valide(a, b)) return null;
		List<BlockPos> r = new ArrayList<>();
		int x0 = Math.min(a.getX(), b.getX()), y0 = Math.min(a.getY(), b.getY()), z0 = Math.min(a.getZ(), b.getZ());
		for (int x = x0; x <= x0 + dx; x++)
			for (int y = y0; y <= y0 + dy; y++)
				for (int z = z0; z <= z0 + dz; z++) {
					// contour : seulement le bord du plan, ou l'enveloppe du volume
					if (contour && axes >= 2) {
						boolean bord = (dx > 0 && (x == x0 || x == x0 + dx)) || (dy > 0 && (y == y0 || y == y0 + dy)) || (dz > 0 && (z == z0 || z == z0 + dz));
						if (!bord) continue;
					}
					r.add(new BlockPos(x, y, z));
				}
		return r;
	}

	/** « Line: 5 blocks », « Floor 5 × 3: 15 blocks (fill) », « Wall 5 × 3: 12 blocks (outline) ». */
	public static MutableComponent forme(BlockPos a, BlockPos b, boolean contour) {
		List<BlockPos> c = cases(a, b, contour);
		int dx = Math.abs(a.getX() - b.getX()) + 1, dy = Math.abs(a.getY() - b.getY()) + 1, dz = Math.abs(a.getZ() - b.getZ()) + 1;
		int axes = (dx > 1 ? 1 : 0) + (dy > 1 ? 1 : 0) + (dz > 1 ? 1 : 0);
		if (c == null) return Component.translatable("airain.cordeau.trop", LIGNE_MAX, COTE_MAX);
		if (axes <= 1) return Component.translatable("airain.cordeau.forme.ligne", c.size());
		MutableComponent m = axes == 3 ? Component.translatable("airain.cordeau.forme.volume", dx, dy, dz, c.size())
			: dy == 1 ? Component.translatable("airain.cordeau.forme.sol", dx, dz, c.size())
			: Component.translatable("airain.cordeau.forme.mur", dx > 1 ? dx : dz, dy, c.size());
		return m.append(Component.translatable(contour ? "airain.cordeau.contour" : "airain.cordeau.plein"));
	}

	// ------------------------------------------------------------------ actions (paquet client -> serveur)
	public static final int POINT = 0, POSER = 1, ANNULER = 2, MODE = 3, TAILLE = 4;   // TAILLE : pos = (face, +1 ou -1, 0)

	public record Action(int quoi, BlockPos pos, boolean mainPrincipale) implements CustomPacketPayload {
		public static final Type<Action> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("airain", "cordeau_action"));
		public static final StreamCodec<RegistryFriendlyByteBuf, Action> CODEC = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, Action::quoi, BlockPos.STREAM_CODEC, Action::pos, ByteBufCodecs.BOOL, Action::mainPrincipale, Action::new);
		@Override public Type<? extends CustomPacketPayload> type() { return TYPE; }

		public static void traiter(Action m, IPayloadContext ctx) {
			ctx.enqueueWork(() -> {
				if (!(ctx.player() instanceof ServerPlayer p)) return;
				InteractionHand main = m.mainPrincipale() ? InteractionHand.MAIN_HAND : InteractionHand.OFF_HAND;
				ItemStack s = p.getItemInHand(main);
				ServerLevel sl = p.serverLevel();
				// 1.69.9 : le carton de motif passe par le même paquet
				if (s.is(Motif.CARTON.get())) { Motif.action(m, p, sl, s); return; }
				if (!s.is(CORDEAU.get())) return;
				ItemStack autre = p.getItemInHand(main == InteractionHand.MAIN_HAND ? InteractionHand.OFF_HAND : InteractionHand.MAIN_HAND);
				switch (m.quoi()) {
					case MODE -> {
						// carton dans l'autre main : accroupi + clic droit tourne le motif
						if (autre.is(Motif.CARTON.get()) && Motif.enregistre(autre)) { Motif.tourner(p, sl, autre); return; }
						boolean c = !contour(s);
						CustomData.update(DataComponents.CUSTOM_DATA, s, t -> t.putBoolean(CONTOUR, c));
						p.displayClientMessage(Component.translatable(c ? "airain.cordeau.mode_contour" : "airain.cordeau.mode_plein").withStyle(ChatFormatting.GOLD), true);
						sl.playSound(null, p.blockPosition(), SoundEvents.SPYGLASS_USE, SoundSource.PLAYERS, 0.7f, 1.4f);
					}
					case ANNULER -> {
						effacer(s);
						p.displayClientMessage(Component.translatable("airain.cordeau.annule").withStyle(ChatFormatting.GRAY), true);
					}
					case POINT -> point(p, sl, s, m.pos());
					case POSER -> { if (autre.is(Motif.CARTON.get()) && Motif.enregistre(autre)) Motif.poser(p, sl, s, autre); else poser(p, sl, s, main); }
					case TAILLE -> {
						BlockPos a = a(s, sl), b = b(s, sl);
						if (a == null || b == null || m.pos().getX() < 0 || m.pos().getX() > 5) return;
						BlockPos[] n = agrandir(a, b, Direction.from3DDataValue(m.pos().getX()), m.pos().getY() > 0 ? 1 : -1);
						if (n == null || !valide(n[0], n[1])) return;
						CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.putLong(A, n[0].asLong()); t.putLong(B, n[1].asLong()); });
						MutableComponent f = autre.is(Motif.CARTON.get()) && Motif.enregistre(autre) ? Motif.forme(n[0], n[1], autre, sl) : forme(n[0], n[1], contour(s));
						p.displayClientMessage(f.withStyle(ChatFormatting.GOLD), true);
					}
					default -> {}
				}
			});
		}
	}

	private static void point(ServerPlayer p, ServerLevel sl, ItemStack s, BlockPos c) {
		if (c.distToCenterSqr(p.getEyePosition()) > PORTEE * PORTEE || !sl.isLoaded(c)) return;
		BlockPos a = a(s, sl);
		String dim = sl.dimension().location().toString();
		if (a == null || b(s, sl) != null) {
			CustomData.update(DataComponents.CUSTOM_DATA, s, t -> { t.putLong(A, c.asLong()); t.remove(B); t.putString(DIM, dim); });
			p.displayClientMessage(Component.translatable("airain.cordeau.point_a").withStyle(ChatFormatting.GOLD), true);
		} else {
			if (!valide(a, c)) { p.displayClientMessage(forme(a, c, contour(s)).withStyle(ChatFormatting.RED), true); return; }
			CustomData.update(DataComponents.CUSTOM_DATA, s, t -> t.putLong(B, c.asLong()));
			p.displayClientMessage(forme(a, c, contour(s)).append(Component.translatable("airain.cordeau.suite_poser")).withStyle(ChatFormatting.GOLD), true);
		}
		sl.playSound(null, c, SoundEvents.LEASH_KNOT_PLACE, SoundSource.PLAYERS, 0.8f, 1.2f);
	}

	private static void poser(ServerPlayer p, ServerLevel sl, ItemStack s, InteractionHand main) {
		BlockPos a = a(s, sl), b = b(s, sl);
		if (a == null || b == null) return;
		List<BlockPos> cs = cases(a, b, contour(s));
		if (cs == null) return;
		InteractionHand autre = main == InteractionHand.MAIN_HAND ? InteractionHand.OFF_HAND : InteractionHand.MAIN_HAND;
		ItemStack modele = p.getItemInHand(autre);
		if (!(modele.getItem() instanceof BlockItem)) { p.displayClientMessage(Component.translatable("airain.cordeau.sans_bloc").withStyle(ChatFormatting.RED), true); return; }
		Component nom = modele.getHoverName();
		ItemStack type = modele.copyWithCount(1);
		int poses = 0, manque = 0;
		for (BlockPos c : cs) {
			if (poses >= POSE_MAX) { manque = -1; break; }   // 1.69.9 : 4 096 par clic, un autre clic continue
			if (!sl.isLoaded(c) || !sl.getBlockState(c).canBeReplaced() || !sl.mayInteract(p, c)) continue;
			if (!sl.getEntities((net.minecraft.world.entity.Entity) null, new net.minecraft.world.phys.AABB(c), e -> e.blocksBuilding).isEmpty()) continue;
			ItemStack pile = source(p, type, autre);
			if (pile == null) { manque++; continue; }
			// face visée : celle tournée vers le joueur, pour que marches et bûches s'orientent comme à la main
			Vec3 v = p.getEyePosition().subtract(Vec3.atCenterOf(c));
			Direction face = Direction.getNearest(v.x, v.y, v.z);
			BlockPlaceContext ctx = new BlockPlaceContext(sl, p, autre, pile, new BlockHitResult(Vec3.atCenterOf(c), face, c, false));
			int avant = pile.getCount();
			InteractionResult r = ((BlockItem) pile.getItem()).place(ctx);
			if (r.consumesAction()) { poses++; if (p.getAbilities().instabuild) pile.setCount(avant); }
		}
		if (poses > 0) sl.playSound(null, b, sl.getBlockState(b).getSoundType(sl, b, p).getPlaceSound(), SoundSource.BLOCKS, 1f, 1f);
		Component msg = manque < 0 ? Component.translatable("airain.cordeau.suite", poses).withStyle(ChatFormatting.GOLD)
			: manque > 0 ? Component.translatable("airain.cordeau.manque", poses, nom, manque).withStyle(ChatFormatting.RED)
			: Component.translatable("airain.cordeau.pose", poses, nom).withStyle(ChatFormatting.GOLD);
		p.displayClientMessage(msg, true);
		if (manque == 0) effacer(s);   // s'il manque des blocs, les piquets restent : on complète après avoir refait le plein
	}

	/** Une pile du bloc à poser : l'autre main d'abord, puis l'inventaire (infini en créatif). */
	private static ItemStack source(ServerPlayer p, ItemStack type, InteractionHand autre) {
		ItemStack m = p.getItemInHand(autre);
		if (ItemStack.isSameItemSameComponents(m, type) && (!m.isEmpty())) return m;
		for (ItemStack i : p.getInventory().items) if (!i.isEmpty() && ItemStack.isSameItemSameComponents(i, type)) return i;
		if (p.getAbilities().instabuild) return type.copy();
		return null;
	}

	/**
	 * 1.69.9 : accroupi + molette. La face de la sélection tournée vers d avance (delta = +1) ou recule (-1) d'un bloc ;
	 * jamais sous un bloc d'épaisseur. Rend les deux nouveaux coins (dans l'ordre A, B), ou null si rien ne bouge.
	 */
	public static BlockPos[] agrandir(BlockPos a, BlockPos b, Direction d, int delta) {
		Direction.Axis ax = d.getAxis();
		int ca = a.get(ax), cb = b.get(ax);
		boolean positif = d.getAxisDirection() == Direction.AxisDirection.POSITIVE;
		if (delta < 0 && ca == cb) return null;
		// le coin qui porte la face visée : le plus grand vers les +, le plus petit vers les - (B si les deux sont au même niveau)
		boolean surA = ca != cb && (positif ? ca > cb : ca < cb);
		int pas = positif ? delta : -delta;
		return new BlockPos[] {surA ? a.relative(ax, pas) : a, surA ? b : b.relative(ax, pas)};
	}
}
