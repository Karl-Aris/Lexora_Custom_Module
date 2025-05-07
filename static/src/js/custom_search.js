/** @odoo-module **/

import { registry } from "@web/core/registry";
const { Component, onMounted, useState } = owl;
const { SearchBar } = await import("@web/search/search_bar/search_bar");

class BulkSOInput extends Component {
    setup() {
        this.state = useState({ value: "" });
    }

    onInput(ev) {
        this.state.value = ev.target.value;
        const terms = this.state.value.split(/[\s,;]+/).filter(Boolean);
        this.props.onChange({
            domain: [["name", "in", terms]],
        });
    }

    render() {
        return (
            <input
                type="text"
                placeholder="Paste SO numbers (e.g. SO1001, SO1002)..."
                onInput={this.onInput.bind(this)}
            />
        );
    }
}

registry.category("search_components").add("bulk_so_input", BulkSOInput);
