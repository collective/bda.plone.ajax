# -*- coding: utf-8 -*-
try:
    import json
except ImportError:
    import simplejson as json
from bda.plone.ajax.utils import format_traceback
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import createToken
from plone.protect.utils import getRoot
from plone.protect.utils import getRootKeyManager
from zope.component import ComponentLookupError
from zope.component import getUtility


def ajax_continue(request, continuation):
    """Set ajax continuation on request.

    ``continuation``
        list of continuation definition objects or single continuation
        definition.
    """
    if request.get('bda.plone.ajax.continuation', None) is None:
        request['bda.plone.ajax.continuation'] = list()
    if isinstance(continuation, list):
        existent = request['bda.plone.ajax.continuation']
        request['bda.plone.ajax.continuation'] = existent + continuation
    else:
        request['bda.plone.ajax.continuation'].append(continuation)


def ajax_message(request, payload, flavor='message'):
    """Convenience to add ajax message definition to ajax continuation
    definitions.
    """
    ajax_continue(request, AjaxMessage(payload, flavor, None))


def ajax_status_message(request, payload):
    """Convenience to add ajax status message definition to ajax continuation
    definitions.
    """
    ajax_continue(request, AjaxMessage(payload, None, '#status_message'))


class AjaxPath(object):
    """Ajax path continuation definition.
    """

    def __init__(self, path):
        self.path = path


class AjaxAction(object):
    """Ajax action continuation definition.
    """

    def __init__(self, target, name, mode, selector):
        self.target = target
        self.name = name
        self.mode = mode
        self.selector = selector


class AjaxEvent(object):
    """Ajax event continuation definition.
    """

    def __init__(self, target, name, selector):
        self.target = target
        self.name = name
        self.selector = selector


class AjaxMessage(object):
    """Ajax message continuation definition.
    """

    def __init__(self, payload, flavor, selector):
        self.payload = payload
        self.flavor = flavor
        self.selector = selector


class AjaxOverlay(object):
    """Ajax overlay configuration. Used to display or close overlays on client
    side.
    """

    def __init__(self, selector='#ajax-overlay', action=None, target=None,
                 close=False, content_selector='.overlay_content'):
        self.selector = selector
        self.content_selector = content_selector
        self.action = action
        self.target = target
        self.close = close


class AjaxContinue(object):
    """Convert ``AjaxAction``, ``AjaxEvent`` and ``AjaxMessage`` instances to
    JSON response definitions for bdajax continuation.
    """

    def __init__(self, continuation):
        self.continuation = continuation

    @property
    def definitions(self):
        """Continuation definitions as list of dicts for JSON serialization.
        """
        if not self.continuation:
            return
        continuation = list()
        for definition in self.continuation:
            if isinstance(definition, AjaxPath):
                continuation.append({
                    'type': 'path',
                    'path': definition.path,
                })
            if isinstance(definition, AjaxAction):
                continuation.append({
                    'type': 'action',
                    'target': definition.target,
                    'name': definition.name,
                    'mode': definition.mode,
                    'selector': definition.selector,
                })
            if isinstance(definition, AjaxEvent):
                continuation.append({
                    'type': 'event',
                    'target': definition.target,
                    'name': definition.name,
                    'selector': definition.selector,
                })
            if isinstance(definition, AjaxMessage):
                continuation.append({
                    'type': 'message',
                    'payload': definition.payload,
                    'flavor': definition.flavor,
                    'selector': definition.selector,
                })
            if isinstance(definition, AjaxOverlay):
                continuation.append({
                    'type': 'overlay',
                    'selector': definition.selector,
                    'content_selector': definition.content_selector,
                    'action': definition.action,
                    'target': definition.target,
                    'close': definition.close,
                })
        return continuation

    def dump(self):
        """Return a JSON dump of continuation definitions.
        """
        ret = self.definitions
        if not ret:
            return
        return json.dumps(ret)


class AjaxFormContinue(AjaxContinue):
    """Used by ``render_ajax_form``.
    """

    @property
    def next(self):
        """Return 'false' if no continuation actions, otherwise a JSON dump of
        continuation definitions.
        """
        ret = self.dump()
        if not ret:
            return 'false'
        return ret


def ajax_form_fiddle(request, selector, mode):
    """Define ajax form fiddle mode and selector. Used on client side to
    determine form location in replacement mode for rendered ajax form.
    """
    request['bda.plone.ajax.form.selector'] = selector
    request['bda.plone.ajax.form.mode'] = mode


ajax_form_template = """\
<div id="ajaxform">
    %(form)s
</div>
<script language="javascript" type="text/javascript">
    var container = document.getElementById('ajaxform');
    var child = container.firstChild;
    while(child != null && child.nodeType == 3) {
        child = child.nextSibling;
    }
    var forms = child.getElementsByTagName('form');
    for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        if (form.querySelector('[name="_authenticator"]').length !== 0) {
            continue;
        }
        var authenticator = document.createElement('input');
        authenticator.setAttribute('type', 'hidden');
        authenticator.setAttribute('name', '_authenticator');
        authenticator.setAttribute('value', '%(token)s');
        form.appendChild(authenticator);
    }
    parent.bdajax.render_ajax_form(child, '%(selector)s', '%(mode)s');
    parent.bdajax.continuation(%(next)s);
</script>
"""


def render_ajax_form(context, request, name):
    """Render ajax form on context by view name.

    By default contents of div with id ``content`` gets replaced. If fiddle
    mode or selector needs to get customized, ``bda.plone.ajax.form.mode``
    and ``bda.plone.ajax.form.selector`` must be given as request parameters.
    """
    try:
        key_manager = getUtility(IKeyManager)
    except ComponentLookupError:
        key_manager = getRootKeyManager(getRoot(context))
    token = createToken(manager=key_manager)
    try:
        result = context.restrictedTraverse(name)()
        selector = request.get('bda.plone.ajax.form.selector', '#content')
        mode = request.get('bda.plone.ajax.form.mode', 'inner')
        continuation = request.get('bda.plone.ajax.continuation')
        form_continue = AjaxFormContinue(continuation)
        response = ajax_form_template % {
            'form': result,
            'token': token,
            'selector': selector,
            'mode': mode,
            'next': form_continue.next,
        }
        return response
    except Exception:
        result = '<div>Form rendering error</div>'
        selector = request.get('bda.plone.ajax.form.selector', '#content')
        mode = request.get('bda.plone.ajax.form.mode', 'inner')
        tb = format_traceback()
        continuation = AjaxMessage(tb, 'error', None)
        form_continue = AjaxFormContinue([continuation])
        response = ajax_form_template % {
            'form': result,
            'token': token,
            'selector': selector,
            'mode': mode,
            'next': form_continue.next,
        }
        return response
