package fr.chatmort.airain.fonderie;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;

import net.createmod.catnip.render.CachedBuffers;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** 1.69.9 : côté client du carton de motif (clics, molette, aperçu) et de la molette du cordeau. */
public final class MotifClient {
	private MotifClient() {}

	static void clic(InteractionHand main, BlockHitResult h) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null) return;
		ItemStack s = mc.player.getItemInHand(main);
		BlockPos a = Motif.a(s, mc.level), b = Motif.b(s, mc.level);
		int quoi; BlockPos pos = BlockPos.ZERO;
		if (Screen.hasControlDown() || mc.player.isShiftKeyDown()) quoi = Cordeau.MODE;          // quart de tour du motif
		else if (a != null && b != null) quoi = Cordeau.POSER;                                     // enregistrer
		else if (h != null) { quoi = Cordeau.POINT; pos = h.getBlockPos(); }                        // le bloc visé lui-même
		else return;
		PacketDistributor.sendToServer(new Cordeau.Action(quoi, pos, main == InteractionHand.MAIN_HAND));
	}

	/** Accroupi + molette, cordeau ou carton en main principale avec deux coins posés : la face regardée avance ou recule. */
	public static void molette(InputEvent.MouseScrollingEvent e) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null || mc.screen != null || !mc.player.isShiftKeyDown() || e.getScrollDeltaY() == 0) return;
		ItemStack s = mc.player.getMainHandItem();
		boolean ok = s.is(Cordeau.CORDEAU.get()) ? Cordeau.a(s, mc.level) != null && Cordeau.b(s, mc.level) != null
			: s.is(Motif.CARTON.get()) && Motif.a(s, mc.level) != null && Motif.b(s, mc.level) != null;
		if (!ok) return;
		e.setCanceled(true);
		Vec3 v = mc.player.getLookAngle();
		Direction d = Direction.getNearest(v.x, v.y, v.z);
		PacketDistributor.sendToServer(new Cordeau.Action(Cordeau.TAILLE, new BlockPos(d.get3DDataValue(), e.getScrollDeltaY() > 0 ? 1 : -1, 0), true));
	}

	/** Pendant la prise du second coin au carton, la taille suit le bloc visé. */
	public static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null || mc.player.tickCount % 4 != 0) return;
		ItemStack s = mc.player.getMainHandItem();
		if (!s.is(Motif.CARTON.get())) return;
		BlockPos a = Motif.a(s, mc.level);
		if (a == null || Motif.b(s, mc.level) != null || !(mc.hitResult instanceof BlockHitResult h) || h.getType() != HitResult.Type.BLOCK) return;
		mc.gui.setOverlayMessage(Motif.selection(a, h.getBlockPos()).append(Component.translatable("airain.motif.suite_b")), false);
	}

	/** Sélection du carton en main : le pourtour en fil d'airain, coins en rouge. */
	public static void rendu(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null) return;
		ItemStack s = mc.player.getMainHandItem();
		if (!s.is(Motif.CARTON.get())) return;
		BlockPos a = Motif.a(s, mc.level);
		if (a == null) return;
		BlockPos b = Motif.b(s, mc.level);
		boolean fixe = b != null;
		if (b == null && mc.hitResult instanceof BlockHitResult h && h.getType() == HitResult.Type.BLOCK) b = h.getBlockPos();
		PoseStack ms = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		VertexConsumer vc = buf.getBuffer(RenderType.lines());
		ms.pushPose();
		ms.translate(-cam.x, -cam.y, -cam.z);
		float al = fixe ? 1f : 0.55f;
		boolean ok = b != null && Motif.tailleOk(a, b);
		if (b != null) LevelRenderer.renderLineBox(ms, vc, MotifClient.boite(a, b).inflate(0.02), ok ? 0.953f : 0.9f, ok ? 0.839f : 0.2f, ok ? 0.580f : 0.2f, al);
		LevelRenderer.renderLineBox(ms, vc, new AABB(a).inflate(0.04), 0.753f, 0.263f, 0.263f, 1f);
		if (b != null) LevelRenderer.renderLineBox(ms, vc, new AABB(b).inflate(0.04), 0.753f, 0.263f, 0.263f, al);
		ms.popPose();
		buf.endBatch(RenderType.lines());
	}

	/** La boîte qui enveloppe les blocs de a à b. */
	static AABB boite(BlockPos a, BlockPos b) {
		return new AABB(Math.min(a.getX(), b.getX()), Math.min(a.getY(), b.getY()), Math.min(a.getZ(), b.getZ()),
			Math.max(a.getX(), b.getX()) + 1, Math.max(a.getY(), b.getY()) + 1, Math.max(a.getZ(), b.getZ()) + 1);
	}

	/** Les blocs du motif répété, en transparence, dans les cases vides seulement (1 000 au plus). */
	static void fantomes(PoseStack ms, MultiBufferSource.BufferSource buf, Minecraft mc, BlockPos a, BlockPos b, Motif.Grille g, int rot) {
		VertexConsumer vc = buf.getBuffer(RenderType.translucent());
		int n = 0;
		for (BlockPos c : BlockPos.betweenClosed(a, b)) {
			BlockState st = Motif.etat(g, rot, c.getX() - a.getX(), c.getY() - a.getY(), c.getZ() - a.getZ());
			if (st == null || st.getRenderShape() != RenderShape.MODEL || !mc.level.getBlockState(c).canBeReplaced()) continue;
			if (++n > Motif.APERCU_MAX) break;
			ms.pushPose();
			ms.translate(c.getX(), c.getY(), c.getZ());
			CachedBuffers.block(st).light(LightTexture.FULL_BRIGHT).color(255, 255, 255, 120).renderInto(ms, vc);
			ms.popPose();
		}
		buf.endBatch(RenderType.translucent());
	}
}
