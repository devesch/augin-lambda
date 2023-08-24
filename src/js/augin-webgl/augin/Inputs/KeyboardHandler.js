import { Vector2, Vector3 } from "../../threejs/three.module.js";
import * as holdEvent from "../../libs/hold-event.module.js";

const KEYCODE = {
  KEY_0: 48,
  KEY_1: 49,
  KEY_2: 50,
  KEY_3: 51,
  KEY_4: 52,
  KEY_5: 53,
  KEY_6: 54,
  KEY_7: 55,
  KEY_8: 56,
  KEY_9: 57,
  KEY_LEFT: 37,
  KEY_RIGHT: 39,
  KEY_UP: 38,
  KEY_DOWN: 40,
  KEY_CTRL: 17,
  KEY_SHIFT: 16,
  KEY_ENTER: 13,
  KEY_SPACE: 32,
  KEY_TAB: 9,
  KEY_ESCAPE: 27,
  KEY_BACKSPACE: 8,
  KEY_HOME: 36,
  KEY_END: 35,
  KEY_INSERT: 45,
  KEY_DELETE: 46,
  KEY_ALT: 18,
  KEY_F1: 112,
  KEY_F2: 113,
  KEY_F3: 114,
  KEY_F4: 115,
  KEY_F5: 116,
  KEY_F6: 117,
  KEY_F7: 118,
  KEY_F8: 119,
  KEY_F9: 120,
  KEY_F10: 121,
  KEY_F11: 122,
  KEY_F12: 123,
  KEY_NUMPAD0: 96,
  KEY_NUMPAD1: 97,
  KEY_NUMPAD2: 98,
  KEY_NUMPAD3: 99,
  KEY_NUMPAD4: 100,
  KEY_NUMPAD5: 101,
  KEY_NUMPAD6: 102,
  KEY_NUMPAD7: 103,
  KEY_NUMPAD8: 104,
  KEY_NUMPAD9: 105,
  KEY_ADD: 107,
  KEY_SUBTRACT: 109,
  KEY_MULTIPLY: 106,
  KEY_DIVIDE: 111,
  KEY_SEPARATOR: 108,
  KEY_DECIMAL: 110,
  KEY_OEM_PLUS: 187,
  KEY_OEM_MINUS: 189,
  KEY_A: 65,
  KEY_B: 66,
  KEY_C: 67,
  KEY_D: 68,
  KEY_E: 69,
  KEY_F: 70,
  KEY_G: 71,
  KEY_H: 72,
  KEY_I: 73,
  KEY_J: 74,
  KEY_K: 75,
  KEY_L: 76,
  KEY_M: 77,
  KEY_N: 78,
  KEY_O: 79,
  KEY_P: 80,
  KEY_Q: 81,
  KEY_R: 82,
  KEY_S: 83,
  KEY_T: 84,
  KEY_U: 85,
  KEY_V: 86,
  KEY_W: 87,
  KEY_X: 88,
  KEY_Y: 89,
  KEY_Z: 90
};
const KeySet = new Set(Object.values(KEYCODE));

export class KeyboardHandler {
  constructor(viewer) {
    this.viewer = viewer;
    this.camera = viewer.camera;

    this.isUpPressed = false;
    this.isDownPressed = false;
    this.isLeftPressed = false;
    this.isRightPressed = false;
    this.isEPressed = false;
    this.isQPressed = false;
    this.isShiftPressed = false;
    this.isRightArrowPressed = false;
    this.isLeftArrowPressed = false;
    this.isDownArrowPressed = false;
    this.isUpArrowPressed = false;

    this.reinitializeParams();
  }

  reinitializeParams() {
    this.shiftMultiplierSpeed = this.viewer.settings.camera.shiftMultiplierSpeed;
  }

  register() {
    const wKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_W, 16.666);
    const aKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_A, 16.666);
    const sKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_S, 16.666);
    const dKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_D, 16.666);
    const qKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_Q, 16.666);
    const eKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_E, 16.666);
    const shiftKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_SHIFT, 16.666);

    const upKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_UP, 100);
    const leftKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_LEFT, 100);
    const downKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_DOWN, 100);
    const rightKey = new holdEvent.KeyboardKeyHold(KEYCODE.KEY_RIGHT, 100);


    wKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    aKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    sKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    dKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    qKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    eKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    shiftKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    upKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    leftKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    downKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));
    rightKey.addEventListener('holding', (e) => this.onKeyDown(e.originalEvent));

    document.addEventListener("keyup", (e) => this.onKeyUp(e));
  }

  onKeyUp(event) {
    this.onKey(event, false);
  }

  onKeyDown(event) {
    this.onKey(event, true);
  }

  onKey(event, keyDown) {
    // if (!keyDown && KeySet.has(event.keyCode)) {
    //     if (this._viewer.inputs.KeyAction(event.keyCode)) {
    //         event.preventDefault();
    //     }
    // }

    switch (event.keyCode) {
      case KEYCODE.KEY_W:
        this.isUpPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_S:
        this.isDownPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_D:
        this.isRightPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_A:
        this.isLeftPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_E:
        this.isEPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_Q:
        this.isQPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_SHIFT:
        this.isShiftPressed = keyDown;
        this.applyMove();
        event.preventDefault();
        break;
      case KEYCODE.KEY_UP:
        this.isUpArrowPressed = keyDown;
        this.applyRotation();
        event.preventDefault();
        break;
      case KEYCODE.KEY_DOWN:
        this.isDownArrowPressed = keyDown;
        this.applyRotation();
        event.preventDefault();
        break;
      case KEYCODE.KEY_RIGHT:
        this.isRightArrowPressed = keyDown;
        this.applyRotation();
        event.preventDefault();
        break;
      case KEYCODE.KEY_LEFT:
        this.isLeftArrowPressed = keyDown;
        this.applyRotation();
        event.preventDefault();
        break;
    }
  }

  applyMove() {
    const move = new Vector3(
      (this.isRightPressed ? 1 : 0) - (this.isLeftPressed ? 1 : 0),
      (this.isEPressed ? 1 : 0) - (this.isQPressed ? 1 : 0),
      (this.isUpPressed ? 1 : 0) - (this.isDownPressed ? 1 : 0)
    );
    const speed = this.isShiftPressed ? this.shiftMultiplierSpeed : 1;
    move.multiplyScalar(speed);
    this.camera.move(move);
  }

  applyRotation() {
    if (this.isRightArrowPressed || this.isLeftArrowPressed || this.isUpArrowPressed || this.isDownArrowPressed)
    {
      const value = 0.1;
      const delta = new Vector2(
        (this.isRightArrowPressed ? value : 0) - (this.isLeftArrowPressed ? value : 0),
        (this.isDownArrowPressed ? value : 0) - (this.isUpArrowPressed ? value : 0),
      );

      this.camera.rotate(delta);
    }
  }
}