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

    connectedCallback () {
      super.connectedCallback()
      /*
         * DOM-based inputs are only parsed once the component has been 'connected' therefore this
         * is the earliest point to load the input into class attributes.
         */
      this.paths = this.info.ppaths
      this.smrystblpath = this.info.smrytblpath
    }

    /**
     * Provides the template for when the tab is visible (active).
     */
    visibleTemplate () {
      return html`
            <br>
            <smry-tbl .src="${this.smrystblpath}"></smry-tbl>
            <div class="grid">
            ${this.paths.map((path) =>
                    html`<diagram-element path="${path}" ></diagram-element>`
            )}
            </div>
        `
    }

    render () {
      return super.render()
    }
}

customElements.define('wult-metric-tab', WultMetricTab)
