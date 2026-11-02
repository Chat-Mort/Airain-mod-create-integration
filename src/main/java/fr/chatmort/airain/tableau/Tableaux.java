package fr.chatmort.airain.tableau;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import fr.chatmort.airain.fondation.FondationRegistre;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/** Les tableaux de service : leurs notes, gardées pour tout le monde même quand la base n'est pas chargée. */
public class Tableaux extends SavedData {
	public static final int NOTES = 6, LIGNES = 4, LONGUEUR = 26;

	public static final class Note {
		public int id, couleur, jour;
		public boolean fait;
		public String texte = "", auteur = "";
		public final Set<String> lus = new LinkedHashSet<>();

		CompoundTag save() {
			CompoundTag t = new CompoundTag();
			t.putInt("id", id); t.putInt("couleur", couleur); t.putInt("jour", jour); t.putBoolean("fait", fait);
			t.putString("texte", texte); t.putString("auteur", auteur);
			ListTag l = new ListTag();
			for (String s : lus) l.add(StringTag.valueOf(s));
			t.put("lus", l);
			return t;
		}

		static Note load(CompoundTag t) {
			Note n = new Note();
			n.id = t.getInt("id"); n.couleur = t.getInt("couleur"); n.jour = t.getInt("jour"); n.fait = t.getBoolean("fait");
			n.texte = t.getString("texte"); n.auteur = t.getString("auteur");
			for (Tag x : t.getList("lus", Tag.TAG_STRING)) n.lus.add(x.getAsString());
			return n;
		}
	}

	public static final class Tableau {
		public ResourceLocation dim; public BlockPos pos;
		public final List<Note> notes = new ArrayList<>();
		public int suivant = 1;
	}

	private final Map<String, Tableau> tableaux = new LinkedHashMap<>();

	public static Tableaux de(MinecraftServer s) {
		return s.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Tableaux::new, Tableaux::charger, null), "airain_tableaux");
	}

	public Tableau tableau(ResourceLocation dim, BlockPos pos) {
		return tableaux.computeIfAbsent(FondationRegistre.cle(dim, pos), k -> { Tableau t = new Tableau(); t.dim = dim; t.pos = pos.immutable(); return t; });
	}

	public void retirer(ResourceLocation dim, BlockPos pos) {
		if (tableaux.remove(FondationRegistre.cle(dim, pos)) != null) setDirty();
	}

	/** Le nom de la base où est le tableau (sinon « Tableau de service »). */
	public static Component nomBase(MinecraftServer s, ResourceLocation dim, BlockPos pos) {
		FondationRegistre.Fondation f = FondationRegistre.de(s).zone(dim, pos.getX() + 0.5, pos.getZ() + 0.5);
		return f == null || f.nom().isEmpty() ? Component.translatable("airain.tableau.sans_base") : Component.literal(f.nom());
	}

	/** Notes laissées par les autres et pas encore lues par ce joueur, toutes bases confondues. */
	public List<Note> nonLues(String joueur) {
		List<Note> l = new ArrayList<>();
		for (Tableau t : tableaux.values()) for (Note n : t.notes) if (!n.fait && !n.auteur.equals(joueur) && !n.lus.contains(joueur)) l.add(n);
		return l;
	}

	public static void connexion(PlayerEvent.PlayerLoggedInEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		Tableaux t = de(p.server);
		String nom = p.getGameProfile().getName();
		for (Tableau tb : t.tableaux.values()) {
			long n = tb.notes.stream().filter(x -> !x.fait && !x.auteur.equals(nom) && !x.lus.contains(nom)).count();
			if (n > 0) p.sendSystemMessage(Component.translatable("airain.tableau.nouvelles", n, nomBase(p.server, tb.dim, tb.pos))
				.withStyle(net.minecraft.ChatFormatting.GOLD));
		}
	}

	@Override
	public CompoundTag save(CompoundTag tag, HolderLookup.Provider r) {
		ListTag l = new ListTag();
		for (Tableau t : tableaux.values()) {
			CompoundTag c = new CompoundTag();
			c.putString("dim", t.dim.toString()); c.putLong("pos", t.pos.asLong()); c.putInt("suivant", t.suivant);
			ListTag n = new ListTag();
			for (Note x : t.notes) n.add(x.save());
			c.put("notes", n);
			l.add(c);
		}
		tag.put("tableaux", l);
		return tag;
	}

	private static Tableaux charger(CompoundTag tag, HolderLookup.Provider r) {
		Tableaux s = new Tableaux();
		for (Tag x : tag.getList("tableaux", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) x;
			Tableau t = new Tableau();
			t.dim = ResourceLocation.parse(c.getString("dim")); t.pos = BlockPos.of(c.getLong("pos")); t.suivant = c.getInt("suivant");
			for (Tag y : c.getList("notes", Tag.TAG_COMPOUND)) t.notes.add(Note.load((CompoundTag) y));
			s.tableaux.put(FondationRegistre.cle(t.dim, t.pos), t);
		}
		return s;
	}
}
