package fr.chatmort.airain.ponder;

/** Textes de base (anglais) des scènes Ponder, dans l'ordre d'apparition ; généré par ponder_textes.py. */
final class PonderTextes {
	private PonderTextes() {}
	static final String HAUT_FOURNEAU_TITRE = "The Imperial Blast Furnace";
	static final String[] HAUT_FOURNEAU = {"The furnace sits on a Blaze Burner, under the grate in the middle of the hearth.", "The hearth: 5 × 5 with cut corners, two rows of fire bricks. The taphole sits in the middle of the front face.", "One to three tuyeres on the sides and at the back, each blown by a Create fan. The faster the fan, the faster the furnace.", "The shaft: 3 × 3, three rows, hollow. The throat goes in the middle of the top.", "Bare-hand right-click on the taphole: missing blocks appear as a hologram, and you can place them right into it.", "Pour the charge into the throat. Superheated burner: 3 copper, 1 zinc and 1 flux give molten airain. Heated burner: automaton scrap is remelted.", "Molten airain comes out of the taphole into pipes; slag comes out through a funnel."};
	static final String LAMINOIR_TITRE = "Rolling Airain into Wire";
	static final String[] LAMINOIR = {"The Rolling Mill is driven by a shaft on its side.", "Airain ingots go in by right-click, funnel or belt. Each ingot becomes 2 wires.", "Bare hand: take the wire back. 8 wires around an airain sheet make 2 cables."};
	static final String TELEPHERIQUE_TITRE = "The Imperial Cable Car";
	static final String[] TELEPHERIQUE = {"A line needs a station at each end. Stations are two blocks high.", "In between, stacked pylons topped with their head. At most 32 blocks per span, 8 pylons per line.", "Cable in hand: right-click a node, then the next one. The heads turn to follow the line.", "Place the gondola on a station and drive a station with a shaft from below: its speed sets the gondola's speed.", "Right-click inside the gondola: it leaves two seconds later. Right-click a station: the gondola comes."};
	static final String MONTE_CHARGE_TITRE = "The Lift";
	static final String[] MONTE_CHARGE = {"A winch, driven by Create rotation, at the foot of a rack mast.", "The cabin runs on the side where the mast was placed.", "Every catwalk placed opposite the mast, beyond the cabin, becomes a floor.", "In the cabin: right-click to go up a floor, sneak to go down. The call box brings the cabin."};
	static final String PASSAGES_MOBILES_TITRE = "Moving Crossings";
	static final String[] PASSAGES_MOBILES = {"The drawbridge and the telescopic catwalk slip into a catwalk line, facing the gap.", "They drive the 1 to 4 catwalks that follow. Wrench in the middle of the floor: change the length.", "A shaft from below: one direction deploys, the other raises or retracts. A redstone signal raises them too.", "While the crossing is open, railings close both ends."};
	static final String CONDUITE_AIR_TITRE = "Carrying the Wind";
	static final String[] CONDUITE_AIR = {"A Create fan blows into an air duct. Ducts connect on their own.", "At the far end, the air vent gives back the same current: same force, same range, same processing.", "Up to 64 ducts. Engineer's goggles show the transmitted current."};
	static final String RAYONNAGE_TITRE = "The Imperial Racking";
	static final String[] RAYONNAGE = {"Rack bays side by side and stacked form a single inventory. One item per bay, 32 stacks.", "A funnel on any bay is enough: each item goes to the bay that already holds it, otherwise to an empty bay.", "The stock is visible on the pallet, and the label shows the exact count.", "Right-click to deposit, twice quickly for everything you carry. Left-click: take a stack; sneak: a single one.", "Wrench: reserve a bay for its item. Reinforcements I to IV: up to 512 stacks."};
	static final String TABLEAU_EMAILLE_TITRE = "The Enamel Board";
	static final String[] TABLEAU_EMAILLE = {"Enamel boards side by side form a single board, up to 16 × 8.", "Bare-hand right-click opens the menu: lines, enamel, frame, font, light, mounting.", "One Create Display Link per line: stress, speed, stock, trains… Value and bar lines read numbers and percentages.", "Against a wall, hanging under a block or on a post: the board finds its mounting by itself."};
}
