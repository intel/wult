/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

/**
 * @license
 * Copyright (C) 2022-2023 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 */

import { LitElement, html } from 'lit'
import '@shoelace-style/shoelace/dist/components/tree/tree'
import '@shoelace-style/shoelace/dist/components/tree-item/tree-item'
import '@shoelace-style/shoelace/dist/components/split-panel/split-panel'

import './data-tab'

/**
 * Populates the tab-panels with a tab-tree for naviagation and data-tabs.
 * @class ScTabPanel
 * @extends {LitElement}
 */
class ScTabPanel extends LitElement {
    static properties = {
        tab: { type: Object }
    }

    /**
     * Select a tab represented by 'tabID' in the tab-tree and expand the tree if necessary to
     * reveal the tab leaf-node.
     * @param {string} tabID - the element ID of the tab to select.
     */
    selectTabInTabTree (tabID) {
        // Deselect any pre-selected tabs.
        const selectedEls = this.renderRoot.querySelectorAll('sl-tree-item[selected]')
        for (const el of selectedEls) {
            el.selected = false
        }

        // Collapse any expanded tree items.
        const expandedEls = this.renderRoot.querySelectorAll('sl-tree-item[expanded]')
        for (const el of expandedEls) {
            el.expanded = false
        }

        // Select the tree item representing the tab with 'tabID'.
        let treeEl = this.renderRoot.getElementById(`${tabID}-tree`)
        treeEl.selected = true

        // Expand all of the non-leaf nodes needed to reveal 'treeEl'.
        while (treeEl.tagName === 'SL-TREE-ITEM') {
            treeEl.expanded = true
            treeEl = treeEl.parentElement
        }
    }

    /**
     * Check if this tab panel contains the data-tab represented by 'dataTabID'.
     * @param {string} dataTabID - the ID of a data-tab.
     * @returns a boolean reflecting if the data-tab represented by 'dataTabID' is
     * contained in this panel.
     */
    hasDataTab (dataTabID) {
        return this.dataTabs.includes(dataTabID)
    }

    /**
     * Show the data-tab with ID 'dataTabID'.
     * @param {string} dataTabID - the ID of the tab to show.
     */
    show (dataTabID) {
        // If the data-tab is not contained by this tab-panel, don't do anything.
        if (!this.hasDataTab(dataTabID)) {
            return
        }

        // If the requested data-tab is already shown by this tab-panel, don't do anything.
        if (this.activeDataTab?.id === dataTabID) {
            return
        }

        if (this.activeDataTab) {
            // Hide any active tab.
            this.activeDataTab.hidden = true
        }
        const targetElement = this.renderRoot.getElementById(dataTabID)
        this.activeDataTab = targetElement
        if (targetElement) {
            targetElement.hidden = false
        }

        this.selectTabInTabTree(dataTabID)
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
                dataTabs = html`${dataTabs}
                    <sc-data-tab hidden id=${innerTab.id} tabname=${innerTab.name}
                        .smrytblpath=${innerTab.smrytblpath} .smrytblfile=${innerTab.smrytblfile}
                        .paths=${innerTab.ppaths} .fpreviews=${innerTab.fpreviews}
                        .dir=${innerTab.dir} .alerts=${innerTab.alerts}>
                    </sc-data-tab>`
            }
        }
        return dataTabs
    }

    /**
     * Open the first tab after finishing loading in.
     */
    firstUpdated () {
        this.show(this.firstTab)
    }

    /**
     * Returns the HTML template for a tree-item in the tab navigation tree.
     * @param {Object} tab: Tab object from the Python side.
     */
    treeItemTemplate (tab) {
        // Recursive base case: the contents of a tree item is just the name.
        if (!tab.tabs) {
            this.dataTabs.push(tab.id)
            if (!this.firstTab) {
                this.firstTab = tab.id
            }
            return tab.name
        }
        /* If this tree item contains children then create tree items for each one.
         * The ternary operator in this template states that if 'innerTab' is a leaf node in the
         * tree, assign a listner for 'click' events which redirects to the relevant tab.
         */
        return html`
            ${tab.name}
            ${tab.tabs.map((innerTab) => {
                return html`
                    <sl-tree-item id=${`${innerTab.id}-tree`} @click=${innerTab.tabs
                        ? () => {}
                        : () => { location.hash = innerTab.id }}>
                        ${this.treeItemTemplate(innerTab)}
                    </sl-tree-item>
                `
            })}
        `
    }

    render () {
        if (!this.tab) {
            return html``
        }
        return html`
            <sl-split-panel position=20 style="--divider-width: 20px;">
                <sl-tree selection="leaf" slot="start">
                    ${this.treeItemTemplate(this.tab)}
                </sl-tree>
                <div style="height: 95vh; overflow:scroll;" slot="end">
                    ${this.tabPanesTemplate(this.tab)}
                </div>
            </sl-split-panel>
        `
    }

    constructor () {
        super()
        // This list tracks the data-tabs contained in this tab-panel.
        this.dataTabs = []

        // Store the name of the first data-tab in the tab-tree.
        this.firstTab = ''
    }
}

customElements.define('sc-tab-panel', ScTabPanel)
