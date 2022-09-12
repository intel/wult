/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html } from 'lit'
import { ScReportTable, InvalidTableFileException } from './report-table.js'

/**
 * Responsible for generating the 'Intro Table' which contains information on the report.
 * @class ScIntroTable
 * @extends {ScReportTable}
 */
class ScIntroTable extends ScReportTable {
    /**
     * Parse a header line from the intro table file into a HTML template.
     * @param {String} line A header line from the intro table text file.
     * @returns {HTMLTemplate} Template containing HTML representation of the original line of text.
     */
    parseHeader (line) {
        const headers = line.split(';')
        return html`
            <tr>
                ${headers.map((header) => html`<th>${header}</th>`)}
            </tr>
        `
    }

    /**
     * Parse a line from the intro table file into a HTML template which represents a table row.
     * @param {String} line A line from the intro table text file which represents a row.
     * @returns {HTMLTemplate} Template containing HTML representation of the original line of text.
     */
    parseRow (line) {
        let template = html``
        let first = true
        for (const cell of line.split(';')) {
            const [value, hovertext, link] = cell.split('|')
            let cellTempl = html`${value}`
            if (link) {
                cellTempl = html`<a href=${link}>${cellTempl}</a>`
            }
            if (hovertext) {
                cellTempl = html`<abbr title=${hovertext}>${cellTempl}</abbr>`
            }

            if (first) {
                template = html`${template}
                    <td class="td-colname">
                        ${cellTempl}
                    </td>
                `
                first = false
            } else {
                template = html`${template}
                    <td>
                        ${cellTempl}
                    </td>
                `
            }
        }
        return html`<tr>${template}</tr>`
    }

    /**
     * Parse the intro table from the source file 'this.file'.
     */
    async parseSrc () {
        const lines = this.makeTextFileLineIterator(this.file)
        let header = await lines.next()
        header = header.value

        // Check that the first line is a header.
        if (!header.startsWith('H;')) {
            throw new InvalidTableFileException('first line in intro table file should be a ' +
                                                'header.')
        }

        header = header.slice(2)
        let template = this.parseHeader(header)

        for await (let line of lines) {
            // Check that subsequent lines are normal table rows.
            if (!line.startsWith('R;')) {
                throw new InvalidTableFileException('lines following the first should all be ' +
                                                    'normal table rows.')
            }
            line = line.slice(2)
            template = html`${template}${this.parseRow(line)}`
        }
        return html`<table>${template}</table>`
    }
}

customElements.define('sc-intro-tbl', ScIntroTable)
