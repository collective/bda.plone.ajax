# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from bda.plone.ajax import render_ajax_form


class AjaxForm(BrowserView):
    """Generic ajax form view.
    """

    def __call__(self):
        """Render ajax form by name.

        Expects request param ``form_name`` on request. Form name maps to a
        browser view rendering the form.
        """
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return render_ajax_form(self.context,
                                self.request,
                                self.request.get('form_name', 'NO_FORM_NAME'))
