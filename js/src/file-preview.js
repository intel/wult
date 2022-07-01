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
import '@shoelace-style/shoelace/dist/components/details/details.js'
import '@shoelace-style/shoelace/dist/components/tab-group/tab-group'
import '@shoelace-style/shoelace/dist/components/tab-panel/tab-panel'
import '@shoelace-style/shoelace/dist/components/tab/tab'

/**
 * Responsible for creating an 'sl-details' element containing previews of files given to 'fpaths'.
 * @class FilePreview
 * @extends {LitElement}
 */
class FilePreview extends LitElement {
    static styles = css`
        .text-field-container {
            overflow: auto;
            max-height: 33vw;
        }

        sl-details::part(base) {
            font-family: Arial, sans-serif;
        }
        sl-details::part(header) {
            font-weight: "bold";
        }
    `

    static properties = {
        name: { type: String },
        fpaths: { type: Object }
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

    render () {
        return html`
            <sl-details summary=${this.name}>
                <sl-tab-group>
                    ${Object.entries(this.fpaths).map((pair) => {
                        const reportID = pair[0]
                        const path = pair[1]
                        const panelID = `details-panel-${this.name}-${reportID}`
                        return html`
                            <sl-tab class="tab" slot="nav" panel=${panelID}>${reportID}</sl-tab>
                            <sl-tab-panel class="tab-panel" name=${panelID}>
                                <div class="text-field-container">
                                    <pre><code>${until(this.getFileContents(path), html`Loading...`)}</code></pre>
                                </div>
                            </sl-tab-panel>
                        `
                    })}
                </sl-tab-group>
            </sl-details>
        `
    }
}

customElements.define('file-preview', FilePreview)
