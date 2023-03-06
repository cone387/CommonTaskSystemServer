# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2023/2/25 11:40
# software: PyCharm
import json

from django.forms import Widget, widgets
from django.utils.safestring import mark_safe


class JSONWidget(widgets.Textarea):

    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, sort_keys=True, ensure_ascii=False)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 40)
            self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            return super(JSONWidget, self).format_value(value)


class JSJsonWidget(Widget):
    """
    在 django  admin 后台中使用  jsoneditor 处理 JSONField

    TODO：有待改进, 这里使用 % 格式化，使用 format 会抛出 KeyError 异常
    """

    html_template = """
    <div id='%(name)s_editor_holder' style='padding-left:170px'></div>
    <textarea hidden readonly class="vLargeTextField" cols="40" id="id_%(name)s" name="%(name)s" rows="20">%(value)s</textarea>

    <script type="text/javascript">
        var element = document.getElementById('%(name)s_editor_holder');
        var json_value = %(value)s;

        var %(name)s_editor = new JSONEditor(element, {
            onChange: function() {
                var textarea = document.getElementById('id_%(name)s');
                var json_changed = JSON.stringify(%(name)s_editor.get()['Object']);
                textarea.value = json_changed;
            }
        });

        %(name)s_editor.set({"Object": json_value})
        %(name)s_editor.expandAll()
    </script>
    """

    def __init__(self, attrs=None):
        super(JSJsonWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, str):
            value = json.loads(value)

        result = self.html_template % {'name': name, 'value': json.dumps(value)}
        return mark_safe(result)
