/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import {LitElement, html, css} from 'lit';

import './diagram-element.js';

class WultMetricTab extends LitElement {
    static styles = css`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;

    static properties = {
        paths: {type: Array},
        tabname: {type: String},
        visible: {type: Boolean}
    };

    checkVisible() {
        let tab = document.getElementById(this.tabname);
        this.visible = tab.classList.contains('active');
    }

    connectedCallback(){
        super.connectedCallback();
        window.addEventListener("click", this._handleClick);
        this.checkVisible();
    }

    disconnectedCallback(){
        window.removeEventListener('click', this._handleClick);
        super.disconnectedCallback();
    }

    constructor() {
        super();
        this._handleClick = this.checkVisible.bind(this);
    }

    /*
     * Provides the template for when the tab is visible (active).
     */
    visibleTemplate() {
        return html`
            <div class="grid">
            ${this.paths.map((path) =>
                    html`<diagram-element path="${path}" ></diagram-element>`
            )}
            </div>
        `
    }

    render() {
        return this.visible
        ? html`${this.visibleTemplate()}`
        : html``;
    }
}

customElements.define('wult-metric-tab', WultMetricTab);
