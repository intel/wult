/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import {LitElement, html, css} from 'lit';

class WultMetricSmryTbl extends LitElement {
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

    static properties = {
        smrystbl: {type: Object},
    };

    getWidth() {
        let nkeys = Object.keys(this.smrystbl).length;
        return Math.min(100, 20 * nkeys);
    }

    constructor() {
        super();
    }

    headerTemplate() {
        return html`
            <tr>
                ${Object.keys(this.smrystbl).map((header) =>{
                    var colspan;
                    if (header == "Title"){
                        colspan = 2;
                    }
                    else {
                        colspan = '';
                    }
                    return html`<th colspan="${colspan}">${header}</th>`
                }
                )}
            </tr>
        `
    }

    rowsTemplate() {
        return html`
            ${Object.entries(this.smrystbl["Title"]).map(([colname, title_dict]) =>
                Object.entries(title_dict["funcs"]).map(([funcname, funcdescr], i) =>
                    /*
                     * For each row:
                     *  1. Add cell with function name and desc (e.g. max, min etc.)
                     *  2. Add function value (usually a number)
                     */
                    html`<tr>
                        ${!i ? html`
                            <td class="td-colname" rowspan="${Object.keys(title_dict["funcs"]).length}">
                                <abbr title="${title_dict["coldescr"]}">${title_dict["metric"]}</abbr>
                            </td>
                        `: html``}
                        <td class="td-funcname">
                            <abbr title="${funcdescr}">${funcname}</abbr>
                        </td>
                        ${Object.entries(this.smrystbl).map(([key, res_dict]) => {
                            if (key == "Title"){
                                return html``
                            }
                            const fdict = res_dict[colname]["funcs"][funcname];
                            return html`
                            <td class="td-value">
                                <abbr title="${fdict["hovertext"]}">${fdict["val"]}</abbr>
                            `
                        }
                        )}
                    </tr>
                    `
                )
            )}
        `
    }

    render() {
        return this.smrystbl
        ? html`
            <table width="${this.getWidth()}%">
            ${this.headerTemplate()}
            ${this.rowsTemplate()}
            </table>
        `
        : html``
    }
}

customElements.define('wult-metric-smry-tbl', WultMetricSmryTbl);
