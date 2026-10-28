package fr.chatmort.airain.fondation;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.network.PacketDistributor;

/** Saisie du nom de la base. */
public class NomFondationScreen extends Screen {
	private final BlockPos pos;
	private final String actuel;
	private EditBox champ;

	public NomFondationScreen(BlockPos pos, String actuel) {
		super(Component.translatable("airain.fondation.ecran"));
		this.pos = pos; this.actuel = actuel;
	}

	@Override
	protected void init() {
		int x = width / 2 - 100, y = height / 2 - 10;
		champ = new EditBox(font, x, y, 200, 20, Component.translatable("airain.fondation.ecran"));
		champ.setMaxLength(32); champ.setValue(actuel);
		addRenderableWidget(champ); setInitialFocus(champ);
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 28, 98, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 102, y + 28, 98, 20).build());
	}

	private void valider() {
		String n = champ.getValue().trim();
		if (!n.isEmpty()) PacketDistributor.sendToServer(new NommerFondation(pos, n));
		onClose();
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key == 257 || key == 335) { valider(); return true; }   // Entrée
		return super.keyPressed(key, scan, mods);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		g.drawCenteredString(font, title, width / 2, height / 2 - 34, 0xE8C878);
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
