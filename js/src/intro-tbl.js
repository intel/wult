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
 * Responsible for generating the 'Intro Table' which contains information on the report.
 * @class IntroTable
 * @extends {ReportTable}
 */
class IntroTable extends ReportTable {
    static properties = {
      introtbl: { type: Object }
    };

    render () {
      if (!this.introtbl) {
        return html``
      }

      this.link_keys = this.introtbl.link_keys
      delete this.introtbl.link_keys

      // If a link is not available, then it is because the original link pointed outside of the
      // report directory. In this case, we should let the report viewer know how they can keep the
      // links with the '--relocatable' option.
      const noLinkHovertext = 'Regenerate the report with "wult report --relocatable" to copy ' +
                              'statistics and results to the report directory.'

      return html`
        <table width="${this.getWidth(this.introtbl)}%">
        <tr>
        ${Object.keys(this.introtbl).map((header) => {
            return html`<th>${header} </th>`
        })}
        </tr>
        ${Object.entries(this.introtbl.Title).map(([key, val]) =>
            html`
            <tr>
            <td class="td-colname"> ${val} </td>
            ${Object.entries(this.introtbl).map(([key1, val1]) => {
                if (key1 !== 'Title') {
                    return html`<td class="td-value"> ${
                        (this.link_keys.includes(key))
                        ? val1[key]
                            ? html`<a href=${val1[key]}> ${val} </a>`
                            : html`<abbr title=${noLinkHovertext}>Not available</abbr>`
                        : val1[key]} </td>`
                }
                return html``
            })}
            </tr>
        `)}
        </table>
      `
    }
}

customElements.define('intro-tbl', IntroTable)
