package fr.chatmort.airain.fondation;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/** Chaque seconde : affiche le nom de la base quand un joueur entre dans sa zone. */
public final class Fondations {
	private static final Map<UUID, String> derniere = new HashMap<>();

	private Fondations() {}

	public static void tick(ServerTickEvent.Post event) {
		MinecraftServer serveur = event.getServer();
		if (serveur.getTickCount() % 20 != 0) return;
		FondationRegistre reg = FondationRegistre.de(serveur);
		for (ServerPlayer p : serveur.getPlayerList().getPlayers()) {
			FondationRegistre.Fondation f = reg.zone(p.level().dimension().location(), p.getX(), p.getZ());
			String cle = f == null ? "" : f.dim() + "|" + f.pos().asLong();
			String avant = derniere.getOrDefault(p.getUUID(), "");
			if (cle.equals(avant)) continue;
			derniere.put(p.getUUID(), cle);
			if (f != null) {
				net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(p, new TitreFondation(f.nom(), f.devise(), f.apparence(), f.ext()));
			}
		}
	}
}
