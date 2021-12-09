/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import {LitElement, html, css} from '../node_modules/lit/index.js';

class DiagramElement extends LitElement {
    static styles = css`
    .plot {
        position: relative;
        height: 100%;
        width: 100%;
        grid-column-start: span 3;
    }
    .frame {
        height: 100%;
        width: 100%;
    }
  `;

    static properties = {
        path: {type: String},
        visible: {type: Boolean},
        ptab: {type: String},
    };

    checkVisible() {
        let parentTab = document.getElementById(this.ptab);
        this.visible = parentTab.classList.contains('active');
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



    render() {
        return this.visible
        ? html`
        <div class="plot">
            <iframe seamless="seamless" frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
        </div>
        `
        : html``;
    }
}

customElements.define('diagram-element', DiagramElement);
