from Products.Five import BrowserView
from .. import ajax_continue
from .. import ajax_form_fiddle
from .. import AjaxMessage
from .. import AjaxOverlay


class AjaxForm(BrowserView):

    @property
    def form_action(self):
        return 'ajaxform?form_name=bdajax_example_form'

    @property
    def submitted(self):
        return 'field' in self.request.form

    @property
    def error(self):
        if not self.submitted:
            return
        if not self.request.form['field']:
            return u'Field must not be empty'

    @property
    def value(self):
        return self.request.form.get('field')

    def __call__(self):
        if self.submitted and not self.error:
            ajax_continue(self.request, AjaxMessage('Success!', 'info', None))
        return super(AjaxForm, self).__call__()


class AjaxOverlayForm(AjaxForm):

    @property
    def form_action(self):
        return 'ajaxform?form_name=bdajax_example_overlay_form'

    def __call__(self):
        if self.submitted and not self.error:
            continuation = [
                AjaxMessage('Success!', 'info', None),
                AjaxOverlay(close=True),
            ]
            ajax_continue(self.request, continuation)
        if self.submitted:
            ajax_form_fiddle(self.request, '#example_ajaxform', 'replace')
        return super(AjaxForm, self).__call__()
