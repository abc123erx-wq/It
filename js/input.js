// ============================================================
//  Teclado, mouse e controles touch
// ============================================================
import { clamp, angleTo, dist2 } from "./util.js";

const MOVE_KEYS = new Set(["w", "a", "s", "d", "arrowup", "arrowdown", "arrowleft", "arrowright"]);

export class InputController {
  constructor(canvas, touchRoot, { onPause = () => {} } = {}) {
    this.canvas = canvas;
    this.touchRoot = touchRoot;
    this.onPause = onPause;
    this.keys = new Set();
    this.mouse = { x: 0, y: 0, seen: false, down: false };
    this.moveStick = { x: 0, y: 0 };
    this.aimStick = { x: 0, y: 0 };
    this.touch = { fire: false, sprint: false, interact: false };
    this.slot = "primary";
    this.seq = { interact: 0, reload: 0, melee: 0, swap: 0 };
    this.scoreboard = false;
    this.paused = false;
    this.cleanups = [];
    this.bind();
  }

  listen(target, event, handler, opts) {
    target.addEventListener(event, handler, opts);
    this.cleanups.push(() => target.removeEventListener(event, handler, opts));
  }

  bind() {
    this.listen(window, "keydown", (e) => {
      const key = e.key.toLowerCase();
      if (MOVE_KEYS.has(key) || [" ", "shift", "e", "r", "v", "tab", "escape", "1", "2", "3"].includes(key)) e.preventDefault();
      if (e.repeat) return;
      this.keys.add(key);
      if (key === "e") this.seq.interact++;
      if (key === "r") this.seq.reload++;
      if (key === "v" || key === " ") this.seq.melee++;
      if (key === "1" || key === "2" || key === "3") {
        this.slot = key === "1" ? "primary" : key === "2" ? "secondary" : "tertiary";
        this.seq.swap++;
      }
      if (key === "escape") this.onPause();
      if (key === "tab") this.scoreboard = true;
    });
    this.listen(window, "keyup", (e) => {
      const key = e.key.toLowerCase(); this.keys.delete(key);
      if (key === "tab") this.scoreboard = false;
    });
    this.listen(window, "blur", () => {
      this.keys.clear(); this.mouse.down = false;
      this.touch.fire = false; this.touch.sprint = false; this.touch.interact = false;
      this.moveStick.x = this.moveStick.y = this.aimStick.x = this.aimStick.y = 0;
      this.scoreboard = false;
    });
    this.listen(this.canvas, "pointermove", (e) => {
      if (e.pointerType === "mouse") {
        this.mouse.x = e.clientX; this.mouse.y = e.clientY; this.mouse.seen = true;
        this.canvas.classList.add("mouse-used");
      }
    });
    this.listen(this.canvas, "pointerdown", (e) => {
      if (e.pointerType === "mouse") {
        if (e.button === 0) this.mouse.down = true;
        if (e.button === 2) this.keys.add("shift");
      }
    });
    this.listen(window, "pointerup", (e) => {
      if (e.pointerType === "mouse") {
        if (e.button === 0) this.mouse.down = false;
        if (e.button === 2) this.keys.delete("shift");
      }
    });
    this.listen(this.canvas, "contextmenu", (e) => e.preventDefault());
    this.bindStick("#move-stick", this.moveStick, false);
    this.bindStick("#aim-stick", this.aimStick, true);
    this.bindTouchButtons();
  }

  bindStick(selector, vector, aim) {
    const root = this.touchRoot?.querySelector(selector);
    if (!root) return;
    const knob = root.querySelector(".stick-knob");
    let pointer = null;
    const update = (e) => {
      const rect = root.getBoundingClientRect();
      const cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2;
      const max = rect.width * 0.32;
      let dx = e.clientX - cx, dy = e.clientY - cy;
      const d = Math.hypot(dx, dy) || 1;
      if (d > max) { dx *= max / d; dy *= max / d; }
      vector.x = clamp(dx / max, -1, 1); vector.y = clamp(dy / max, -1, 1);
      if (knob) knob.style.transform = `translate(${dx}px, ${dy}px)`;
    };
    const down = (e) => { pointer = e.pointerId; root.setPointerCapture?.(pointer); update(e); e.preventDefault(); };
    const move = (e) => { if (pointer === e.pointerId) { update(e); e.preventDefault(); } };
    const up = (e) => { if (pointer === e.pointerId) { pointer = null; vector.x = vector.y = 0; if (knob) knob.style.transform = "translate(0, 0)"; } };
    this.listen(root, "pointerdown", down);
    this.listen(root, "pointermove", move);
    this.listen(root, "pointerup", up);
    this.listen(root, "pointercancel", up);
  }

  bindTouchButtons() {
    const buttons = this.touchRoot?.querySelectorAll("[data-touch]") || [];
    for (const button of buttons) {
      const action = button.dataset.touch;
      const down = (e) => {
        e.preventDefault(); button.classList.add("pressed");
        if (action === "fire") this.touch.fire = true;
        if (action === "sprint") this.touch.sprint = true;
        if (action === "interact") { this.touch.interact = true; this.seq.interact++; }
        if (action === "reload") this.seq.reload++;
        if (action === "melee") this.seq.melee++;
        if (action === "swap") {
          this.slot = this.slot === "primary" ? "secondary" : this.slot === "secondary" ? "tertiary" : "primary";
          this.seq.swap++;
        }
      };
      const up = (e) => {
        e.preventDefault(); button.classList.remove("pressed");
        if (action === "fire") this.touch.fire = false;
        if (action === "sprint") this.touch.sprint = false;
        if (action === "interact") this.touch.interact = false;
      };
      this.listen(button, "pointerdown", down);
      this.listen(button, "pointerup", up);
      this.listen(button, "pointercancel", up);
      this.listen(button, "lostpointercapture", up);
    }
  }

  sample(player, view, world) {
    let x = this.moveStick.x, y = this.moveStick.y;
    if (this.keys.has("w") || this.keys.has("arrowup")) y -= 1;
    if (this.keys.has("s") || this.keys.has("arrowdown")) y += 1;
    if (this.keys.has("a") || this.keys.has("arrowleft")) x -= 1;
    if (this.keys.has("d") || this.keys.has("arrowright")) x += 1;
    const len = Math.hypot(x, y);
    if (len > 1) { x /= len; y /= len; }

    let aim = player?.angle || 0;
    if (this.aimStick.x * this.aimStick.x + this.aimStick.y * this.aimStick.y > 0.05) {
      aim = Math.atan2(this.aimStick.y, this.aimStick.x);
    } else if (this.mouse.seen && view) {
      const w = view.screenToWorld(this.mouse.x, this.mouse.y);
      if (w && player) aim = angleTo(player.x, player.y, w.x, w.y);
    } else if (player && world?.zombies?.length) {
      // Mira assistida leve para controles de toque sem joystick direito.
      let best = null, bestD = Infinity;
      for (const z of world.zombies) {
        const d = dist2(player.x, player.y, z.x, z.y);
        const a = angleTo(player.x, player.y, z.x, z.y);
        const diff = Math.abs(((a - aim + Math.PI * 3) % (Math.PI * 2)) - Math.PI);
        if (d < 800 * 800 && diff < 1.25 && d < bestD) { best = z; bestD = d; }
      }
      if (best) aim = angleTo(player.x, player.y, best.x, best.y);
    }
    return {
      x, y, aim,
      fire: this.mouse.down || this.touch.fire,
      sprint: this.keys.has("shift") || this.touch.sprint,
      interactHeld: this.keys.has("e") || this.touch.interact,
      slot: this.slot,
      seq: { ...this.seq }
    };
  }

  destroy() { for (const clean of this.cleanups) clean(); this.cleanups.length = 0; }
}
