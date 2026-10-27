package fr.chatmort.airain.enchant;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import fr.chatmort.airain.AirainMod;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Table d'enchantement de l'Empire : on choisit l'enchantement parmi les livres des bibliothèques sculptées voisines. */
public class TableEmpireBlock extends Block implements EntityBlock {
	private static final VoxelShape FORME = Block.box(0, 0, 0, 16, 12, 16);

	public TableEmpireBlock(Properties properties) {
		super(properties);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
		return FORME;
	}

	@Override
	protected boolean useShapeForLightOcclusion(BlockState state) {
		return true;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
		if (level.isClientSide)
			return InteractionResult.SUCCESS;
		if (player instanceof ServerPlayer sp) {
			sp.openMenu(new SimpleMenuProvider((id, inv, p) -> new TableEmpireMenu(id, inv, ContainerLevelAccess.create(level, pos)),
				Component.translatable("block.airain.table_enchantement")), buf -> buf.writeBlockPos(pos));
		}
		return InteractionResult.CONSUME;
	}

	@Override
	public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new TableEmpireBlockEntity(pos, state);
	}

	@Override
	@SuppressWarnings("unchecked")
	public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
		if (!level.isClientSide || type != AirainMod.TABLE_BE.get())
			return null;
		return (l, p, s, be) -> TableEmpireBlockEntity.animer(l, p, s, (TableEmpireBlockEntity) be);
	}

	/** Comme la table vanilla : des glyphes s'échappent des bibliothèques sculptées garnies vers la table. */
	@Override
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		for (int i = 0; i < 6; i++) {
			BlockPos b = pos.offset(random.nextInt(7) - 3, random.nextInt(4) - 1, random.nextInt(7) - 3);
			if (b.equals(pos) || !(level.getBlockEntity(b) instanceof net.minecraft.world.level.block.entity.ChiseledBookShelfBlockEntity etagere)
				|| etagere.isEmpty())
				continue;
			level.addParticle(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 2.0, pos.getZ() + 0.5,
				b.getX() - pos.getX() + random.nextFloat() - 0.5, b.getY() - pos.getY() - random.nextFloat() - 1.0,
				b.getZ() - pos.getZ() + random.nextFloat() - 0.5);
		}
	}
}
