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
import '@shoelace-style/shoelace/dist/components/tree/tree'
import '@shoelace-style/shoelace/dist/components/tree-item/tree-item'
import '@shoelace-style/shoelace/dist/components/split-panel/split-panel'

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
     * Convert a 'tabName' to a valid CSS selector name.
     */
    convertToSelector (tabName) {
        return tabName.replace(/\s/g, '-').replace(/[^a-zA-Z0-9-]+/g, '')
    }

    /**
     * Checks if there is a hash in the URL when the page is first loaded and opens the appropriate
     * tab if necessary.
     */
    firstUpdated () {
        const hash = location.hash
        if (hash) {
            const tabGroup = this.renderRoot.querySelector('sl-tab-group')
            tabGroup.updateComplete.then(() => {
                tabGroup.show(this.subtabs[hash.substring(1)])
            })
            this.firstTab = this.subtabs[hash.substring(1)]
            const targetElement = this.renderRoot.querySelector(hash)
            this.currentEl = targetElement
            targetElement.hidden = false
        }
    }

    /**
     * Checks if the current URL includes a hash e.g. "report/#WakeLatency" and updates the visible
     * tab accordingly.
     */
    updateVisibleTab () {
        if (this.currentEl) {
            this.currentEl.hidden = true
        }
        const targetElement = this.renderRoot.querySelector(location.hash)
        this.currentEl = targetElement
        if (targetElement) {
            targetElement.hidden = false
        }
    }

    connectedCallback () {
        super.connectedCallback()
        this.hashHandler = this.updateVisibleTab.bind(this)
        window.addEventListener('hashchange', this.hashHandler, false)
    }

    disconnectedCallback () {
        window.removeEventListener('hashchange', this.hashHandler)
    }

    /**
     * Returns the HTML template for tab panes which consist of the contents of tabs in 'tab'.
     * */
    tabPanesTemplate (tab) {
        let dataTabs = html``
        for (const innerTab of tab.tabs) {
            if (innerTab.tabs) {
                dataTabs = html`${dataTabs}${this.tabPanesTemplate(innerTab)}`
            } else {
                dataTabs = html`${dataTabs}<sc-data-tab hidden id="${this.convertToSelector(innerTab.name)}" tabname=${innerTab.name} .smrytblpath=${innerTab.smrytblpath} .smrytblfile=${innerTab.smrytblfile} .paths=${innerTab.ppaths} .fpreviews=${innerTab.fpreviews} .dir=${innerTab.dir}></sc-data-tab>`
            }
        }
        return dataTabs
    }

    /**
     * Returns the HTML template for a tree-item in the tab navigation tree.
     * @param {Object} tab: Tab object from the Python side.
     * @param {string} parentTabName: the tab to associate the child tree items with.
     */
    treeItemTemplate (tab, parentTabName) {
        // Recursive base case: the contents of a tree item is just the name.
        if (!tab.tabs) {
            this.subtabs[this.convertToSelector(tab.name)] = parentTabName
            return tab.name
        }
        /* If this tree item contains children then create tree items for each one.
         * The ternary operator in this template states that if 'innerTab' is a leaf node in the
         * tree, assign a listner for 'click' events which redirects to the relevant tab.
         */
        return html`
                ${tab.name}
                ${tab.tabs.map((innerTab) => html`
                    <sl-tree-item @click=${innerTab.tabs
                        ? () => {}
                        : () => { location.hash = this.convertToSelector(innerTab.name) }}>
                        ${this.treeItemTemplate(innerTab, parentTabName)}
                    </sl-tree-item>
            `)}
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
                    <sl-tab-panel class="tab-panel" name="${tab.name}">
                        <sl-split-panel position=20 style="--divider-width: 20px;">
                            <sl-tree selection="leaf" slot="start">
                                ${this.treeItemTemplate(tab, tab.name)}
                            </sl-tree>
                            <div style="height: 95vh; overflow:scroll;" slot="end">
                                ${this.tabPanesTemplate(tab)}
                            </div>
                        </sl-split-panel>
                    </sl-tab-panel>
                `)}
            </sl-tab-group>
      `
    }

    constructor () {
        super()
        // This dictionary tracks which sub-tab belongs to which tab. This is so the right tab can
        // be opened to show the sub-tab.
        this.subtabs = {}
    }
}

customElements.define('sc-tab-group', ScTabGroup)
