package fr.chatmort.airain.manuel;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Les deux manuels d'armes : le Règlement des armes de l'Empire et le Traité des armes de l'Écho.
 * Une page par arme, par coiffe et par ensemble d'armure. Une page se dévoile dès qu'un joueur de l'équipe
 * a porté l'objet (ou une pièce de l'ensemble) sur lui ; avant, elle reste « ?????????? ».
 * Les découvertes sont communes à toute l'équipe et gardées avec le monde.
 */
public class Manuel extends SavedData {
	/** Les deux camps : 0 = Empire, 1 = Écho. */
	public static final int EMPIRE = 0, ECHO = 1;

	/** Une page : sa clé de texte (airain.manuel.<cle>.*), sa section dans le livre, et les objets qui la dévoilent. */
	public record Entree(String cle, int camp, String section, String... objets) {
		/** Page d'ensemble d'armure (plusieurs pièces) plutôt que d'un seul objet. */
		public boolean ensemble() { return objets.length > 1; }
	}

	public static final List<Entree> ENTREES = new ArrayList<>();
	private static void e(int camp, String section, String cle, String... objets) { ENTREES.add(new Entree(cle, camp, section, objets)); }
	static {
		// ---- Règlement des armes de l'Empire
		e(EMPIRE, "sacrees", "sacred_sword", "airain:sacred_sword");
		e(EMPIRE, "sacrees", "sacred_katana", "airain:sacred_katana");
		e(EMPIRE, "sacrees", "sacred_greatsword", "airain:sacred_greatsword");
		e(EMPIRE, "sacrees", "sacred_twinblade", "airain:sacred_twinblade");
		e(EMPIRE, "sacrees", "sacred_pickaxe", "airain:sacred_pickaxe");
		e(EMPIRE, "imperiales", "imperial_sword", "airain:imperial_sword");
		e(EMPIRE, "imperiales", "imperial_katana", "airain:imperial_katana");
		e(EMPIRE, "imperiales", "imperial_greatsword", "airain:imperial_greatsword");
		e(EMPIRE, "imperiales", "imperial_twinblade", "airain:imperial_twinblade");
		e(EMPIRE, "imperiales", "imperial_pickaxe", "airain:imperial_pickaxe");
		e(EMPIRE, "imperiales", "imperial_scepter", "airain:imperial_scepter");
		e(EMPIRE, "coiffes_empire", "airain_crown", "airain:airain_crown");
		e(EMPIRE, "coiffes_empire", "crowned_helmet", "airain:crowned_helmet");
		e(EMPIRE, "coiffes_empire", "sacred_crown", "airain:sacred_crown");
		e(EMPIRE, "coiffes_empire", "imperial_helmet", "airain:imperial_helmet");
		e(EMPIRE, "armures_empire", "set_sacred", "airain:sacred_crown", "airain:sacred_chestplate", "airain:sacred_leggings", "airain:sacred_boots");
		e(EMPIRE, "armures_empire", "set_imperial", "airain:imperial_helmet", "airain:imperial_chestplate", "airain:imperial_leggings", "airain:imperial_boots");
		// ---- Traité des armes de l'Écho
		e(ECHO, "runiques", "runic_sword", "airain:runic_sword");
		e(ECHO, "runiques", "runic_katana", "airain:runic_katana");
		e(ECHO, "runiques", "runic_greatsword", "airain:runic_greatsword");
		e(ECHO, "runiques", "runic_twinblade", "airain:runic_twinblade");
		e(ECHO, "runiques", "runic_pickaxe", "airain:runic_pickaxe");
		e(ECHO, "arcaniques", "arcane_sword", "airain:arcane_sword");
		e(ECHO, "arcaniques", "arcane_katana", "airain:arcane_katana");
		e(ECHO, "arcaniques", "arcane_greatsword", "airain:arcane_greatsword");
		e(ECHO, "arcaniques", "arcane_twinblade", "airain:arcane_twinblade");
		e(ECHO, "arcaniques", "arcane_pickaxe", "airain:arcane_pickaxe");
		e(ECHO, "arcaniques", "arcane_scepter", "airain:arcane_scepter");
		e(ECHO, "coiffes_echo", "echo_diadem", "airain:echo_diadem");
		e(ECHO, "coiffes_echo", "diadem_helmet", "airain:diadem_helmet");
		e(ECHO, "coiffes_echo", "runic_helmet", "airain:runic_helmet");
		e(ECHO, "coiffes_echo", "arcane_helmet", "airain:arcane_helmet");
		e(ECHO, "armures_echo", "set_runic", "airain:runic_helmet", "airain:runic_chestplate", "airain:runic_leggings", "airain:runic_boots");
		e(ECHO, "armures_echo", "set_arcane", "airain:arcane_helmet", "airain:arcane_chestplate", "airain:arcane_leggings", "airain:arcane_boots");
	}

	/** Objets déjà portés par un joueur de l'équipe (identifiants). */
	private final Set<String> vus = new LinkedHashSet<>();

	public static Manuel de(MinecraftServer s) {
		return s.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(Manuel::new, Manuel::charger, null), "airain_manuel");
	}

	/** Pages dévoilées : les clés des entrées dont au moins un objet a été vu. */
	public List<String> devoilees() {
		List<String> l = new ArrayList<>();
		for (Entree en : ENTREES) for (String o : en.objets()) if (vus.contains(o)) { l.add(en.cle()); break; }
		return l;
	}

	/** Toutes les 5 s : regarde l'inventaire et l'équipement de chaque joueur ; une nouvelle page est annoncée. */
	public static void tick(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 100 != 13) return;
		Manuel m = null;
		List<ItemStack> piles = new ArrayList<>(p.getInventory().items);
		for (EquipmentSlot s : EquipmentSlot.values()) piles.add(p.getItemBySlot(s));
		for (ItemStack s : piles) {
			if (s.isEmpty()) continue;
			String id = BuiltInRegistries.ITEM.getKey(s.getItem()).toString();
			if (!id.startsWith("airain:")) continue;
			for (Entree en : ENTREES) {
				if (!java.util.Arrays.asList(en.objets()).contains(id)) continue;
				if (m == null) m = de(p.server);
				boolean avant = m.devoilees().contains(en.cle());
				if (m.vus.add(id)) m.setDirty();
				if (!avant && m.devoilees().contains(en.cle()))   // nouvelle page dans l'un des deux manuels
					for (ServerPlayer q : p.server.getPlayerList().getPlayers())
						q.displayClientMessage(Component.translatable("airain.manuel.nouvelle_page",
							Component.translatable("item.airain." + (en.camp() == EMPIRE ? "imperial_arms_regulations" : "echo_arms_treatise")),
							Component.translatable("airain.manuel." + en.cle() + ".titre")).withStyle(net.minecraft.ChatFormatting.GOLD), true);
			}
		}
	}

	@Override
	public CompoundTag save(CompoundTag t, HolderLookup.Provider r) {
		ListTag l = new ListTag();
		for (String v : vus) l.add(StringTag.valueOf(v));
		t.put("vus", l);
		return t;
	}

	private static Manuel charger(CompoundTag t, HolderLookup.Provider r) {
		Manuel m = new Manuel();
		for (Tag v : t.getList("vus", Tag.TAG_STRING)) m.vus.add(v.getAsString());
		return m;
	}
}
