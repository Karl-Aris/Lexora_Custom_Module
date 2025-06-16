odoo.define('google_sheet_embedder.html_frame_widget', function (require) {
  "use strict";

  const fieldRegistry = require('web.field_registry');
  const FieldHtml = require('web.basic_fields').FieldHtml;

  const HtmlFrameWidget = FieldHtml.extend({
    _renderReadonly: function () {
      try {
        const content = this.value || '';
        this.$el.html(content);
      } catch (error) {
        console.error("Failed to render iframe content:", error);
        this.$el.html('<p style="color:red;">Error rendering iframe</p>');
      }
    },
  });

  fieldRegistry.add('html_frame', HtmlFrameWidget);
});
