/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html } from 'lit'
import { ReportTable } from './report-table.js'

/**
 * Responsible for generating the summary table for a given metric.
 * @class SummaryTable
 * @extends {ReportTable}
 */
class SummaryTable extends ReportTable {
    static properties = {
      smrystbl: { type: Object }
    };

    /**
     * Returns the HTML template for the headers of the summary table.
     * @return {TemplateResult} <tr> element containing table headers with the sets of results used
     *                          and 'Title' header.
     */
    headerTemplate () {
      return html`
            <tr>
                ${Object.keys(this.smrystbl).map((header) => {
                    let colspan
                    if (header === 'Title') {
                        colspan = 2
                    } else {
                        colspan = ''
                    }
                    return html`<th colspan="${colspan}">${header}</th>`
                }
                )}
            </tr>
        `
    }

    rowsTemplate () {
      return html`
            ${Object.entries(this.smrystbl.Title).map(([colname, titleDict]) =>
                Object.entries(titleDict.funcs).map(([funcname, funcdescr], i) =>
                    /*
                     * For each row:
                     *  1. Add cell with function name and desc (e.g. max, min etc.)
                     *  2. Add function value (usually a number)
                     */
                    html`<tr>
                        ${!i
? html`
                            <td class="td-colname" rowspan="${Object.keys(titleDict.funcs).length}">
                                <abbr title="${titleDict.coldescr}">${titleDict.metric}</abbr>
                            </td>
                        `
: html``}
                        <td class="td-funcname">
                            <abbr title="${funcdescr}">${funcname}</abbr>
                        </td>
                        ${Object.entries(this.smrystbl).map(([key, resDict]) => {
                            if (key === 'Title') {
                                return html``
                            }
                            const fdict = resDict[colname].funcs[funcname]
                            return html`
                            <td class="td-value">
                                <abbr title="${fdict.hovertext}">${fdict.val}</abbr>
                            </td>
                            `
                        }
                        )}
                    </tr>
                    `
                )
            )}
        `
    }

    render () {
      return this.smrystbl
        ? html`
            <table width="${this.getWidth(this.smrystbl)}%">
            ${this.headerTemplate()}
            ${this.rowsTemplate()}
            </table>
        `
        : html``
    }
}

customElements.define('smry-tbl', SummaryTable)
