import types
try:
    import json
except ImportError:
    import simplejson as json


def ajax_continue(request, continuation):
    """Set ajax continuation on request.
    
    ``continuation``
        list of continuation definition objects or single continuation
        definition.
    """
    if request.get('bda.plone.ajax.continuation', None) is None:
        request['bda.plone.ajax.continuation'] = list()
    if type(continuation) is types.ListType:
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
        return continuation
    
    def dump(self):
        """Return a JSON dump of continuation definitions.
        """
        ret = self.definitions
        if not ret:
            return
        return json.dumps(ret)