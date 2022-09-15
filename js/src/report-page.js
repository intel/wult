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
import '@shoelace-style/shoelace/dist/components/divider/divider'
import '@shoelace-style/shoelace/dist/components/dialog/dialog'

import './intro-tbl'
import './tab-group'

/**
 * 'LitElement' containing the other components of the HTML report.
 * @class ScReportPage
 * @extends {LitElement}
 */
export class ScReportPage extends LitElement {
    static properties = {
        introtbl: { type: Object },
        src: { type: String },
        reportInfo: { type: Object },
        toolname: { type: String },
        titleDescr: { type: String },
        tabs: { type: Object },
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

        .cors-warning {
            display: flex;
            flex-direction: column;
            font-family: Arial, sans-serif;
        }

        // Hide the close button as the dialog is not closable.
        sl-dialog::part(close-button) {
            visibility: hidden;
        }
    `

    get _corsWarning () {
        return this.renderRoot.querySelector('.cors-warning')
    }

    /**
     * Extracts fields in 'this.reportInfo' into various class properties.
     */
    initRepProps () {
        this.toolname = this.reportInfo.toolname
        this.titleDescr = this.reportInfo.title_descr
    }

    async connectedCallback () {
        try {
            let resp = await fetch(this.src)
            this.reportInfo = await resp.json()
            resp = await fetch(this.reportInfo.intro_tbl)
            this.introtbl = await resp.blob()
            const rawTabs = await (await fetch(this.reportInfo.tab_file)).json()
            this.tabs = await this.extractTabs(rawTabs, true)
            this.initRepProps()
        } catch (err) {
        // Catching a CORS error caused by viewing reports locally.
            if (err instanceof TypeError) {
                this.fetchFailed = true
            }
        }
        super.connectedCallback()
    }

    updated (changedProperties) {
        if (changedProperties.has('fetchFailed')) {
            // Prevent the dialog from closing.
            this._corsWarning.addEventListener('sl-request-close', event => {
                event.preventDefault()
            })
        }
    }

    /**
     * Returns the HTML template for an alert to handle the CORS error thrown when the report is
     * viewed locally. We use first try to use the 'file:/' protocol to read the JSON file which
     * contains the tab data. This can cause a CORS error when the browser tries to read local
     * files. Because of this we warn the user about what is happening. Then we suggest that they
     * upload the report directory so that we can circumvent the security restriction.
     */
    corsWarning () {
        return html`
            <sl-dialog class="cors-warning" label="Failed to load report" open>
                <p>
                    Due to browser security limitations your report could not be retrieved. Please
                    upload your report directory using the upload button below:
                </p>
                <input @change="${this.processUploadedFiles}" id="upload-files" directory webkitdirectory type="file">
                <sl-divider></sl-divider>
                <p>
                    If you have tried uploading your report directory with the button above and it 
                    is still not rendering properly, please see our documentation for details on
                    other methods for viewing wult reports:
                    <a href="https://intel.github.io/wult/pages/howto-view-local.html#open-wult-reports-locally"> here</a>.
                </p>
            </sl-dialog>
        `
    }

    findFile (query) {
        const fileKeys = Object.keys(this.files)
        for (const key of fileKeys) {
            if (key.endsWith(query)) {
                return this.files[key]
            }
        }
        throw Error(`unable to find an uploaded file ending with '${query}'.`)
    }

    async extractTabs (tabs, useFetch) {
        // Convert summary file paths to 'File' objects.
        for (const tab of tabs) {
            if (tab.smrytblpath) {
                if (useFetch) {
                    tab.smrytblfile = await (await fetch(tab.smrytblpath)).blob()
                } else {
                    tab.smrytblfile = this.findFile(tab.smrytblpath)
                }
            }
            if (tab.tabs) {
                tab.tabs = await this.extractTabs(tab.tabs, useFetch)
            }
        }
        return tabs
    }

    /**
     * Process user-uploaded report files.
     */
    async processUploadedFiles () {
        const fileInput = this.renderRoot.getElementById('upload-files')

        this.files = {}
        for (const file of fileInput.files) {
            this.files[file.webkitRelativePath] = file
        }

        const content = await this.findFile('report_info.json').arrayBuffer()
        this.reportInfo = JSON.parse((new TextDecoder()).decode(content))
        this.introtbl = this.findFile(this.reportInfo.intro_tbl)

        const tabs = await this.findFile(this.reportInfo.tab_file).arrayBuffer().then((content) => {
            return JSON.parse((new TextDecoder()).decode(content))
        })
        this.tabs = await this.extractTabs(tabs, false)

        this.initRepProps()
        this.fetchFailed = false
    }

    constructor () {
        super()
        // The report page will first attempt to use the 'Fetch' API to retreive report resources.
        // If it fails to use fetch 'fetchFailed' will become 'true'. This then tells the template
        // to suggest the user uploads their report directory.
        this.fetchFailed = false

        // 'reportInfo' is an 'Object' representation of the JSON contents of 'report_info.json'.
        this.reportInfo = {}
    }

    render () {
        if (this.fetchFailed) {
            return this.corsWarning()
        }

        return html`
            <div class="report-head">
                ${this.toolname ? html`<h1 class="report-title">${this.toolname} report</h1>` : html``}
                ${this.titleDescr
                    ? html`
                        <p class="title_descr">${this.titleDescr}</p>
                        <br>
                    `
                    : html``
                }
                ${this.introtbl ? html`<sc-intro-tbl .file=${this.introtbl}></sc-intro-tbl>` : html``}
            </div>
            <br>
            ${this.tabs ? html`<sc-tab-group .tabs=${this.tabs}></sc-tab-group>` : html``}
        `
    }
}

customElements.define('sc-report-page', ScReportPage)
