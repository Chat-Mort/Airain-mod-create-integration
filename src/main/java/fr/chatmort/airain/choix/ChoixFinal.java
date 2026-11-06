package fr.chatmort.airain.choix;

import java.util.List;

import fr.chatmort.airain.gardien.Fin;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Le choix final, dans le monde :
 * - à la mort de l'Empereur, sa machine reste là, éteinte, et le Cœur d'Airain s'éteint (dès qu'un joueur le porte) ;
 * - fin Empire : poser le Cœur éteint dans la machine, puis l'allumer avec un cœur du Gardien des enfers ;
 * - fin Écho : poser le Cœur éteint sur le résonateur d'un Grand Relais (magnétite sur ardoise renforcée),
 *   puis frapper avec le diapason d'Ada, un Écho primordial sur soi.
 * Le choix vaut pour tout le monde et ne se fait qu'une fois (voir {@link Fin}).
 */
public final class ChoixFinal {
	private ChoixFinal() {}

	static final ResourceLocation COEUR = id("kubejs", "coeur_d_airain"), ETEINT = id("kubejs", "coeur_eteint"),
		DIAPASON = id("kubejs", "diapason_echo"), ECHO = id("kubejs", "echo_primordial"), EMPEREUR = id("cataclysm", "the_harbinger");
	/** Marque de l'affichage du Cœur posé sur un résonateur. */
	static final String POSE = "airain_coeur_pose";

	private static ResourceLocation id(String ns, String p) { return ResourceLocation.fromNamespaceAndPath(ns, p); }
	private static boolean est(ItemStack s, ResourceLocation r) { return !s.isEmpty() && BuiltInRegistries.ITEM.getKey(s.getItem()).equals(r); }
	/** Le Cœur, éteint ou non (l'ancien Cœur se change de toute façon en Cœur éteint en le portant). */
	static boolean coeur(ItemStack s) { return est(s, ETEINT) || est(s, COEUR); }
	static ItemStack coeurEteint() { return new ItemStack(BuiltInRegistries.ITEM.get(ETEINT)); }

	// ---------------------------------------------------------------- l'Empereur tombe
	public static void mort(LivingDeathEvent e) {
		if (!(e.getEntity().level() instanceof ServerLevel sl) || !BuiltInRegistries.ENTITY_TYPE.getKey(e.getEntity().getType()).equals(EMPEREUR)) return;
		Fin.de(sl.getServer()).empereurTombe();
		// la machine se pose au sol, sous l'endroit où il est tombé, tournée vers le joueur le plus proche
		BlockPos p = e.getEntity().blockPosition();
		for (int k = 0; k < 40 && p.getY() > sl.getMinBuildHeight() && sl.getBlockState(p.below()).canBeReplaced(); k++) p = p.below();
		if (!sl.getBlockState(p).canBeReplaced() || !sl.getBlockState(p.above()).canBeReplaced()) p = p.above();
		var j = sl.getNearestPlayer(e.getEntity(), 64);
		Direction face = j == null ? Direction.NORTH : Direction.getNearest(j.getX() - p.getX(), 0, j.getZ() - p.getZ());
		sl.setBlock(p, fr.chatmort.airain.AirainMod.MACHINE_EMPEREUR.get().defaultBlockState().setValue(MachineEmpereurBlock.FACING, face), 3);
		sl.playSound(null, p, SoundEvents.IRON_GOLEM_DEATH, SoundSource.HOSTILE, 2f, 0.4f);
		for (ServerPlayer q : sl.getServer().getPlayerList().getPlayers()) {   // la voix d'Elias, dans le Cœur qui s'éteint
			q.sendSystemMessage(Component.translatable("airain.choix.elias").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
			q.sendSystemMessage(Component.translatable("airain.choix.indice").withStyle(ChatFormatting.GRAY));
		}
	}

	// ---------------------------------------------------------------- toutes les 2 s : le Cœur s'éteint, les âmes tournent
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 40 != 21) return;
		Fin fin = Fin.de(p.server);
		if (fin.empereurMort()) {
			var inv = p.getInventory();
			for (int i = 0; i < inv.getContainerSize(); i++)
				if (est(inv.getItem(i), COEUR)) { inv.setItem(i, coeurEteint()); p.displayClientMessage(Component.translatable("airain.choix.eteint").withStyle(ChatFormatting.GOLD), true); }
		}
		if (!fin.choix().isEmpty()) return;
		for (Display.ItemDisplay d : poses(p.serverLevel(), p.getBoundingBox().inflate(32)))
			p.serverLevel().sendParticles(ParticleTypes.SOUL, d.getX(), d.getY(), d.getZ(), 6, 0.6, 0.4, 0.6, 0.01);
	}

	private static List<Display.ItemDisplay> poses(ServerLevel l, AABB zone) {
		return l.getEntities(EntityType.ITEM_DISPLAY, zone, d -> d.getTags().contains(POSE));
	}

	// ---------------------------------------------------------------- le résonateur du Grand Relais
	public static void resonateur(PlayerInteractEvent.RightClickBlock e) {
		if (e.getHand() != InteractionHand.MAIN_HAND || !(e.getLevel() instanceof ServerLevel sl) || !(e.getEntity() instanceof ServerPlayer p)) return;
		BlockPos pos = e.getPos();
		if (!sl.getBlockState(pos).is(Blocks.LODESTONE) || !sl.getBlockState(pos.below()).is(Blocks.REINFORCED_DEEPSLATE)) return;
		ItemStack main = p.getMainHandItem();
		List<Display.ItemDisplay> ici = poses(sl, new AABB(pos).inflate(1, 2, 1));
		Fin fin = Fin.de(sl.getServer());
		if (ici.isEmpty() && coeur(main) && fin.choix().isEmpty()) {                 // poser le Cœur
			if (!p.getAbilities().instabuild) main.shrink(1);
			commande(sl, pos, "summon minecraft:item_display ~0.5 ~1.9 ~0.5 {Tags:[\"" + POSE + "\"],billboard:\"vertical\",item:{id:\"" + ETEINT + "\",count:1},brightness:{sky:15,block:15}}");
			sl.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1f, 0.5f);
			p.displayClientMessage(Component.translatable("airain.choix.resonateur.pose"), true);
			annuler(e);
		} else if (!ici.isEmpty() && main.isEmpty()) {                               // le reprendre
			ici.forEach(d -> d.discard());
			p.getInventory().placeItemBackInInventory(coeurEteint());
			annuler(e);
		} else if (!ici.isEmpty() && est(main, DIAPASON)) {                           // frapper : fin Écho
			int k = -1;
			for (int i = 0; i < p.getInventory().getContainerSize() && k < 0; i++) if (est(p.getInventory().getItem(i), ECHO)) k = i;
			if (k < 0 && !p.getAbilities().instabuild) p.displayClientMessage(Component.translatable("airain.choix.resonateur.echo"), true);
			else if (choisir(p, "echo")) {
				if (k >= 0 && !p.getAbilities().instabuild) p.getInventory().getItem(k).shrink(1);
				ici.forEach(d -> d.discard());
				liberer(sl, pos);
			}
			annuler(e);
		}
	}

	private static void annuler(PlayerInteractEvent.RightClickBlock e) {
		e.setCanceled(true);
		e.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
	}

	private static void commande(ServerLevel sl, BlockPos pos, String c) {
		MinecraftServer s = sl.getServer();
		s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withLevel(sl).withPosition(net.minecraft.world.phys.Vec3.atLowerCornerOf(pos))
			.withSuppressedOutput().withPermission(4), c);
	}

	// ---------------------------------------------------------------- le choix
	/** Enregistre la fin, prévient tout le monde, donne les livres et récompenses à chaque joueur, valide les quêtes. */
	static boolean choisir(ServerPlayer auteur, String v) {
		Fin fin = Fin.de(auteur.server);
		if (!fin.enregistrer(v)) {
			auteur.displayClientMessage(Component.translatable("airain.fin.deja", Component.translatable("airain.fin." + fin.choix())), true);
			return false;
		}
		MinecraftServer s = auteur.server;
		for (ServerPlayer q : s.getPlayerList().getPlayers()) {
			for (String r : v.equals("empire") ? new String[] {"airain.choix.empire.1"} : new String[] {"airain.choix.echo.1", "airain.choix.echo.2"})
				q.sendSystemMessage(Component.translatable(r).withStyle(v.equals("empire") ? ChatFormatting.GOLD : ChatFormatting.AQUA, ChatFormatting.ITALIC));
			Fin.recompenser(q, v);
			for (String etape : new String[] {"airain_fin", "airain_fin_" + v})          // quêtes « Le choix final » et la fin choisie
				s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput().withPermission(4),
					"kubejs stages add " + q.getGameProfile().getName() + " " + etape);
		}
		return true;
	}

	/** Fin Empire : la machine repart. */
	static void rallumer(ServerLevel sl, BlockPos pos) {
		sl.playSound(null, pos, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 2f, 0.6f);
		sl.playSound(null, pos, SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 1.5f, 0.5f);
		sl.playSound(null, pos, SoundEvents.FIRECHARGE_USE, SoundSource.BLOCKS, 1.5f, 0.6f);
		sl.sendParticles(ParticleTypes.FLAME, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, 60, 0.6, 0.6, 0.6, 0.05);
		sl.sendParticles(ParticleTypes.CLOUD, pos.getX() + 0.5, pos.getY() + 2, pos.getZ() + 0.5, 80, 0.5, 1.5, 0.5, 0.05);
		sl.sendParticles(ParticleTypes.WAX_ON, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, 40, 1, 1, 1, 0.1);
	}

	/** Fin Écho : une colonne de lumière, et les âmes qui montent. */
	static void liberer(ServerLevel sl, BlockPos pos) {
		sl.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 2f, 0.5f);
		sl.playSound(null, pos, SoundEvents.BELL_RESONATE, SoundSource.BLOCKS, 2f, 0.8f);
		for (int y = 0; y < 40; y += 2) {
			sl.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 2 + y, pos.getZ() + 0.5, 6, 0.25, 1, 0.25, 0.01);
			sl.sendParticles(ParticleTypes.SOUL, pos.getX() + 0.5, pos.getY() + 2 + y, pos.getZ() + 0.5, 8, 1.2, 1, 1.2, 0.03);
		}
	}
}
