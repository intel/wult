/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html, css } from 'lit'
import { WultTab } from './wult-tab.js'

import './diagram.js'
import './file-preview'
import './smry-tbl'

/**
 * Responsible for generating all content contained within a metric tab.
 * @class WultMetricTab
 * @extends {LitElement}
 */
class WultMetricTab extends WultTab {
    static styles = css`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
  `;

    static properties = {
        paths: { type: Array },
        fpreviews: { type: Array },
        smrytblpath: { type: String }
    }

    /**
     * Provides the template for when the tab is visible (active).
     */
    visibleTemplate () {
        return html`
            <br>
            ${this.smrytblpath ? html`<sc-smry-tbl .src="${this.smrytblpath}"></sc-smry-tbl>` : html``}
            ${this.fpreviews
                ? this.fpreviews.map((fpreview) => html`
                    <sc-file-preview .title=${fpreview.title} .diff=${fpreview.diff} .paths=${fpreview.paths}></sc-file-preview>
                    <br>
                `)
                : html``
            }
            <div class="grid">
                ${this.paths
                    ? this.paths.map((path) => html`
                    <sc-diagram path="${path}"></sc-diagram>
                    `)
                    : html``}
            </div>
        `
    }

    render () {
        return super.render()
    }
}

customElements.define('wult-metric-tab', WultMetricTab)
