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
		if (type != AirainMod.TABLE_BE.get())
			return null;
		return level.isClientSide ? (l, p, s, be) -> TableEmpireBlockEntity.animer(l, p, s, (TableEmpireBlockEntity) be)
			: (l, p, s, be) -> TableEmpireBlockEntity.tickServeur(l, p, s, (TableEmpireBlockEntity) be);
	}

	/**
	 * Des glyphes s'échappent des bibliothèques que la table lit (livres enchantés) et filent vers elle ;
	 * celles qui portent un tome ancien envoient en plus des étincelles dorées.
	 */
	@Override
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		if (!(level.getBlockEntity(pos) instanceof TableEmpireBlockEntity table)) return;
		var et = table.etageres(false);
		for (int i = 0; i < Math.min(4, et.size()); i++) {
			BlockPos b = et.get(random.nextInt(et.size()));
			level.addParticle(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 2.0, pos.getZ() + 0.5,
				b.getX() + random.nextFloat() - 0.5, b.getY() - random.nextFloat() - 1.0, b.getZ() + random.nextFloat() - 0.5);
		}
		for (BlockPos b : table.etageres(true)) {
			if (random.nextInt(3) != 0) continue;
			double sx = pos.getX() + b.getX() + 0.5, sy = pos.getY() + b.getY() + 0.5, sz = pos.getZ() + b.getZ() + 0.5;
			double dx = pos.getX() + 0.5 - sx, dy = pos.getY() + 1.1 - sy, dz = pos.getZ() + 0.5 - sz;
			level.addParticle(ParticleTypes.WAX_ON, sx, sy, sz, dx * 0.12, dy * 0.12 + 0.02, dz * 0.12);
		}
	}
}
