package fr.chatmort.airain.chronique;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Les Chroniques oubliées : ce que l'équipe a vécu, partagé par tout le monde.
 * Le récit (débloqué par les quêtes), le journal de bord (noté tout seul), les archives (écrits trouvés).
 * Dans les arguments du journal, « #clé » est un texte à traduire, le reste est littéral.
 */
public class Chronique extends SavedData {
	/** Ordre du récit : les clés débloquées par les quêtes, dans l'ordre de l'histoire. */
	public static final String[] RECIT = {"reveil", "surface", "avant_poste", "atelier", "entretien", "refractaires", "gardien_vent",
		"inscriptions", "marees", "bastion", "capsules", "forge_ames", "station", "gardien_cieux", "cites", "citadelle", "memoires", "coeur",
		"eveil", "colosse", "berceau", "empereur", "fin_empire", "fin_echo",
		"echo_refus", "echo_vael", "echo_ada", "echo_choeur"};

	public record Entree(int jour, String cle, List<String> args) {}

	private final List<Entree> journal = new ArrayList<>();

	/**
	 * Index des archives : camp, auteur, puis les écrits {id airain_doc, clé du titre}, dans l'ordre de lecture.
	 * Les écrits hors index trouvés en jeu s'ajoutent à la fin.
	 */
	public static final String[][][] INDEX = {
		{{"empire", "ferrand"}, {"ferrand1", "airain.ferrand1.titre"}, {"ferrand2", "airain.ferrand2.titre"}, {"ferrand3", "airain.ferrand3.titre"}, {"testament_ferrand", "airain.testament.titre"}},
		{{"empire", "helena"}, {"helena1", "airain.helena1.titre"}, {"helena2", "airain.helena2.titre"}, {"helena3", "airain.helena3.titre"}, {"helena4", "airain.helena4.titre"},
			{"helena5", "airain.helena5.titre"}, {"helena6", "airain.helena6.titre"}, {"helena7", "airain.helena7.titre"}},
		{{"empire", "elias"}, {"elias1", "airain.elias1.titre"}, {"elias2", "airain.elias2.titre"}, {"elias3", "airain.elias3.titre"}, {"elias4", "airain.elias4.titre"}, {"vael", "airain.vael.titre"}},
		{{"empire", "archives"}, {"conseil", "airain.conseil.titre"}, {"station", "airain.station.titre"}, {"essais", "airain.essais.titre"}, {"incident", "airain.relais.titre"},
			{"mine", "airain.mine.titre"}, {"prospecteur", "airain.prospecteur.titre"}, {"cargaison", "airain.cargaison.titre"}, {"nether", "airain.nether.titre"},
			{"profondeurs", "airain.profondeurs.titre"}, {"dirigeable", "airain.dirigeable.titre"}, {"ciel", "airain.ciel.titre"}},
		{{"refractaires", "ada"}, {"ada", "airain.ada.titre"}, {"lettre", "airain.lettre.titre"}, {"ada_morgana", "airain.ada_morgana.titre"}, {"ada_fin", "airain.ada_fin.titre"}},
		{{"refractaires", "morgana"}, {"morgana1", "airain.morgana1.titre"}, {"morgana2", "airain.morgana2.titre"}, {"morgana3", "airain.morgana3.titre"}, {"morgana_note", "airain.morgana.note.titre"}},
		{{"refractaires", "sybille"}, {"apprentie1", "airain.apprentie1.titre"}, {"apprentie2", "airain.apprentie2.titre"}, {"apprentie3", "airain.apprentie3.titre"},
			{"apprentie4", "airain.apprentie4.titre"}, {"apprentie5", "airain.apprentie5.titre"}, {"apprentie6", "airain.apprentie6.titre"}, {"apprentie7", "airain.apprentie7.titre"}},
		{{"refractaires", "camps"}, {"refractaire", "airain.ruine.titre"}, {"cache", "airain.cache.titre"}, {"champ_bataille", "airain.champ_bataille.titre"}, {"abri_nether", "airain.abri_nether.titre"}}};

	private final Set<String> recit = new LinkedHashSet<>();
	private final Set<String> marques = new LinkedHashSet<>();       // « premières fois » déjà notées
	private final List<CompoundTag> archives = new ArrayList<>();
	private final Set<String> docs = new LinkedHashSet<>();
	private final Set<String> auteurs = new LinkedHashSet<>();

	public static Chronique de(MinecraftServer s) {
		return s.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Chronique::new, Chronique::charger, null), "airain_chronique");
	}

	static int jour(MinecraftServer s) { return (int) (s.overworld().getDayTime() / 24000L) + 1; }

	public static String tr(String cle) { return "#" + cle; }

	/** Note une entrée du journal. */
	public static void noter(MinecraftServer s, String cle, String... args) {
		Chronique c = de(s);
		c.journal.add(new Entree(jour(s), cle, List.of(args)));
		c.setDirty();
	}

	/** N'écrit l'entrée qu'une fois pour toute la partie. */
	public static void premiere(MinecraftServer s, String marque, String cle, String... args) {
		Chronique c = de(s);
		if (c.marques.add(marque)) noter(s, cle, args);
	}

	public static void auteur(ServerPlayer p) {
		Chronique c = de(p.server);
		if (c.auteurs.add(p.getGameProfile().getName())) c.setDirty();
	}

	public boolean debloquer(MinecraftServer s, String cle) {
		if (!recit.add(cle)) return false;
		journal.add(new Entree(jour(s), "airain.chronique.j.recit", List.of(tr("airain.chronique.recit." + cle + ".titre"))));
		setDirty();
		return true;
	}

	// ---- événements
	public static void boss(ServerPlayer p, LivingEntity e) {
		auteur(p);
		premiere(p.server, "boss:" + e.getType().getDescriptionId(), "airain.chronique.j.boss", p.getGameProfile().getName(), tr(e.getType().getDescriptionId()));
	}

	public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		String d = e.getTo().location().getPath();
		if (!d.equals("the_nether") && !d.equals("the_end")) return;
		auteur(p);
		premiere(p.server, "dim:" + d, "airain.chronique.j.dim." + d, p.getGameProfile().getName());
	}

	/** Les écrits de l'Empire et des Réfractaires portés dans l'inventaire rejoignent les archives. */
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 100 != 7) return;
		Chronique c = null;
		for (ItemStack s : p.getInventory().items) {
			var cd = s.get(DataComponents.CUSTOM_DATA);
			if (cd == null || !cd.contains("airain_doc")) continue;
			if (c == null) c = de(p.server);
			String doc = cd.copyTag().getString("airain_doc");
			if (!c.docs.add(doc)) continue;
			c.archives.add((CompoundTag) s.copyWithCount(1).save(p.registryAccess()));
			var livre = s.get(DataComponents.WRITTEN_BOOK_CONTENT);
			String titre = livre != null ? livre.title().raw() : s.getHoverName().getString();
			auteur(p);
			noter(p.server, "airain.chronique.j.ecrit", p.getGameProfile().getName(), titre);
		}
	}

	/** Les données envoyées au livre. */
	public CompoundTag paquet(MinecraftServer s) {
		CompoundTag t = save(new CompoundTag(), s.registryAccess());
		t.putInt("aujourdhui", jour(s));
		return t;
	}

	// ---- commandes : /airain chronique recit <clé> | jusqua <clé> | note <clé> [args séparés par |]
	public static LiteralArgumentBuilder<CommandSourceStack> commande() {
		return Commands.literal("chronique")
			.then(Commands.literal("recit").then(Commands.argument("cle", StringArgumentType.word())
				.suggests((c, b) -> { for (String k : RECIT) b.suggest(k); return b.buildFuture(); })
				.executes(c -> {
					String k = StringArgumentType.getString(c, "cle");
					boolean neuf = de(c.getSource().getServer()).debloquer(c.getSource().getServer(), k);
					if (neuf) annoncer(c.getSource().getServer(), k);
					return neuf ? 1 : 0;
				})))
			.then(Commands.literal("jusqua").then(Commands.argument("cle", StringArgumentType.word())
				.suggests((c, b) -> { for (String k : RECIT) b.suggest(k); return b.buildFuture(); })
				.executes(c -> {
					String k = StringArgumentType.getString(c, "cle");
					MinecraftServer s = c.getSource().getServer();
					int n = 0;
					for (String r : RECIT) {
						if (!r.startsWith("fin_") && de(s).debloquer(s, r)) n++;
						if (r.equals(k)) break;
					}
					int f = n;
					c.getSource().sendSuccess(() -> Component.translatable("airain.chronique.rattrape", f), true);
					return n;
				})))
			.then(Commands.literal("note").then(Commands.argument("cle", StringArgumentType.word())
				.executes(c -> { noter(c.getSource().getServer(), "airain.chronique.j." + StringArgumentType.getString(c, "cle")); return 1; })
				.then(Commands.argument("args", StringArgumentType.greedyString()).executes(c -> {
					noter(c.getSource().getServer(), "airain.chronique.j." + StringArgumentType.getString(c, "cle"),
						StringArgumentType.getString(c, "args").split("\\|"));
					return 1;
				}))));
	}

	private static void annoncer(MinecraftServer s, String k) {
		for (ServerPlayer p : s.getPlayerList().getPlayers())
			p.displayClientMessage(Component.translatable("airain.chronique.nouveau", Component.translatable("airain.chronique.recit." + k + ".titre"))
				.withStyle(net.minecraft.ChatFormatting.GOLD), true);
	}

	// ---- sauvegarde
	@Override
	public CompoundTag save(CompoundTag t, HolderLookup.Provider r) {
		ListTag j = new ListTag();
		for (Entree e : journal) {
			CompoundTag c = new CompoundTag();
			c.putInt("jour", e.jour()); c.putString("cle", e.cle());
			ListTag a = new ListTag();
			for (String s : e.args()) a.add(StringTag.valueOf(s));
			c.put("args", a);
			j.add(c);
		}
		t.put("journal", j);
		t.put("recit", liste(recit)); t.put("marques", liste(marques)); t.put("docs", liste(docs)); t.put("auteurs", liste(auteurs));
		ListTag ar = new ListTag();
		ar.addAll(archives);
		t.put("archives", ar);
		return t;
	}

	private static ListTag liste(Set<String> s) {
		ListTag l = new ListTag();
		for (String x : s) l.add(StringTag.valueOf(x));
		return l;
	}

	private static void lire(ListTag l, Set<String> s) { for (Tag x : l) s.add(x.getAsString()); }

	private static Chronique charger(CompoundTag t, HolderLookup.Provider r) {
		Chronique c = new Chronique();
		for (Tag x : t.getList("journal", Tag.TAG_COMPOUND)) {
			CompoundTag e = (CompoundTag) x;
			List<String> a = new ArrayList<>();
			for (Tag y : e.getList("args", Tag.TAG_STRING)) a.add(y.getAsString());
			c.journal.add(new Entree(e.getInt("jour"), e.getString("cle"), a));
		}
		lire(t.getList("recit", Tag.TAG_STRING), c.recit); lire(t.getList("marques", Tag.TAG_STRING), c.marques);
		lire(t.getList("docs", Tag.TAG_STRING), c.docs); lire(t.getList("auteurs", Tag.TAG_STRING), c.auteurs);
		for (Tag x : t.getList("archives", Tag.TAG_COMPOUND)) c.archives.add((CompoundTag) x);
		return c;
	}
}
