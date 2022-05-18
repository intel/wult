/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { LitElement, html, css } from '../node_modules/lit/index.js'

/**
 * Responsible for creating a 'div' element containing a plot.
 * @class DiagramElement
 * @extends {LitElement}
 */
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
        path: { type: String }
    };

    /**
     * Hides the loading indicator once the diagram 'iframe' has finished loading. Intended to be
     * called when a 'load' event is detected.
     */
    hideLoading () {
        this.renderRoot.querySelector('#loading').style.display = 'none'
    }

    render () {
        return html`
            <div id="loading">
                <p>Loading plot...</p>
            </div>
            <div class="plot">
                <iframe @load=${this.hideLoading} seamless="seamless" frameborder="0" scrolling="no" class="frame" src="${this.path}"></iframe>
            </div>
        `
    }
}

customElements.define('diagram-element', DiagramElement)
