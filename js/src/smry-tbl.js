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
import { ReportTable } from './report-table.js'
import '@shoelace-style/shoelace/dist/components/details/details.js'

/**
 * Responsible for generating the summary table for a given metric.
 * @class SummaryTable
 * @extends {ReportTable}
 */
class SummaryTable extends ReportTable {
    static styles = [
        ReportTable.styles,
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
        return html`<table width=${this.getWidth(this.cols)}>${template}</table>`
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
