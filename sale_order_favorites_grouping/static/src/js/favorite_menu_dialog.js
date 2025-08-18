/** @odoo-module **/

import { FavoriteMenuDialog } from "@web/search/search_favorites_menu/favorite_menu_dialog";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

const GROUP_OPTIONS = [
    "Customer Related",
    "Delivery",
    "Invoices",
    "Others",
];

patch(FavoriteMenuDialog.prototype, "sale_order_favorites_grouping", {
    setup() {
        super.setup();
        this.state = useState({
            ...this.state,
            group_name: this.props.filter?.group_name || "",
        });
        this.groupOptions = GROUP_OPTIONS;
    },

    async save() {
        await this.props.onSave({
            ...this.state,
            name: this.state.name,
            domain: this.state.domain,
            context: this.state.context,
            sort: this.state.sort,
            group_name: this.state.group_name,  // Save selected group
        });
        this.props.close();
    },
});