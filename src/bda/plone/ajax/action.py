try:
    import json
except ImportError:
    import simplejson as json
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.contentprovider.interfaces import IContentProvider
from Products.Five import BrowserView

class Action(BrowserView):
    
    def ajaxaction(self):
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
            return json.dumps(ret)
        raise Exception('Ajax action "%s" not found' % action);
