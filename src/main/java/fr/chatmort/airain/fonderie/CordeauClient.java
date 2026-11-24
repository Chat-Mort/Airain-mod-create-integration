package fr.chatmort.airain.fonderie;

import java.util.List;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** 1.69.1 : côté client du cordeau (clics, aperçu en fil d'airain, nombre de cases dans la barre d'action). */
public final class CordeauClient {
	private CordeauClient() {}

	static void clic(InteractionHand main, BlockHitResult h) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null) return;
		ItemStack s = mc.player.getItemInHand(main);
		boolean principale = main == InteractionHand.MAIN_HAND;
		BlockPos a = Cordeau.a(s, mc.level), b = Cordeau.b(s, mc.level);
		int quoi;
		BlockPos pos = BlockPos.ZERO;
		if (Screen.hasControlDown()) quoi = Cordeau.MODE;
		else if (mc.player.isShiftKeyDown()) quoi = Cordeau.ANNULER;
		else if (a != null && b != null) quoi = Cordeau.POSER;
		else if (h != null) { quoi = Cordeau.POINT; pos = Cordeau.cellule(mc.level, h); }
		else return;
		PacketDistributor.sendToServer(new Cordeau.Action(quoi, pos, principale));
	}

	/** Le cordeau tenu (main principale d'abord), ou vide. */
	private static ItemStack tenu(Minecraft mc) {
		ItemStack m = mc.player.getMainHandItem();
		if (m.is(Cordeau.CORDEAU.get())) return m;
		ItemStack o = mc.player.getOffhandItem();
		return o.is(Cordeau.CORDEAU.get()) ? o : ItemStack.EMPTY;
	}

	/** Deuxième point provisoire : B s'il est posé, sinon la case visée. */
	private static BlockPos secondPoint(Minecraft mc, ItemStack s) {
		BlockPos b = Cordeau.b(s, mc.level);
		if (b != null) return b;
		if (mc.hitResult instanceof BlockHitResult h && h.getType() == HitResult.Type.BLOCK) return Cordeau.cellule(mc.level, h);
		return null;
	}

	// pendant le choix du point B, la barre d'action suit la case visée
	public static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null || mc.player.tickCount % 4 != 0) return;
		ItemStack s = tenu(mc);
		if (s.isEmpty()) return;
		BlockPos a = Cordeau.a(s, mc.level);
		if (a == null || Cordeau.b(s, mc.level) != null) return;
		BlockPos c = secondPoint(mc, s);
		if (c == null) return;
		mc.gui.setOverlayMessage(Cordeau.forme(a, c, Cordeau.contour(s)).append(Component.translatable("airain.cordeau.suite_b")), false);
	}

	public static void rendu(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null) return;
		ItemStack s = tenu(mc);
		if (s.isEmpty()) return;
		BlockPos a = Cordeau.a(s, mc.level);
		if (a == null) return;
		BlockPos b = secondPoint(mc, s);
		boolean fixe = Cordeau.b(s, mc.level) != null;
		List<BlockPos> cs = b == null ? null : Cordeau.cases(a, b, Cordeau.contour(s));
		PoseStack ms = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		VertexConsumer vc = buf.getBuffer(RenderType.lines());
		ms.pushPose();
		ms.translate(-cam.x, -cam.y, -cam.z);
		// cases prévues en fil d'airain (plus pâle tant que B n'est pas planté)
		float al = fixe ? 1f : 0.55f;
		if (cs != null) for (BlockPos c : cs) LevelRenderer.renderLineBox(ms, vc, new AABB(c).deflate(0.03), 0.953f, 0.839f, 0.580f, al);
		// piquets A et B en rouge impérial
		LevelRenderer.renderLineBox(ms, vc, new AABB(a).inflate(0.02), 0.753f, 0.263f, 0.263f, 1f);
		if (b != null) LevelRenderer.renderLineBox(ms, vc, new AABB(b).inflate(0.02), 0.753f, 0.263f, 0.263f, fixe ? 1f : 0.55f);
		ms.popPose();
		buf.endBatch(RenderType.lines());
	}
}
