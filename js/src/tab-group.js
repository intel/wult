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
import '@shoelace-style/shoelace/dist/components/alert/alert'
import '@shoelace-style/shoelace/dist/components/tab-group/tab-group'
import '@shoelace-style/shoelace/dist/components/tab/tab'
import '@shoelace-style/shoelace/dist/components/tab-panel/tab-panel'

import './data-tab'

/**
 * Responsible for generating a group of tabs and their contents.
 * @class TabGroup
 * @extends {LitElement}
 */
class ScTabGroup extends LitElement {
    static styles = css`
        /*
         * By default, inactive Shoelace tabs have 'display: none' which breaks Plotly legends.
         * Therefore we make inactive tabs invisible in our own way using the following two css
         * classes:
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

        /*
         * The hierarchy of tabs can go up to and beyond 5 levels of depth. Remove the padding on
         * tab panels so that there is no space between each level of tabs.
         */
        .tab-panel::part(base) {
            padding: 0px 0px;
        }
        /*
         * Also reduce the bottom padding of tabs as it makes them easier to read.
         */
        .tab::part(base) {
            padding-bottom: var(--sl-spacing-x-small);
            font-family: Arial, sans-serif;
        }
    `

    static properties = {
        tabs: { type: Object }
    };

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
                        <sl-tab class="tab" slot="nav" panel="${innerTab.name}">${innerTab.name}</sl-tab>
                        <sl-tab-panel class="tab-panel" id="${innerTab.name}" name="${innerTab.name}">${this.tabTemplate(innerTab)}</sl-tab-panel>
                    `)}
                </sl-tab-group>
        `
        }
        return html`
            <sc-data-tab tabname=${tab.name} .smrytblpath=${tab.smrytblpath} .smrytblfile=${tab.smrytblfile} .paths=${tab.ppaths} .fpreviews=${tab.fpreviews} .dir=${tab.dir}></sc-data-tab>
        `
    }

    render () {
        if (!this.tabs) {
            return html``
        }

        return html`
            <sl-tab-group>
                ${this.tabs.map((tab) => html`
                    <sl-tab class="tab" slot="nav" panel="${tab.name}">${tab.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${tab.name}">${this.tabTemplate(tab)}</sl-tab-panel>
                `)}
            </sl-tab-group>
      `
    }
}

customElements.define('sc-tab-group', ScTabGroup)
