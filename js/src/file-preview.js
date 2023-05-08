/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

/**
 * @license
 * Copyright (C) 2022-2023 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 */

import { LitElement, html, css } from 'lit'
import { until } from 'lit/directives/until.js'
import '@shoelace-style/shoelace/dist/components/button/button'
import '@shoelace-style/shoelace/dist/components/details/details.js'
import '@shoelace-style/shoelace/dist/components/tab-group/tab-group'
import '@shoelace-style/shoelace/dist/components/tab-panel/tab-panel'
import '@shoelace-style/shoelace/dist/components/tab/tab'

/**
 * Responsible for creating an 'sl-details' element containing previews of files given to 'paths'.
 * @class ScFilePreview
 * @extends {LitElement}
 */
class ScFilePreview extends LitElement {
    static styles = css`
        .text-field-container {
            overflow: auto;
            max-height: 33vh;
            display: flex;
            flex-direction: column;
        }

        .diff-table {
            width: 100%;
            height: 100%;
            border: none;
        }

        .diff-div {
            height: 33vh;
            display: flex;
            flex-direction: column;
        }

        sl-details::part(base) {
            font-family: Arial, sans-serif;
        }
        sl-details::part(header) {
            font-weight: "bold";
        }
    `

    static properties = {
        title: { type: String },
        files: { type: Object },
        paths: { type: Object },
        loadedFiles: { type: Boolean, attribute: false },
        diff: { type: String },
        diffFile: { type: Object }
    };

    getNewTabBtnTemplate (file) {
        return html`
            <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${URL.createObjectURL(file)} target="_blank">
                Open in New Tab
            </sl-button>
        `
    }

    getDiffTemplate () {
        if (this.diffFile) {
            const panelID = `${this.title}-diff`
            return html`
                <sl-tab class="tab" slot="nav" panel=${panelID}>Diff</sl-tab>
                <sl-tab-panel class="tab-panel" name=${panelID}>
                    <div class="diff-div" id=${panelID}>
                        <div>
                            ${this.getNewTabBtnTemplate(this.diffFile)}
                        </div>
                        <!-- Diffs are created in the form of an HTML table so
                        viewed using an iframe  -->
                        <iframe seamless class="diff-table" src="${this.diff}"></iframe>
                    </div>
                </sl-tab-panel>
            `
        }
        return html``
    }

    getTabTemplate (reportID, file) {
        const panelID = `details-panel-${this.title}-${reportID}`
        return html`
            <sl-tab class="tab" slot="nav" panel=${panelID}>${reportID}</sl-tab>
            <sl-tab-panel class="tab-panel" name=${panelID}>
                <div class="text-field-container">
                    <div>
                        ${this.getNewTabBtnTemplate(file)}
                    </div>
                    <pre><code>${until(file.text(), html`Loading...`)}</code></pre>
                </div>
            </sl-tab-panel>
        `
    }

    async loadFiles () {
        for (const pair of Object.entries(this.paths)) {
            await fetch(pair[1])
                .then((resp) => resp.blob())
                .then((blob) => {
                    this.files[pair[0]] = blob
                })
        }
        if (this.diff) {
            await fetch(this.diff)
                .then((resp) => resp.blob())
                .then((blob) => { this.diffFile = blob })
        }
        this.loadedFiles = true
    }

    connectedCallback () {
        super.connectedCallback()
        if (!this.files && this.paths) {
            this.files = {}
            this.loadedFiles = false
            this.loadFiles()
        } else {
            this.loadedFiles = true
        }
    }

    render () {
        if (!this.files) {
            return html``
        }

        return html`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.files).map((pair) => this.getTabTemplate(pair[0], pair[1]))}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `
    }
}

customElements.define('sc-file-preview', ScFilePreview)
