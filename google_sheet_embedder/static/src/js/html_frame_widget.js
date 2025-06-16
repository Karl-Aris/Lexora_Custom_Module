odoo.define('google_sheet_embedder.html_frame_widget', function (require) {
  "use strict";

  const fieldRegistry = require('web.field_registry');
  const FieldHtml = require('web.basic_fields').FieldHtml;

  const HtmlFrameWidget = FieldHtml.extend({
    _renderReadonly: function () {
      // Use safe rendering to avoid undefined issues
      const content = this.value || '';
      this.$el.html(content);
    },
  });

  fieldRegistry.add('html_frame', HtmlFrameWidget);
});
