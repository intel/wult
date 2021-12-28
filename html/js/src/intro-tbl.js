/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import {html} from 'lit';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { ReportTable } from './report-table.js';

/**
 * Responsible for generating the 'Intro Table' which contains information on the report.
 * @class IntroTable
 * @extends {LitElement}
 */
class IntroTable extends ReportTable {
    static properties = {
        introtbl: {type: Object},
    };

    constructor() {
        super();
    }

    render() {
        return this.introtbl
        ? html`
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
                    if (key1 != "Title"){
                        return html`<td class="td-value"> ${unsafeHTML(String(val1[key]))} </td>`
                    }})}
                </tr>
                `)}
            </table>
        `
        : html``
    }
}

customElements.define('intro-tbl', IntroTable);
