try:
    import json
except ImportError:
    import simplejson as json
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.contentprovider.interfaces import IContentProvider
from Products.Five import BrowserView
from bda.plone.ajax import AjaxContinue


class Action(BrowserView):
    
    def continuation(self, ret):
        continuation = self.request.get('cone.app.continuation')
        if continuation:
            continuation = AjaxContinue(continuation).definitions
        else:
            continuation = False
        ret['continuation'] = continuation
    
    def ajaxaction(self):
        """Ajaxaction view, expected by bdajax contract.
        
        This view tries to lookup action by restricted traverse first, if not
        found, it tries to lookup contentprovider by action name. If this fails
        an error is raised.
        """
        mode = self.request.get('bdajax.mode')
        selector = self.request.get('bdajax.selector')
        action = self.request.get('bdajax.action')
        ret = {
            'mode': mode,
            'selector': selector,
        }
        try:
            view = self.context.restrictedTraverse(action)
        except KeyError:
            view = None
        if view:
            ret['payload'] = view()
            self.continuation(ret)
            return json.dumps(ret)
        try:
            toadapt = (self.context, self.request, self)
            renderer = getMultiAdapter(toadapt,
                                       IContentProvider,
                                       name=action)
        except ComponentLookupError:
            renderer = None
        if renderer:
            renderer.update()
            ret['payload'] = renderer.render()
            self.continuation(ret)
            return json.dumps(ret)
        raise Exception('Ajax action "%s" not found' % action);