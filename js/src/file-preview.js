/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
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
 * @class FilePreview
 * @extends {LitElement}
 */
class FilePreview extends LitElement {
    static styles = css`
        .text-field-container {
            overflow: auto;
            max-height: 33vw;
        }

        .diff-table {
            width: 100%;
            max-height: 50vw;
            border: none;
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
        paths: { type: Object },
        diff: { type: String }
    };

    getFileContents (path) {
        return new Promise(function (resolve, reject) {
            fetch(path)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error: status ${response.status}`)
                    }
                    return response.blob()
                })
                .then((blob) => blob.text())
                .then((text) => {
                    resolve(text)
                })
        })
    }

    getDiffTemplate () {
        if (this.diff) {
            const panelID = `${this.title}-diff`
            return html`
                <sl-tab class="tab" slot="nav" panel=${panelID}>Diff</sl-tab>
                <sl-tab-panel class="tab-panel" name=${panelID}>
                    <div class="diff-div" id=${panelID}>
                        <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${this.diff} target="_blank">
                            Open Diff in New Tab
                        </sl-button>
                        <!-- Diffs are created in the form of an HTML table so
                        viewed using an iframe  -->
                        <iframe seamless class="diff-table" src="${this.diff}"></iframe>
                    </div>
                </sl-tab-panel>
            `
        }
        return html``
    }

    render () {
        return html`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.paths).map((pair) => {
                        const reportID = pair[0]
                        const path = pair[1]
                        const panelID = `details-panel-${this.title}-${reportID}`
                        return html`
                            <sl-tab class="tab" slot="nav" panel=${panelID}>${reportID}</sl-tab>
                            <sl-tab-panel class="tab-panel" name=${panelID}>
                                <div class="text-field-container">
                                    <pre><code>${until(this.getFileContents(path), html`Loading...`)}</code></pre>
                                </div>
                            </sl-tab-panel>
                        `
                    })}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `
    }
}

customElements.define('file-preview', FilePreview)
