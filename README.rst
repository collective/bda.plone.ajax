Integration package
===================

This is the plone integration package for
`bdajax <http://github.com/bluedynamics/bdajax/>`_.


Installation
============

- Make egg available in your instance.
- Apply extension profile.


Usage
=====

For detailed documentation about ``bdajax`` please refer to
`bdajax <http://github.com/bluedynamics/bdajax/>`_.


Implement ajax action as browser view
-------------------------------------

An ajax action can be implemented as simple browser view. The easiest way is to
render a template only. Create template ``tile_a.pt``::

    <div xmlns:ajax="http://namesspaces.bluedynamics.eu/ajax" tal:omit-tag="">

      <!-- the tile -->
      <div class="tile_a"
           style="background-color:#ffc261;">

        <h3>I am tile A</h3>

        <!-- perform action directly. here we render tile_b, see below -->
        <a href=""
           ajax:bind="click"
           ajax:action="bdajax_example_tile_b:.tile_a:replace"
           ajax:target=""
           tal:attributes="ajax:target context/absolute_url">alter me</a>

      </div>

    </div>

Configure via ZCML::

    <browser:page
      for="*"
      name="bdajax_example_tile_a"
      template="tile_a.pt"
      permission="zope2.View" />


Implement Ajax Action as content provider
-----------------------------------------

Create a template ``tile_b.pt`` containing the markup::

    <div xmlns:ajax="http://namesspaces.bluedynamics.eu/ajax" tal:omit-tag="">

      <!-- bind custom event to tile, perform action if event triggered -->
      <!-- when event gets triggered, tile_a gets rendered, see above -->
      <div class="tile_b"
           style="background-color:#61ff68;"
           ajax:bind="altertile"
           ajax:action="bdajax_example_tile_a:.tile_b:replace">

        <h3>I am tile B</h3>

        <!-- bind element to click event and trigger custom event -->
        <a href=""
           ajax:bind="click"
           ajax:event="altertile:.tile_b"
           ajax:target=""
           tal:attributes="ajax:target context/absolute_url">alter me</a>

      </div>

    </div>

Create content provider in ``provider.py``::

    from Acquisition import Explicit
    from zope.interface import (
        Interface,
        implementer,
    )
    from zope.component import adapter
    from zope.publisher.interfaces.browser import (
        IBrowserRequest,
        IBrowserView,
    )
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

Configure provider via ZCML::

    <adapter
      name="bdajax_example_tile_b"
      provides="zope.contentprovider.interfaces.IContentProvider"
      factory=".provider.Provider" />


Implement a wrapper view
------------------------

The two ajax action rendering snippets above each render a tile only. now we
need to wrap this inside a plone view. Create template ``ploneview.pt``::

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal"
          xmlns:i18n="http://xml.zope.org/namespaces/i18n"
          lang="en"
          metal:use-macro="here/main_template/macros/master"
          i18n:domain="bda.plone.ajax">
    <body>

      <metal:main fill-slot="main">
        <tal:main-macro metal:define-macro="main">

          <tal:tile replace="structure context/@@bdajax_example_tile_a" />

        </tal:main-macro>
      </metal:main>

    </body>
    </html>

And register via ZCML::

    <browser:page
      for="*"
      name="bdajax_example_view"
      template="ploneview.pt"
      permission="zope2.View" />

Now start instance and navigate to ``@@bdajax_example_view``. You get initially
``tile a`` rendered switching to ``tile b`` on click and vise versa. This code
equates the one contained in examples folder.


Implement ajaxified batch
-------------------------

Create a batch implementation in python, i.e. ``examplebatch.py`` calculating
batch vocab::

    from Products.Five import BrowserView
    from bda.plone.ajax.batch import Batch


    RESULTLEN = 45
    SLICESIZE = 10


    class ExampleBatch(Batch):
        batchname = 'examplebatch'

        @property
        def vocab(self):
            ret = list()
            # len result
            count = RESULTLEN
            # entries per page
            slicesize = SLICESIZE
            # number of batch pages
            pages = count / slicesize
            if count % slicesize != 0:
                pages += 1
            # current batch page
            current = self.request.get('b_page', '0')
            for i in range(pages):
                # create query with page number
                query = 'b_page=%s' % str(i)
                # create batch target url
                url = '%s?%s' % (self.context.absolute_url(), query)
                # append batch page
                ret.append({
                    'page': '%i' % (i + 1),
                    'current': current == str(i),
                    'visible': True,
                    'url': url,
                })
            return ret

Create batched result view::

    class BatchedResult(BrowserView):

        @property
        def batch(self):
            return ExampleBatch(self.context, self.request)()

        @property
        def slice(self):
            result = range(RESULTLEN)
            current = int(self.request.get('b_page', '0'))
            start = current * SLICESIZE
            end = start + SLICESIZE
            return result[start:end]

Create batched result template, i.e. ``batchedresult.pt``::

    <div xmlns="http://www.w3.org/1999/xhtml"
         xml:lang="en"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:i18n="http://xml.zope.org/namespaces/i18n"
         i18n:domain="bda.plone.ajax"
         class="examplebatchsensitiv"
         ajax:bind="batchclicked"
         tal:attributes="ajax:target context/absolute_url;
                         ajax:action string:bdajax_example_batched_result:.examplebatchsensitiv:replace">

      <tal:listingbatch replace="structure view/batch" />

      <ul>
        <li tal:repeat="item view/slice" tal:content="item">x</li>
      </ul>

      <tal:listingbatch replace="structure view/batch" />

    </div>

Create wrapper view, i.e. ``batchview.pt``::

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal"
          xmlns:i18n="http://xml.zope.org/namespaces/i18n"
          lang="en"
          metal:use-macro="here/main_template/macros/master"
          i18n:domain="bda.plone.ajax">
    <body>

      <metal:main fill-slot="main">
        <tal:main-macro metal:define-macro="main">

          <tal:tile replace="structure context/@@bdajax_example_batched_result" />

        </tal:main-macro>
      </metal:main>

    </body>
    </html>

And register views via ZCML::

    <browser:page
      for="*"
      name="bdajax_example_batch"
      template="batchview.pt"
      permission="zope2.View" />

    <browser:page
      for="*"
      name="bdajax_example_batched_result"
      class=".examplebatch.BatchedResult"
      template="batchedresult.pt"
      permission="zope2.View" />

Now start instance and navigate to ``@@bdajax_example_batch``. You get an
example result rendered batched. This code equates the one contained in
examples folder.


Examples
--------

This package ships with examples, as explained above.
To enable examples include ``bda.plone.ajax.examples`` via ZCML.


Contributors
============

- Robert Niederreiter (Autor)
- Jens W. Klein
