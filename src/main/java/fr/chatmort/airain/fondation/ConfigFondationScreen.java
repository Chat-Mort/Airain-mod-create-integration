package fr.chatmort.airain.fondation;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.PacketDistributor;

/** Écran de l'étendard : nom de la base, puis style, couleurs, motif et forme de la bannière, avec un aperçu. */
public class ConfigFondationScreen extends Screen {
	private static final String[] CLES = {"style", "fond", "ornement", "motif", "forme"};
	private static final int[] TAILLES = {Apparence.STYLES, Apparence.FONDS.length, Apparence.ORNEMENTS.length, Apparence.MOTIFS.length, Apparence.FORMES.length};
	private final BlockPos pos;
	private final String nomActuel;
	private final int[] choix;
	private EditBox champ;

	public ConfigFondationScreen(BlockPos pos, String nom, Apparence a) {
		super(Component.translatable("airain.fondation.ecran"));
		this.pos = pos; this.nomActuel = nom;
		this.choix = new int[] {a.style(), a.fond(), a.ornement(), a.motif(), a.forme()};
	}

	private Apparence apparence() {
		return new Apparence(choix[0], choix[1], choix[2], choix[3], choix[4]);
	}

	@Override
	protected void init() {
		int x = width / 2 - 150, y = height / 2 - 90;
		champ = new EditBox(font, x, y + 14, 190, 20, Component.translatable("airain.fondation.ecran"));
		champ.setMaxLength(32); champ.setValue(nomActuel);
		addRenderableWidget(champ); setInitialFocus(champ);
		for (int k = 0; k < CLES.length; k++) {
			final int i = k;
			int ly = y + 48 + k * 24;
			addRenderableWidget(Button.builder(Component.literal("<"), b -> choix[i] = Math.floorMod(choix[i] - 1, TAILLES[i])).bounds(x + 80, ly, 20, 20).build());
			addRenderableWidget(Button.builder(Component.literal(">"), b -> choix[i] = Math.floorMod(choix[i] + 1, TAILLES[i])).bounds(x + 170, ly, 20, 20).build());
		}
		addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> valider()).bounds(x, y + 172, 94, 20).build());
		addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), b -> onClose()).bounds(x + 96, y + 172, 94, 20).build());
	}

	private void valider() {
		PacketDistributor.sendToServer(new ConfigurerFondation(pos, champ.getValue().trim(), apparence().pack()));
		onClose();
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if ((key == 257 || key == 335) && champ.isFocused()) { valider(); return true; }
		return super.keyPressed(key, scan, mods);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = width / 2 - 150, y = height / 2 - 90;
		g.drawString(font, title, x, y, 0xE8C878);
		for (int k = 0; k < CLES.length; k++) {
			int ly = y + 48 + k * 24;
			g.drawString(font, Component.translatable("airain.etendard." + CLES[k]), x, ly + 6, 0xD0C8B0);
			g.drawCenteredString(font, Component.translatable("airain.etendard." + CLES[k] + "." + choix[k]), x + 135, ly + 6, 0xFFFFFF);
		}
		// aperçu de la bannière (calques teintés)
		Apparence a = apparence();
		int px = x + 220, py = y + 14;
		g.fill(px - 6, py - 6, px + 70, py + 138, 0x80101010);
		RenderSystem.enableBlend();
		dessiner(g, a.texFond(), Apparence.FONDS[a.fond()], px, py);
		if (a.texMotif() != null) dessiner(g, a.texMotif(), Apparence.ORNEMENTS[a.ornement()], px, py);
		dessiner(g, a.texOrnement(), Apparence.ORNEMENTS[a.ornement()], px, py);
		RenderSystem.setShaderColor(1, 1, 1, 1);
	}

	private static void dessiner(GuiGraphics g, ResourceLocation tex, int c, int x, int y) {
		RenderSystem.setShaderColor((c >> 16 & 255) / 255f, (c >> 8 & 255) / 255f, (c & 255) / 255f, 1f);
		g.blit(tex, x, y, 64, 128, 0f, 0f, 16, 32, 16, 32);
	}

	@Override
	public boolean isPauseScreen() { return false; }
}
