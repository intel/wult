/*
 * -*- coding: utf-8 -*-
 * vim: ts=4 sw=4 tw=100 et ai si
 *
 * Copyright (C) 2021-2022 Intel, Inc.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

import { LitElement } from 'lit'

/**
 * Generic class which handles visiblity of report tabs. When creating a new tab, it is recommended
 * to use a class which inherits from this class or create a new type. For example, if you want to
 * add a new 'data' tab, then use the '<sc-data-tab>' element over this one.
 *
 * @class ScTab
 * @extends {LitElement}
 */
export class ScTab extends LitElement {
    /**
     * Provides the template for when the tab is visible (active).
     */
    visibleTemplate () {
        throw new Error("Inherit from this class and implement 'visibleTemplate'.")
    }

    render () {
        return this.visibleTemplate()
    }
}

customElements.define('sc-tab', ScTab)
