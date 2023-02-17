/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

/**
 * @license
 * Copyright (C) 2019-2023 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 */

import { LitElement, html, css } from 'lit'
import '@shoelace-style/shoelace/dist/components/spinner/spinner.js'

/**
 * Responsible for creating a 'div' element containing a plot.
 * @class ScDiagram
 * @extends {LitElement}
 */
class ScDiagram extends LitElement {
    static styles = css`
    .frame {
        height: 85vh;
        width: 100%;
    }
    .loading {
        display: flex;
        justify-content: center;
        padding: 5% 0%;
        font-size: 15vw;
    }
  `;

    static properties = {
        path: { type: String },
        _visible: { type: Boolean, state: true }
    };

    /**
     * Early DOM lifecycle event. Invoked each time the custom element is appended into a
     * document-connected element.
     */
    connectedCallback () {
        super.connectedCallback()
        const callback = (entries, _) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this._visible = true
                } else {
                    this._visible = false
                }
            })
        }
        this.observer = new IntersectionObserver(callback)
        this.observer.observe(this.parentElement)
    }

    /**
     * Removes the intersection observer in case the tab is destroyed so the window does not attempt
     * to trigger the handler when it is no longer accessible.
     */
    disconnectedCallback () {
        super.disconnectedCallback()
        this.observer.disconnect()
    }

    constructor () {
        super()
        this._visible = false
    }

    /**
     * Hides the loading indicator once the diagram 'iframe' has finished loading. Intended to be
     * called when a 'load' event is detected.
     * @param spinnerID - ID of the spinner component to hide.
     */
    hideLoading (spinnerID) {
        this.renderRoot.querySelector(`#${spinnerID}`).remove()
    }

    /**
     * Returns the HTML template for a loading spinner.
     * @param spinnerID - ID to give to the contained spinner.
     * @returns HTMLTemplate
     */
    spinnerTemplate (spinnerID) {
        return html`
            <div id=${spinnerID} class="loading">
                <sl-spinner></sl-spinner>
            </div>
        `
    }

    render () {
        if (!this._visible) {
            return html``
        }
        return html`
            ${this.spinnerTemplate('plot-spinner')}
            <iframe id="plot-frame" frameborder="0" scrolling="no" class="frame" seamless
                @load=${() => this.hideLoading('plot-spinner')}
                src=${this.path}>
            </iframe>
        `
    }
}

customElements.define('sc-diagram', ScDiagram)
