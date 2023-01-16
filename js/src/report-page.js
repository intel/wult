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
import '@shoelace-style/shoelace/dist/components/divider/divider'
import '@shoelace-style/shoelace/dist/components/dialog/dialog'

import './intro-tbl'
import './tab-group'

/**
 * Convert a 'tabName' to a valid HTML element ID.
 */
function convertToValidID (tabName) {
    return tabName
        .replace(/\s/g, '-')
        .replace('%', 'Percent')
        .replace(/[^a-zA-Z0-9-]+/g, '')
}

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
            font-family: Arial, sans-serif;
        }

        .cors-warning {
            display: flex;
            flex-direction: column;
            font-family: Arial, sans-serif;
        }

        .sticky {
            position: sticky;
            top: 0;
            height: 100vh;
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
        this.reportTitle = this.reportInfo.title
        this.reportDescr = this.reportInfo.descr
    }

    generateTabIDs (tabs) {
        for (const tab of tabs) {
            if (tab.tabs) {
                tab.tabs = this.generateTabIDs(tab.tabs)
            }
            const id = convertToValidID(tab.name)
            if (this.tabIDs.has(id)) {
                this.tabIDs.set(id, this.tabIDs.get(id) + 1)
                tab.id = `${id}-${this.tabIDs.get(id)}`
            } else {
                this.tabIDs.set(id, 0)
                tab.id = id
            }
        }
        return tabs
    }

    parseReportInfo (json) {
        this.reportInfo = json
        this.initRepProps()

        // Fetch intro table.
        if (json.intro_tbl) {
            fetch(json.intro_tbl)
                .then(resp => resp.blob())
                .then(blob => { this.introtbl = blob })
        }

        // Fetch tabs file.
        fetch(json.tab_file).then(resp => resp.json())
            .then(async tabjson => { this.tabs = this.generateTabIDs(tabjson) })
    }

    connectedCallback () {
        fetch(this.src)
            .then(resp => resp.json())
            .then(json => this.parseReportInfo(json))
            .catch(err => {
                // Catching a CORS error caused by viewing reports locally.
                if (err instanceof TypeError) {
                    this.fetchFailed = true
                } else {
                    throw err
                }
            })
        super.connectedCallback()
    }

    updated (changedProperties) {
        if (changedProperties.has('fetchFailed')) {
            if (this.fetchFailed) {
                // Prevent the dialog from closing.
                this._corsWarning.addEventListener('sl-request-close', event => {
                    event.preventDefault()
                })
            }
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
                    tab.smrytblfile = await fetch(tab.smrytblpath).then((resp) => resp.blob())
                } else {
                    tab.smrytblfile = this.findFile(tab.smrytblpath)
                }
            }
            if (tab.tabs) {
                tab.tabs = await this.extractTabs(tab.tabs, useFetch)
            }
        }
        return this.generateTabIDs(tabs)
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

        // 'tabIDs' maps tab IDs to a count of how many tabs have that ID. This is used to avoid
        // duplicates IDs. If 3 tabs have the same ID 'tabName', then each one will be given ID
        // 'tabName', 'tabName-1', 'tabName-2' separately.
        this.tabIDs = new Map()
    }

    render () {
        if (this.fetchFailed) {
            return this.corsWarning()
        }

        return html`
            <div class="report-head">
                ${this.reportTitle ? html`<h1>${this.reportTitle}</h1>` : html``}
                ${this.reportDescr
                    ? html`
                        <p>${this.reportDescr}</p>
                    `
                    : html``
                }
                ${this.introtbl ? html`<sc-intro-tbl .file=${this.introtbl}></sc-intro-tbl>` : html``}
            </div>
            <br>
            <div class="sticky">
                ${this.tabs ? html`<sc-tab-group .tabs=${this.tabs}></sc-tab-group>` : html``}
            </div>
        `
    }
}

customElements.define('sc-report-page', ScReportPage)
