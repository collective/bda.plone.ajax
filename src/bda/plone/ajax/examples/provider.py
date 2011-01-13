from Acquisition import Explicit
from zope.interface import (
    Interface,
    implements,
)
from zope.component import adapts
from zope.publisher.interfaces.browser import (
    IBrowserRequest,
    IBrowserView,
)
from zope.contentprovider.interfaces import IContentProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Provider(Explicit):
    
    implements(IContentProvider)
    adapts(Interface, IBrowserRequest, IBrowserView)
    
    template = ViewPageTemplateFile(u'tile_b.pt')
    
    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request
    
    def update(self):
        pass
    
    def render(self):
        return self.template(self)