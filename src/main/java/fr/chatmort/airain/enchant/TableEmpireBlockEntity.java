package fr.chatmort.airain.enchant;

import fr.chatmort.airain.AirainMod;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Ne sert qu'à animer le livre flottant (même logique que la table vanilla). */
public class TableEmpireBlockEntity extends BlockEntity {
	private static final RandomSource HASARD = RandomSource.create();
	public int temps;
	public float tourne, oTourne, cibleRot, flip, oFlip, flipCible, flipVit, ouvert, oOuvert;

	public TableEmpireBlockEntity(BlockPos pos, BlockState state) {
		super(AirainMod.TABLE_BE.get(), pos, state);
	}

	public static void animer(Level level, BlockPos pos, BlockState state, TableEmpireBlockEntity be) {
		be.oOuvert = be.ouvert;
		be.oTourne = be.tourne;
		Player p = level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 3.0, false);
		if (p != null) {
			be.cibleRot = (float) Mth.atan2(p.getZ() - (pos.getZ() + 0.5), p.getX() - (pos.getX() + 0.5));
			be.ouvert += 0.1F;
			if (be.ouvert < 0.5F || HASARD.nextInt(40) == 0) {
				float avant = be.flipCible;
				do {
					be.flipCible += (float) (HASARD.nextInt(4) - HASARD.nextInt(4));
				} while (avant == be.flipCible);
			}
		} else {
			be.cibleRot += 0.02F;
			be.ouvert -= 0.1F;
		}
		be.tourne = Mth.wrapDegrees(be.tourne * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		be.cibleRot = Mth.wrapDegrees(be.cibleRot * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		float d = Mth.wrapDegrees((be.cibleRot - be.tourne) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
		be.tourne += d * 0.4F;
		be.ouvert = Mth.clamp(be.ouvert, 0.0F, 1.0F);
		be.temps++;
		be.oFlip = be.flip;
		float f = Mth.clamp((be.flipCible - be.flip) * 0.4F, -0.2F, 0.2F);
		be.flipVit += (f - be.flipVit) * 0.9F;
		be.flip += be.flipVit;
	}
}
