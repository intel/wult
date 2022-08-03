/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2021-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { LitElement, html } from 'lit'
import { cache } from 'lit/directives/cache.js'

/**
 * Generic class which handles visiblity of report tabs. When creating a new tab, it is recommended
 * to use a class which inherits from this class or create a new type. For example, if you want to
 * add a new 'data' tab, then use the '<sc-data-tab>' element over this one.
 *
 * @class ScTab
 * @extends {LitElement}
 */
export class ScTab extends LitElement {
    static properties = {
        tabname: { type: String },
        info: { type: Object },
        visible: { type: Boolean, attribute: false }
    };

    /**
     * Checks mutations to the parent tab element to see if the 'active' attribute has been set and
     * sets the 'visible' attribute accordingly.
     */
    checkVisible (mutationsList, observer) {
        for (const mutation of mutationsList) {
            if (mutation.attributeName === 'active') {
                if (this.tabname === mutation.target.id) {
                    this.visible = true
                } else {
                    this.visible = false
                }
            }
        }
    }

    /**
     * Early DOM lifecycle event. Invoked each time the custom element is appended into a
     * document-connected element.
     */
    connectedCallback () {
        super.connectedCallback()
        // Adds event listener so that the tab will re-evaulate 'visible' every time the user clicks
        // to see if the tab has been opened. Read relevant docs here:
        // https://lit.dev/docs/components/events/#adding-event-listeners-to-other-elements

        // ScTabs are contained by SlTabPanel components which gain the 'active'
        // attribute when the respective tab is active. Therefore we observe
        // changes on that SlTabPanel and when it becomes active, we know that
        // this tab is visible.

        // Bind the callback to 'this' instance so that it can access class properties.
        const mutationCallback = this.checkVisible.bind(this)

        // Options for the observer (which mutations to observe).
        const config = { attributes: true }

        this.observer = new MutationObserver(mutationCallback)
        this.observer.observe(this.parentElement, config)
    }

    /**
     * Removes the 'click' event handler in the case that the tab is destroyed so that the window
     * does not attempt to trigger the handler when it is no longer accessible.
     */
    disconnectedCallback () {
        super.disconnectedCallback()
        this.observer.disconnect()
    }

    /**
     * Provides the template for when the tab is visible (active).
     */
    visibleTemplate () {
        throw new Error("Inherit from this class and implement 'visibleTemplate'.")
    }

    render () {
        // Use 'cache()' to cache tabs which means their content will be saved after being loaded for
        // the first time and does not need to be re-generated every time.
        return html`
        ${cache(this.visible
            ? html`${this.visibleTemplate()}`
            : html``
    )}`
    }
}

customElements.define('sc-tab', ScTab)
