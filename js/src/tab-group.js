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

import { html, css, LitElement } from 'lit'
import '@shoelace-style/shoelace/dist/components/alert/alert'
import '@shoelace-style/shoelace/dist/components/tab-group/tab-group'
import '@shoelace-style/shoelace/dist/components/tab/tab'
import '@shoelace-style/shoelace/dist/components/tab-panel/tab-panel'

import './tab-panel'

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
         * Also reduce the top and bottom padding of tabs as it makes them easier to read.
         */
        .tab::part(base) {
            padding-bottom: var(--sl-spacing-x-small);
            padding-top: var(--sl-spacing-x-small);
            font-family: Arial, sans-serif;
        }

        /*
         * Specify height of tabs to match the button to toggle the report header.
         */
        sl-tab-group::part(tabs) {
            height: 2rem;
        }
    `

    static properties = {
        tabs: { type: Object }
    };

    get _tabPanels () {
        return this.renderRoot.querySelectorAll('sc-tab-panel')
    }

    get _tabGroup () {
        return this.renderRoot.querySelector('sl-tab-group')
    }

    /**
     * Returns the tab-panel element containing the data-tab represented by 'dataTabID'.
     * @param {string} dataTabID - the ID of the requested data-tab.
     */
    getTabPanel (dataTabID) {
        for (const tabPanel of this._tabPanels) {
            if (tabPanel.hasDataTab(dataTabID)) {
                return tabPanel
            }
        }
    }

    /**
     * Returns the currently active container tab element.
     */
    getActiveTab () {
        const tabs = this._tabGroup.querySelectorAll('sl-tab')
        for (const tab of tabs) {
            if (tab.active) {
                return tab
            }
        }
        throw Error('BUG: unable to find active tab')
    }

    /**
     * Returns the currently active data-tab element.
     */
    getActiveDataTab () {
        const activeTab = this.getActiveTab()
        for (const tabPanel of this._tabPanels) {
            if (tabPanel.tab.name === activeTab.panel) {
                return tabPanel.activeDataTab
            }
        }
        throw Error('BUG: unable to find active data tab')
    }

    /**
     * Open the container tab containing the data-tab represented by 'dataTabID'.
     * @param {dataTabID} dataTabID - the ID of the data tab to show.
     */
    show (dataTabID = location.hash.substring(1)) {
        for (const tabPanel of this._tabPanels) {
            tabPanel.show(dataTabID)
        }
    }

    /**
     * Handles any data-tab specified in the URL and adds an event handler which updates the URL
     * when a user opens a new tab.
     */
    firstUpdated () {
        // Listen for events which signal the user opened a new tab, update 'location.href' to
        // reflect the tab that was openeed.
        this.tabChangeHandler = () => { location.href = `#${this.getActiveDataTab().id}` }
        this._tabGroup.addEventListener('sl-tab-show', this.tabChangeHandler)

        this._tabGroup.updateComplete.then(() => {
            // Remove the '#' from 'location.hash' to get the 'dataTabID'.
            const dataTabID = location.hash.substring(1)

            // If no tab was specified in the URL, open the first data-tab in the first tab.
            if (!dataTabID) {
                location.hash = `${this._tabPanels[0].firstTab}`
                return
            }
            const tabPanel = this.getTabPanel(dataTabID)
            tabPanel.updateComplete.then(() => {
                tabPanel.show(dataTabID)
                this._tabGroup.show(tabPanel.parentElement.name)
            })
        })
    }

    connectedCallback () {
        super.connectedCallback()
        this.hashHandler = () => { this.show() }
        window.addEventListener('hashchange', this.hashHandler, false)
    }

    disconnectedCallback () {
        window.removeEventListener('hashchange', this.hashHandler)
        this._tabGroup.removeEventListener('sl-tab-show', this.tabChangeHandler)
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
                        <sc-tab-panel .tab=${tab}></sc-tab-panel>
                    </sl-tab-panel>
                `)}
            </sl-tab-group>
      `
    }
}

customElements.define('sc-tab-group', ScTabGroup)
