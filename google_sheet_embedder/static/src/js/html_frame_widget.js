/** @odoo-module **/

import { FieldHtml } from "@web/views/fields/html/html_field";
import { registry } from "@web/core/registry";

const HtmlFrame = {
    ...FieldHtml,
    get htmlContent() {
        return this.props.value || "";
    },
};

registry.category("fields").add("html_frame", HtmlFrame);