/** @odoo-module **/

import { SearchFavoritesMenu } from "@web/search/search_favorites_menu/search_favorites_menu";
import { patch } from "@web/core/utils/patch";

patch(SearchFavoritesMenu.prototype, "sale_order_delivery_tracking", {
    get groupedFilters() {
        const groups = {};
        for (const filter of this.props.favorites.filters) {
            const group = filter.group_name || "Ungrouped";
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(filter);
        }
        return groups;
    },
});
