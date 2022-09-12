/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { until } from 'lit/directives/until.js'
import { LitElement, css, html } from 'lit'

export class InvalidTableFileException {
    constructor (msg) {
        this.message = msg
        this.name = 'InvalidTableFileException'
    }
}

/**
 * Contains CSS and helper functions for tables.
 * @class Table
 * @extends {LitElement}
 */
export class ScReportTable extends LitElement {
    static properties = {
        file: { type: File },
        template: { attribute: false }
    };

    static styles = css`
        table {
            table-layout: fixed;
            border-collapse: collapse;
            width: auto;
        }

        table th {
            font-family: Arial, sans-serif;
            font-size: 15px;
            font-weight: bold;
            padding: 10px 5px;
            border-style: solid;
            border-width: 1px;
            overflow: hidden;
            word-break: normal;
            border-color: black;
            text-align: center;
            background-color: rgb(161, 195, 209);
        }

        table td {
            font-family: Arial, sans-serif;
            font-size: 14px;
            padding: 5px 10px;
            border-style: solid;
            border-width: 1px;
            overflow: hidden;
            word-break:normal ;
            border-color:black;
            background-color: rgb(237, 250, 255);
        }

        table .td-colname {
            font-size: 15px;
            font-weight: bold;
            text-align: left;
        }

        table .td-value {
            text-align: left;
        }

        table .td-funcname {
            text-align: left;
        }
    `;

    /**
     * Returns pixel width of table based on the number of columns in the table.
     * @param {Number} ncols number of columns in the table.
     * @return {Number} number of pixels to set the width of the table to.
     */
    getWidth (ncols) {
        return Math.min(100, 20 * (ncols - 2))
    }

    /**
     * Generator of lines within the file at URL 'fileURL'.
     */
    async * makeTextFileLineIterator (file) {
        const utf8Decoder = new TextDecoder('utf-8')
        const reader = file.stream().getReader()
        let { value: chunk, done: readerDone } = await reader.read()
        chunk = chunk ? utf8Decoder.decode(chunk, { stream: true }) : ''

        const re = /\r\n|\n|\r/gm
        let startIndex = 0

        for (;;) {
            const result = re.exec(chunk)
            if (!result) {
                if (readerDone) {
                    // Stop the generator if the whole file has been parsed.
                    break
                }

                // No new-line found but reader has not finished parsing file so call 'read()' and wait for
                // the reader to return more of the file. Then process that combined with any remaining
                // unprocessed file content.
                const remainder = chunk.substr(startIndex);
                ({ value: chunk, done: readerDone } = await reader.read())
                chunk = remainder + (chunk ? utf8Decoder.decode(chunk, { stream: true }) : '')
                startIndex = re.lastIndex = 0
                continue
            }

            // New-line found, so return substring from after the previous new-line to this new-line.
            yield chunk.substring(startIndex, result.index)
            startIndex = re.lastIndex
        }

        if (startIndex < chunk.length) {
            // End of file reached and no more new-line characters found so yield any remaining unprocessed
            // content.
            yield chunk.substr(startIndex)
        }
    }

    render () {
        if (!this.file) {
            return html``
        }

        const template = this.parseSrc()
        return html`${until(template, html``)}`
    }
}

customElements.define('sc-report-table', ScReportTable)
