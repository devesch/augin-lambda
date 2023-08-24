import { DefaultInputScheme } from "./DefaultInputScheme.js";
import { KeyboardHandler } from "./KeyboardHandler.js";
import { MouseHandler } from "./MouseHandler.js";
import { TouchHandler } from "./TouchHandler.js";
import { BrowserHelper } from "../Helpers/BrowserHelper.js";

export class Input
{
    constructor(viewer)
    {
        this.mouse = new MouseHandler(viewer);
        this.keyboard = new KeyboardHandler(viewer);
        this.touch = new TouchHandler(viewer);

        this._scheme = new DefaultInputScheme(viewer);
    }

    get scheme() {
        return this._scheme;
    }

    set scheme(value) {
        this._scheme = value != null ? value : new DefaultInputScheme(this._viewer);
    }

    reinitializeParams() {
        this.mouse.reinitializeParams();
        this.keyboard.reinitializeParams();
        if (BrowserHelper.hasTouchSupport()) {
            this.touch.reinitializeParams();
        }
    }

    register()
    {
        this.mouse.register();
        this.keyboard.register();
        if (BrowserHelper.hasTouchSupport()) {
            this.touch.register();
        }
    }

    mainAction(action) {
        this._scheme.onMainAction(action);
    }
}