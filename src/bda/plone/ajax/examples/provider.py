from Acquisition import Explicit
from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.contentprovider.interfaces import IContentProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bda.plone.ajax import ajax_message


@implementer(IContentProvider)
@adapter(Interface, IBrowserRequest, IBrowserView)
class Provider(Explicit):
    template = ViewPageTemplateFile(u'tile_b.pt')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def render(self):
        # set here continuation message. See bda.plone.ajax.__init__ for
        # details.
        ajax_message(self.request, 'Demo continuation message', flavor='info')
        return self.template(self)
