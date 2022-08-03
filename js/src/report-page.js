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
import '@shoelace-style/shoelace/dist/components/alert/alert'

import './intro-tbl'
import './tab-group'

/**
 * 'LitElement' containing the other components of the HTML report.
 * @class ScReportPage
 * @extends {LitElement}
 */
export class ScReportPage extends LitElement {
    static properties = {
        src: { type: String },
        reportInfo: { type: Object, attribute: false },
        fetchFailed: { type: Boolean, attribute: false }
    }

    static styles = css`
        .report-head {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .report-title {
            font-family: Arial, sans-serif;
        }
    `

    async connectedCallback () {
        super.connectedCallback()
        try {
            const resp = await fetch(this.src)
            this.reportInfo = await resp.json()
            this.toolname = this.reportInfo.toolname
            this.titleDescr = this.reportInfo.title_descr
            this.tabFile = this.reportInfo.tab_file
            this.introtbl = this.reportInfo.intro_tbl
        } catch (err) {
        // Catching a CORS error caused by viewing reports locally.
            if (err instanceof TypeError) {
                this.fetchFailed = true
            }
        }
    }

    /**
     * Returns the HTML template for an alert to tell the user about a CORS error thrown when the
     * report is viewed locally.  We use the 'file:/' protocol to read the JSON file which contains
     * the tab data. This can cause a CORS error when the browser tries to read local files. Because
     * of this we warn the user about what is happening and inform them how to properly view reports
     * locally.
     */
    corsWarning () {
        return html`
        <sl-alert variant="danger" open>
          Warning: it looks like you might be trying to view this report
          locally.  See our documentation on how to do that <a
          href="https://intel.github.io/wult/pages/howto.html#open-wult-reports-locally">
            here.</a>
          </sl-alert>
      `
    }

    render () {
        if (this.fetchFailed) {
            return this.corsWarning()
        }

        return html`
            <div class="report-head">
                <h1 class="report-title">${this.toolname} report</h1>
                ${this.titleDescr
                    ? html`
                    <p class="title_descr">${this.titleDescr}</p>
                    <br>
                    `
                    : html``
                }

                <sc-intro-tbl .src=${this.introtbl}></sc-intro-tbl>
            </div>
            <br>
            <sc-tab-group .tabFile="${this.tabFile}"></sc-tab-group>
        `
    }
}

customElements.define('sc-report-page', ScReportPage)
