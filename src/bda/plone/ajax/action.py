# -*- coding: utf-8 -*-
from bda.plone.ajax import AjaxContinue
from bda.plone.ajax import AjaxMessage
from bda.plone.ajax.utils import format_traceback
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
import logging

try:
    import json
except ImportError:
    import simplejson as json

logger = logging.getLogger(__name__)


class Action(BrowserView):

    def continuation(self, ret):
        continuation = self.request.get('bda.plone.ajax.continuation', False)
        if continuation:
            continuation = AjaxContinue(continuation).definitions
        ret['continuation'] = continuation

    def ajaxaction(self):
        """Ajaxaction view, expected by bdajax contract.

        This view tries to lookup action by restricted traverse first, if not
        found, it tries to lookup contentprovider by action name. If this fails
        an error is raised.
        """
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        self.request.response.setHeader(
            'Content-Type',
            'application/json; charset=utf-8'
        )
        try:
            mode = self.request.get('bdajax.mode')
            selector = self.request.get('bdajax.selector')
            action = self.request.get('bdajax.action')
            ret = {
                'mode': mode,
                'selector': selector,
            }
            try:
                view = self.context.restrictedTraverse(action)
            except (KeyError, AttributeError):
                view = None
            if view:
                ret['payload'] = view()
                self.continuation(ret)
                return json.dumps(ret)
            toadapt = (self.context, self.request, self)
            renderer = getMultiAdapter(toadapt, IContentProvider, name=action)
            renderer.update()
            ret['payload'] = renderer.render()
            self.continuation(ret)
            return json.dumps(ret)
        except Exception, e:
            logger.exception(e)
            tb = format_traceback()
            continuation = AjaxContinue(
                [AjaxMessage(tb, 'error', None)]).definitions
            return json.dumps({
                'mode': 'NONE',
                'selector': 'NONE',
                'payload': '',
                'continuation': continuation,
            })
