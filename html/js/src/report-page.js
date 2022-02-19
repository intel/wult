/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { LitElement, html } from 'lit'

import './intro-tbl'
import './tab-group'

/**
 * Contains CSS and helper functions for tables.
 * @class StatsPage
 * @extends {LitElement}
 */
export class ReportPage extends LitElement {
    static properties = {
      src: { type: String },
      reportInfo: { type: Object, attribute: false }
    }

    async connectedCallback () {
      super.connectedCallback()
      const resp = await fetch(this.src)
      this.reportInfo = await resp.json()
      this.toolname = this.reportInfo.toolname
      this.titleDescr = this.reportInfo.title_descr
      this.tabFile = this.reportInfo.tab_file
      this.introtbl = this.reportInfo.intro_tbl
    }

    render () {
      return html`
        <h1>${this.toolname} report</h1>
        <br>

        ${this.titleDescr
        ? html`
        <p class="title_descr">${this.titleDescr}</p>
        <br>
        `
        : html``
        }


        <intro-tbl .introtbl='${this.introtbl}'></intro-tbl>
        <br>

        <tab-group .tabFile="${this.tabFile}"></tab-group>
        `
    }
}

customElements.define('report-page', ReportPage)
