package fr.chatmort.airain.armure;

/** Les deux lignées d'équipement de fin de partie : chacune n'est servie que par sa fin. */
public enum Lignee {
	EMPIRE, ECHO;

	/** La fin choisie autorise-t-elle cette lignée ? */
	public boolean autorisee(net.minecraft.server.MinecraftServer srv) {
		var f = fr.chatmort.airain.gardien.Fin.de(srv);
		return this == EMPIRE ? f.empire() : f.echo();
	}

	public String cle() { return this == EMPIRE ? "empire" : "echo"; }
}
