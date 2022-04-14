/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2019-2021 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html, css } from 'lit'
import { WultTab } from './wult-tab.js'

import './diagram-element.js'

/**
 * Responsible for generating all content contained within a statistics tab.
 * @class StatsTab
 * @extends {LitElement}
 */
class StatsTab extends WultTab {
    static styles = css`
        .grid {
            display: grid;
            width: 100%;
            grid-auto-rows: 800px;
            grid-auto-flow: dense;
        }
    `;

    connectedCallback () {
        super.connectedCallback()
        /*
         * DOM-based inputs are only parsed once the component has been 'connected' therefore this
         * is the earliest point to load the input into class attributes.
         */
        this.paths = this.info.ppaths
        this.smrystbl = this.info.smrys_tbl
    }

    /**
     * Provides the template for when the tab is visible (active).
     * @returns {TemplateResult}
     */
    visibleTemplate () {
        return html`
        <br>
        <wult-metric-smry-tbl .smrystbl="${this.smrystbl}"></wult-metric-smry-tbl>
        <div class="grid">
        ${this.paths.map((path) =>
            html`<diagram-element path="${path}" ></diagram-element>`
        )}
        </div>
        `
    }
}

customElements.define('stats-tab', StatsTab)
