/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2021-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html } from 'lit'
import { ReportTable } from './report-table.js'

/**
 * Generator of lines within the file at URL 'fileURL'.
 */
async function * makeTextFileLineIterator (fileURL) {
  const utf8Decoder = new TextDecoder('utf-8')
  const response = await fetch(fileURL)
  const reader = response.body.getReader()
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

/**
 * Responsible for generating the summary table for a given metric.
 * @class SummaryTable
 * @extends {ReportTable}
 */
class SummaryTable extends ReportTable {
    static properties = {
      src: { type: String },
      template: { attribute: false }
    };

    /**
     * Helper function for 'parseSrc()'. Converts the semi-colon separated values of a metric line
     * in the summary table text format to its HTML template.
     * @param {Array<String>} values - the values which were semi-colon separated parsed into an Array<String>.
     * @returns {TemplateLiteral}
     */
    parseMetric (values) {
      const cellAttrs = values[0].split('|')
      return html`
        <td rowspan=${values[1]} class="td-colname">
            <abbr title=${cellAttrs[1]}>${cellAttrs[0]}</abbr>
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
            <abbr title=${hover}>${contents}</abbr>
        </td>
      `
    }

    /**
     * Parse the summary table from the source file located at 'this.src'.
     */
    async parseSrc () {
      let template = html``
      let metricCell

      for await (const line of makeTextFileLineIterator(this.src)) {
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
          const funcCells = html`
            ${values.map((val) => this.parseSummaryFunc(val))}
          `

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
      return template
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

    /**
     * Returns pixel width of table based on the number of sets of results shown in the report.
     * @return {Number} no. of pixels to set the width of the table to.
     */
    getWidth () {
      return Math.min(100, 20 * (this.cols - 2))
    }

    render () {
      return this.template
        ? html`
            <table width="${this.getWidth(this.smrystbl)}%">
            ${this.template}
            </table>
        `
        : html``
    }
}

customElements.define('smry-tbl', SummaryTable)
