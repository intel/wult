/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import {LitElement, html} from 'lit';

/**
 * Generic class which handles visiblity of report tabs. When creating a new tab, it is recommended
 * to use a class which inherits from this class or create a new type. For example, if you want to
 * add a new 'metric' tab, then use the '<wult-metric-tab>' element over this one.
 * 
 * @class WultTab
 * @extends {LitElement}
 */
export class WultTab extends LitElement {

    static properties = {
        tabname: {type: String},
        info: {type: Object},
        visible: {type: Boolean, attribute: false}
    };

    /**
     * Checks whether this tab is visible by checking if the tab has the 'active' class applied to
     * it and sets the 'visible' attribute accordingly.
     */
    checkVisible() {
        let tab = document.getElementById(this.tabname);
        this.visible = tab.classList.contains('active');
    }

    /**
     * Early DOM lifecycle event. Invoked each time the custom element is appended into a
     * document-connected element.
     */
    connectedCallback(){
        super.connectedCallback();
        // Adds event listener so that the tab will re-evaulate 'visible' every time the user clicks
        // to see if the tab has been opened. Read relevant docs here:
        // https://lit.dev/docs/components/events/#adding-event-listeners-to-other-elements
        window.addEventListener("click", this._handleClick);
        this.checkVisible();
    }

    /**
     * Removes the 'click' event handler in the case that the tab is destroyed so that the window
     * does not attempt to trigger the handler when it is no longer accessible.
     */
    disconnectedCallback(){
        window.removeEventListener('click', this._handleClick);
        super.disconnectedCallback();
    }

    constructor() {
        super();
        this._handleClick = this.checkVisible.bind(this);
    }

    /**
     * Provides the template for when the tab is visible (active).
     */
    visibleTemplate() {
        throw new Error("Inherit from this class and implement 'visibleTemplate'.")
    }

    render() {
        return this.visible
        ? html`${this.visibleTemplate()}`
        : html``;
    }
}

customElements.define('wult-tab', WultTab);
