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
import '@shoelace-style/shoelace/dist/components/button/button.js'
import '@shoelace-style/shoelace/dist/components/dialog/dialog.js'
import '@shoelace-style/shoelace/dist/components/divider/divider.js'
import '@shoelace-style/shoelace/dist/components/spinner/spinner.js'

/**
 * Responsible for creating a 'div' element containing a plot.
 * @class ScDiagram
 * @extends {LitElement}
 */
class ScDiagram extends LitElement {
    static styles = css`
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5% 0%;
            font-size: 15vw;
            height: 85vh;
        }

        sl-dialog {
            --width: 100vw;
            --header-spacing: var(--sl-spacing-small);
            --body-spacing: var(--sl-spacing-2x-small);
        }

        .dialog-overview::part(panel) {
            height: 95vh;
            overflow: hidden;
            display: block;
        }

        .plot-iframe {
            height: 0%;
            width: 100%;
        }
  `;

    static properties = {
        path: { type: String },
        _dialogOpened: { type: Boolean, state: true },
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
        this._dialogOpened = false
    }

    /**
     * Hides the loading indicator once the diagram 'iframe' has finished loading. Intended to be
     * called when a 'load' event is detected.
     * @param spinnerID - ID of the spinner component to hide.
     * @param iframeID - the ID of the iframe which has loaded and should have its height restored.
     */
    hideLoading (spinnerID, iframeID) {
        // Hide the spinner.
        this.renderRoot.querySelector(`#${spinnerID}`).remove()

        // Increase the height of the iframe.
        const iframeEl = this.renderRoot.querySelector(`#${iframeID}`)
        iframeEl.style.height = '85vh'
    }

    /**
     * Opens the dialog with a fullscreen view of the diagram.
     */
    openFullscreen () {
        const dialog = this.renderRoot.querySelector('.dialog-overview')

        if (!dialog) {
            throw Error('failed to find dialog element, unable to open fullscreen diagram view.')
        }

        this._dialogOpened = true
        return dialog.show()
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

    /**
     * Returns an HTMLTemplate of the plot iframe and a loading spinner to indicate its loaded
     * status.
     * @param {String} spinnerID - an ID unique to this shadow root for the loading indicator.
     * @param {String} iframeID - an ID unique to this shadow root for the plot iframe.
     */
    iframeTemplate (spinnerID, iframeID) {
        return html`
            ${this.spinnerTemplate(spinnerID)}
            <iframe id=${iframeID} seamless frameborder="0" scrolling="no" class="plot-iframe"
                @load=${() => this.hideLoading(spinnerID, iframeID)} src=${this.path}>
            </iframe>
        `
    }

    /**
     * Returns an HTMLTemplate of the dialog containing the fullscreen view of the plot.
     */
    dialogTemplate () {
        return html`
            <sl-dialog class="dialog-overview">
                ${this._dialogOpened
                    ? this.iframeTemplate('dialog-spinner', 'dialog-iframe')
                    : html``
                }
            </sl-dialog>
        `
    }

    render () {
        if (!this._visible) {
            return html``
        }
        return html`
            ${this.dialogTemplate()}
            <sl-divider></sl-divider>

            <sl-button style="margin-left: 2em;" @click=${this.openFullscreen}>
                Open Fullscreen View
            </sl-button>

            ${this.iframeTemplate('page-spinner', 'page-iframe')}
        `
    }
}

customElements.define('sc-diagram', ScDiagram)
