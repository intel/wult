/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { html, css, LitElement } from 'lit'
import '@shoelace-style/shoelace/dist/components/tab-group/tab-group'
import '@shoelace-style/shoelace/dist/components/tab/tab'
import '@shoelace-style/shoelace/dist/components/tab-panel/tab-panel'

import './wult-metric-tab'

/**
 * Responsible for generating a group of tabs and their contents.
 * @class TabGroup
 * @extends {LitElement}
 */
class TabGroup extends LitElement {
    static styles = css`
      /*
      * By default, inactive Shoelace tabs have 'display: none' which breaks Plotly
      * legends. Therefore we make inactive tabs invisible in our own way using the
      * following two css classes:
      */
      sl-tab-panel{
        display: block !important;
        height: 0px !important;
        overflow: hidden;
      }

      sl-tab-panel[active] {
        display: block !important;
        height: auto !important;
      }
    `

    static properties = {
      tabFile: { type: String },
      tabs: { type: Object, attribute: false }
    };

    connectedCallback () {
      super.connectedCallback()
      // Once this component is attached to the DOM, 'tabFile' should be populated and we can read
      // the data from it and load it into the underlying 'tabs' property.
      fetch(this.tabFile)
        .then((response) => response.json())
        .then(data => { this.tabs = data })
    }

    /**
     * Returns the HTML template for a given Tab object.
     * @param {Object} tab: Tab object from the Python side.
     */
    tabTemplate (tab) {
      // If this tab contains children tabs then create a child tab group and insert the child tabs.
      if (tab.tabs) {
        return html`
          <sl-tab-group>
            ${tab.tabs.map((innerTab) => html`
             <sl-tab slot="nav" panel="${innerTab.name}">${innerTab.name}</sl-tab>
             <sl-tab-panel id="${innerTab.name}" name="${innerTab.name}">${this.tabTemplate(innerTab)}</sl-tab-panel>
             `)}
          </sl-tab-group>
        `
      }
      return html`
      <wult-metric-tab tabname="${tab.name}" .smrytblpath="${tab.smrytblpath}" .paths="${tab.ppaths}" .dir="${tab.dir}" ></wult-metric-tab>
      `
    }

    render () {
      return this.tabs
        ? html`
            <sl-tab-group>
              ${this.tabs.map((tab) =>
                html`
                  <sl-tab slot="nav" panel="${tab.name}">${tab.name}</sl-tab>
                  <sl-tab-panel name="${tab.name}">${this.tabTemplate(tab)}</sl-tab-panel>
                `
              )}
            </sl-tab-group>
          `
        : html``
    }
}

customElements.define('tab-group', TabGroup)
