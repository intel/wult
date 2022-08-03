/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2021-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html, css } from 'lit'
import { createRef, ref } from 'lit/directives/ref.js'
import { ScReportTable } from './report-table.js'
import '@shoelace-style/shoelace/dist/components/details/details.js'
import '@shoelace-style/shoelace/dist/components/button/button.js'

/**
 * Responsible for generating the summary table for a given metric.
 * @class SummaryTable
 * @extends {ScReportTable}
 */
class SummaryTable extends ScReportTable {
    static styles = [
        ScReportTable.styles,
        // Add CSS for 'sl-details' in metric cells which contain metric descriptions.
        css`
        sl-details::part(base) {
            max-width: 30vw;
            font-family: Arial, sans-serif;
            background-color: transparent;
            border: none;
        }
        sl-details::part(header) {
            font-weight: "bold";
            padding: var(--sl-spacing-x-small) var(--sl-spacing-4x-large) var(--sl-spacing-x-small) var(--sl-spacing-x-small);
            font-size: 12px;
        }
        `
    ]

    // Add a 'ref' to the '<table>' element of the summary table.
    tableRef = createRef()

    /**
     * Removes 'sl-details' nodes containing metric descriptions.
     * @param tableEl - DOM Element containing summary table.
     */
    removeDetailsEl (tableEl) {
        for (const child of tableEl.childNodes) {
            if (child.tagName === 'TR') {
                for (const grandChild of child.childNodes) {
                    for (const cellNode of grandChild.childNodes) {
                        if (cellNode.tagName === 'SL-DETAILS') {
                            grandChild.removeChild(cellNode)
                        }
                    }
                }
            }
        }

        return tableEl
    }

    /**
     * Copy the summary table to the clipboard. Excludes metric descriptions from the copied HTML.
     */
    copyTable () {
        const sel = window.getSelection()

        // Ignore any content which is already selected.
        sel.removeAllRanges()

        // Select a 'Range' containing the table element.
        const range = document.createRange()
        range.selectNodeContents(this.tableRef.value)
        sel.addRange(range)

        // Remove the 'sl-details' nodes containing metric descriptions, then copy.
        this.removeDetailsEl(sel.anchorNode)
        document.execCommand('copy')

        // Deselect everything.
        sel.removeAllRanges()
        this.requestUpdate()
    }

    /**
     * Helper function for 'parseSrc()'. Converts the semi-colon separated values of a metric line
     * in the summary table text format to its HTML template.
     * @param {Array<String>} values - the values which were semi-colon separated parsed into an Array<String>.
     * @returns {TemplateLiteral}
     */
    parseMetric (values) {
        const cellAttrs = values[0].split('|')
        return html`
            <td rowspan=${values[1]}>
                <strong>${cellAttrs[0]}</strong>
                <sl-details summary="Description">
                    ${cellAttrs[1]}
                </sl-details>
            </td>
        `
    }

    /**
     * Helper function for 'parseSrc()'. Converts a summary function line in the text format to its
     * HTML template.
     * @param {String} cell - cell representation from the summary table file.
     * @returns {TemplateLiteral}
     */
    parseSummaryFunc (cell) {
        const [contents, hover] = cell.split('|')
        return html`
            <td class="td-value">
                ${hover ? html`<abbr title=${hover}>${contents}</abbr>` : html`${contents}`}
            </td>
        `
    }

    /**
     * Parse the summary table from the source file located at 'this.src'.
     */
    async parseSrc () {
        let template = html``
        let metricCell

        for await (const line of this.makeTextFileLineIterator(this.src)) {
            const values = line.split(';')

            // Extract the type of row this line represents (always represented by the first value).
            // Then shift the values so that only the cell values remain.
            const rowType = values[0]
            values.shift()

            if (rowType === 'H') {
                // Header row.
                for (const header of values) {
                    template = html`${template}<th>${header}</th>`
                    this.cols = this.cols + 1
                }
            } else if (rowType === 'M') {
                // Metric row.
                metricCell = this.parseMetric(values)
            } else {
                // Summary function row.
                const funcCells = html`${values.map((val) => this.parseSummaryFunc(val))}`

                template = html`
                    ${template}
                    <tr>
                      ${metricCell}
                      ${funcCells}
                    </tr>
                `
                // Each metric should only be added once to the table as it stretches over all of the
                // functions which are calculated on that metric.
                if (metricCell) {
                    metricCell = undefined
                }
            }
        }
        template = html`<table ${ref(this.tableRef)} width=${this.getWidth(this.cols)}>${template}</table>`

        // Add button to copy table to clipboard.
        return html`
            <div style="display:flex;">
                ${template}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `
    }

    constructor () {
        super()
        this.cols = 0
    }

    connectedCallback () {
        super.connectedCallback()
        this.parseSrc()
            .then((template) => {
                this.template = template
            })
    }
}

customElements.define('smry-tbl', SummaryTable)
