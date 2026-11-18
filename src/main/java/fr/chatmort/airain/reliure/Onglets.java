package fr.chatmort.airain.reliure;

import java.util.List;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.inventory.CreativeModeInventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.ScreenEvent;

/**
 * Sur l'écran d'un sac (ou de tout conteneur) qui contient une Reliure : ses livres en onglets à gauche.
 * N'utilise que l'API de Minecraft : si un mod de sac change son écran, les onglets disparaissent, rien ne casse.
 */
public final class Onglets {
	private Onglets() {}

	private record Trouvee(int slot, List<ItemStack> livres) {}

	private static Trouvee chercher(AbstractContainerScreen<?> e) {
		if (e instanceof CreativeModeInventoryScreen) return null;
		var slots = e.getMenu().slots;
		for (int i = 0; i < slots.size(); i++) {
			ItemStack s = slots.get(i).getItem();
			if (Reliure.est(s)) return new Trouvee(i, Reliure.livres(s));
		}
		return null;
	}

	// 4 onglets au plus par colonne (à hauteur de l'inventaire du joueur) ; les suivants dans une colonne plus à gauche
	private static final int PAR_COLONNE = 4;
	/** Plaques d'airain de l'interface HD (22x19, normale et survolée), présentes seulement dans le pack. */
	private static final net.minecraft.resources.ResourceLocation PLAQUE = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("airain", "textures/gui/book_tab.png");

	private static int[] place(AbstractContainerScreen<?> e, int n, int i) {
		int parCol = Math.min(n, PAR_COLONNE);
		int c = i / PAR_COLONNE, r = i % PAR_COLONNE;
		// collé au cadre (− 21) ; chaque colonne suivante 18 px plus à gauche : son côté ouvert recouvre le bord arrondi
		// de la précédente, les plaques d'une rangée n'en font qu'une
		int x = e.getGuiLeft() - 21 - c * 18;
		int y = e.getGuiTop() + e.getYSize() - 6 - (parCol - r) * 20;
		return new int[] {x, y};
	}

	/** Survol d'un onglet : ses 4 px de gauche sont sous l'onglet de la colonne suivante quand il y en a un sur la rangée. */
	private static boolean sous(int n, int i, int[] p, double mx, double my) {
		int x0 = p[0] + (i + PAR_COLONNE < n ? 4 : 0);
		return mx >= x0 && mx < p[0] + 22 && my >= p[1] && my < p[1] + 19;
	}

	public static void rendu(ScreenEvent.Render.Post ev) {
		if (!(ev.getScreen() instanceof AbstractContainerScreen<?> e)) return;
		Trouvee t = chercher(e);
		if (t == null || t.livres().isEmpty()) return;
		GuiGraphics g = ev.getGuiGraphics();
		int n = t.livres().size();
		ItemStack info = null;
		for (int i = 0; i < n; i++) {
			int[] p = place(e, n, i);
			boolean sur = sous(n, i, p, ev.getMouseX(), ev.getMouseY());
			if (fr.chatmort.airain.gui.InterfaceHD.actif()) {
				// interface HD : plaque d'airain arrondie côté extérieur (cramoisie au survol), livre au centre
				g.blit(PLAQUE, p[0], p[1], 0, sur ? 19 : 0, 22, 19, 32, 64);
				g.renderItem(t.livres().get(i), p[0] + 4, p[1] + 1);
			} else {
				g.fill(p[0] - 1, p[1] - 1, p[0] + 23, p[1] + 20, 0xFF000000);
				g.fill(p[0], p[1], p[0] + 22, p[1] + 19, sur ? 0xFFFFECBE : 0xFFD2BE96);
				g.fill(p[0], p[1], p[0] + 22, p[1] + 1, 0x60FFFFFF);
				g.renderItem(t.livres().get(i), p[0] + 3, p[1] + 2);
			}
			if (sur) info = t.livres().get(i);
		}
		if (info != null)
			g.renderComponentTooltip(Minecraft.getInstance().font,
				List.of(info.getHoverName(), Component.translatable("airain.reliure.clic").withStyle(net.minecraft.ChatFormatting.GRAY)),
				ev.getMouseX(), ev.getMouseY());
	}

	public static void clic(ScreenEvent.MouseButtonPressed.Pre ev) {
		if (!(ev.getScreen() instanceof AbstractContainerScreen<?> e) || ev.getButton() != 0) return;
		Trouvee t = chercher(e);
		if (t == null) return;
		int n = t.livres().size();
		for (int i = 0; i < n; i++) {
			int[] p = place(e, n, i);
			if (sous(n, i, p, ev.getMouseX(), ev.getMouseY())) {
				Minecraft.getInstance().getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, 1f));
				LectureClient.lire(Reliure.CONTENEUR, t.slot(), i, t.livres());
				ev.setCanceled(true);
				return;
			}
		}
	}
}
