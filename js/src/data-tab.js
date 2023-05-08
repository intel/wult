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
import '@shoelace-style/shoelace/dist/components/alert/alert'

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
        sl-alert {
            margin-left: 20px;
            margin-right: 20px;
        }
  `;

    static properties = {
        paths: { type: Array },
        alerts: { type: Array },
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

            ${this.alerts.length > 0
                ? html`<br><sl-alert variant="primary" open><ul>
                    ${this.alerts.map((alert) => html`<li>${alert}</li>`)}
                  </ul></sl-alert>`
                : html``
            }

            ${this.fpreviews
                ? this.fpreviews.map((fpreview) => html`
                    <sc-file-preview .title=${fpreview.title}
                        .diff=${fpreview.diff} .diffFile=${fpreview.diffFile}
                        .paths=${fpreview.paths} .files=${fpreview.files}>
                    </sc-file-preview>
                    <br>
                `)
                : html``
            }
            <div style="display: flex; flex-direction: column;">
                ${this.paths
                    ? this.paths.map((path) => html`<sc-diagram path=${path}></sc-diagram>`)
                    : html``}
            </div>
        `
    }
}

customElements.define('sc-data-tab', ScDataTab)
