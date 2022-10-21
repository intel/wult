/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { LitElement, html, css } from 'lit'

import './diagram.js'
import './file-preview'
import './smry-tbl'

/**
 * Responsible for generating all content contained within a metric tab.
 * @class ScDataTab
 * @extends {LitElement}
 */
class ScDataTab extends LitElement {
    static styles = css`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;

    static properties = {
        paths: { type: Array },
        fpreviews: { type: Array },
        smrytblpath: { type: String },
        smrytblfile: { type: Blob }
    }

    render () {
        if (this.smrytblpath && !this.smrytblfile) {
            fetch(this.smrytblpath).then((resp) => {
                return resp.blob()
            }).then((blob) => {
                this.smrytblfile = blob
            })
        }

        return html`
            <br>
            ${this.smrytblfile ? html`<sc-smry-tbl .file="${this.smrytblfile}"></sc-smry-tbl>` : html``}
            ${this.fpreviews
                ? this.fpreviews.map((fpreview) => html`
                    <sc-file-preview .title=${fpreview.title} .diff=${fpreview.diff} .paths=${fpreview.paths}></sc-file-preview>
                    <br>
                `)
                : html``
            }
            <div class="grid">
                ${this.paths
                    ? this.paths.map((path) => html`
                    <sc-diagram path="${path}"></sc-diagram>
                    `)
                    : html``}
            </div>
        `
    }
}

customElements.define('sc-data-tab', ScDataTab)
