/* jslint browser: true */
/* global jQuery, bdajax */
/*
 * bdajax v1.6.3
 *
 * Author: Robert Niederreiter
 * License: Simplified BSD
 *
 * Requires:
 * - jQuery 1.6.4+
 * - jQuery Tools overlay.js
 */

var bdajax;

(function($) {
    "use strict";

    $(document).ready(function() {
        bdajax.spinner.hide();
        $(document).bdajax();
    });

    $.fn.bdajax = function() {
        var context = $(this);
        $('*', context).each(function() {
            for (var i in this.attributes) {
                var attr = this.attributes[i];
                if (attr && attr.nodeName) {
                    var name = attr.nodeName;
                    if (name.indexOf('ajax:bind') > -1) {
                        var events = attr.nodeValue;
                        var ajax = $(this);
                        ajax.unbind(events);
                        if (ajax.attr('ajax:action') ||
                            ajax.attr('ajax:event')  ||
                            ajax.attr('ajax:overlay')) {
                            ajax.bind(events, bdajax._dispatching_handler);
                        }
                    }
                    if (name.indexOf('ajax:form') > -1) {
                        bdajax.prepare_ajax_form($(this));
                    }
                }
            }
        });
        // B/C: Ajax forms have a dedicated ``ajax:form`` directive now.
        bdajax.bind_ajax_form(context);
        for (var binder in bdajax.binders) {
            bdajax.binders[binder](context);
        }
        return context;
    };

    // global bdajax object
    bdajax = {

        // By default, we redirect to the login page on 403 error.
        // That we assume at '/login'.
        default_403: '/login',

        // object for hooking up JS binding functions after ajax calls
        binders: {},

        // ajax spinner handling
        spinner: {

            _elem: null,
            _request_count: 0,

            elem: function() {
                if (this._elem === null) {
                    this._elem = $('#ajax-spinner');
                }
                return this._elem;
            },

            show: function() {
                this._request_count++;
                if (this._request_count > 1) {
                    return;
                }
                this.elem().show();
            },

            hide: function(force) {
                this._request_count--;
                if (force) {
                    this._request_count = 0;
                    this.elem().hide();
                    return;
                } else if (this._request_count <= 0) {
                    this._request_count = 0;
                    this.elem().hide();
                }
            }
        },

        parseurl: function(url) {
            var parser = document.createElement('a');
            parser.href = url;
            var path = parser.pathname;
            if (path.indexOf('/') !== 0) {
                // Internet Explorer 11 doesn't starts with '/'
                path = '/' + path;
            }
            url = parser.protocol + '//' + parser.host + path;
            if (url.charAt(url.length - 1) === '/') {
                url = url.substring(0, url.length - 1);
            }
            return url;
        },

        parsequery: function(url) {
            var parser = document.createElement('a');
            parser.href = url;
            var params = {};
            var search = parser.search;
            if (search) {
                var parameters = search.substring(1, search.length).split('&');
                for (var i = 0; i < parameters.length; i++) {
                    var param = parameters[i].split('=');
                    params[param[0]] = param[1];
                }
            }
            return params;
        },

        parsepath: function(url) {
            var parser = document.createElement('a');
            parser.href = url;
            return parser.pathname;
        },

        parsetarget: function(target) {
            var url = this.parseurl(target);
            var params = this.parsequery(target);
            var path = this.parsepath(target);
            if (!params) { params = {}; }
            return {
                url: url,
                params: params,
                path: path
            };
        },

        request: function(options) {
            if (options.url.indexOf('?') !== -1) {
                var addparams = options.params;
                options.params = this.parsequery(options.url);
                options.url = this.parseurl(options.url);
                for (var key in addparams) {
                    options.params[key] = addparams[key];
                }
            } else {
                if (!options.params) { options.params = {}; }
            }
            if (!options.type) { options.type = 'html'; }
            if (!options.error) {
                options.error = function(req, status, exception) {
                    if (parseInt(status, 10) === 403) {
                        window.location.pathname = bdajax.default_403;
                    } else {
                        var message = '<strong>' + status + '</strong> ';
                        message += exception;
                        bdajax.error(message);
                    }
                };
            }
            if (!options.cache) { options.cache = false; }
            var wrapped_success = function(data, status, request) {
                options.success(data, status, request);
                bdajax.spinner.hide();
            };
            var wrapped_error = function(request, status, error) {
                if (request.status === 0) {
                    bdajax.spinner.hide(true);
                    return;
                }
                status = request.status || status;
                error = request.statusText || error;
                options.error(request, status, error);
                bdajax.spinner.hide(true);
            };
            this.spinner.show();
            $.ajax({
                url: options.url,
                dataType: options.type,
                data: options.params,
                success: wrapped_success,
                error: wrapped_error,
                cache: options.cache
            });
        },

        path: function(path) {
            if (typeof(window.history.replaceState) === undefined) {
                return;
            }
            if (path.charAt(0) !== '/') {
                path = '/' + path;
            }
            window.history.replaceState({}, '', path);
        },

        action: function(options) {
            options.success = this._ajax_action_success;
            this._perform_ajax_action(options);
        },

        fiddle: function(payload, selector, mode) {
            if (mode === 'replace') {
                $(selector).replaceWith(payload);
                var context = $(selector);
                if (context.length) {
                    context.parent().bdajax();
                } else {
                    $(document).bdajax();
                }
            } else if (mode === 'inner') {
                $(selector).html(payload);
                $(selector).bdajax();
            }
        },

        continuation: function(definitions) {
            if (!definitions) {
                return;
            }
            this.spinner.hide();
            var definition, target;
            for (var idx in definitions) {
                definition = definitions[idx];
                if (definition.type === 'path') {
                    this.path(definition.path);
                } else if (definition.type === 'action') {
                    target = this.parsetarget(definition.target);
                    this.action({
                        url: target.url,
                        params: target.params,
                        name: definition.name,
                        mode: definition.mode,
                        selector: definition.selector
                    });
                } else if (definition.type === 'event') {
                    this.trigger(
                        definition.name,
                        definition.selector,
                        definition.target
                    );
                } else if (definition.type === 'overlay') {
                    if (definition.close) {
                        var elem = $(definition.selector);
                        var overlay = elem.data('overlay');
                        if (overlay) {
                            overlay.close();
                        }
                    } else {
                        target = this.parsetarget(definition.target);
                        this.overlay({
                            action: definition.action,
                            selector: definition.selector,
                            content_selector: definition.content_selector,
                            url: target.url,
                            params: target.params
                        });
                    }
                } else if (definition.type === 'message') {
                    if (definition.flavor) {
                        var flavors = ['message', 'info', 'warning', 'error'];
                        if (flavors.indexOf(definition.flavor) === -1) {
                            throw "Continuation definition.flavor unknown";
                        }
                        switch (definition.flavor) {
                            case 'message':
                                this.message(definition.payload);
                                break;
                            case 'info':
                                this.info(definition.payload);
                                break;
                            case 'warning':
                                this.warning(definition.payload);
                                break;
                            case 'error':
                                this.error(definition.payload);
                                break;
                        }
                    } else {
                        if (!definition.selector) {
                            throw "Continuation definition.selector expected";
                        }
                        $(definition.selector).html(definition.payload);
                    }
                }
            }
        },

        trigger: function(name, selector, target) {
            var create_event = function() {
                var evt = $.Event(name);
                if (target.url) {
                    evt.ajaxtarget = target;
                } else {
                    evt.ajaxtarget = bdajax.parsetarget(target);
                }
                return evt;
            };
            // _dispatching_handler calls stopPropagation on event which is
            // fine in order to prevent weird behavior on parent DOM elements,
            // especially for standard events. Since upgrade to jQuery 1.9
            // stopPropagation seem to react on the event instance instead of
            // the trigger call for each element returned by selector, at least
            // on custom events, thus we create a separate event instance for
            // each elem returned by selector.
            $(selector).each(function() {
                $(this).trigger(create_event());
            });
        },

        overlay: function(options) {
            var selector = '#ajax-overlay';
            if (options.selector) {
                selector = options.selector;
            }
            var content_selector = '.overlay_content';
            if (options.content_selector) {
                content_selector = options.content_selector;
            }
            var elem = $(selector);
            elem.removeData('overlay');
            var url, params;
            if (options.target) {
                var target = this.parsetarget(options.target);
                url = target.url;
                params = target.params;
            } else {
                url = options.url;
                params = options.params;
            }
            this._perform_ajax_action({
                name: options.action,
                selector: selector + ' ' + content_selector,
                mode: 'inner',
                url: url,
                params: params,
                success: function(data) {
                    bdajax._ajax_action_success(data);
                    // overlays are not displayed if no payload is received.
                    if (!data.payload) {
                        return;
                    }
                    elem.overlay({
                        mask: {
                            color: '#fff',
                            loadSpeed: 200
                        },
                        onClose: function() {
                            var content = $(content_selector,
                                            this.getOverlay());
                            content.html('');
                        },
                        oneInstance: false,
                        closeOnClick: true,
                        fixed: false
                    });
                    elem.data('overlay').load();
                }
            });
        },

        message: function(message) {
            var elem = $('#ajax-message');
            elem.removeData('overlay');
            elem.overlay({
                mask: {
                    color: '#fff',
                    loadSpeed: 200
                },
                onBeforeLoad: function() {
                    var overlay = this.getOverlay();
                    $('.message', overlay).html(message);
                },
                onLoad: function() {
                    elem.find('button:first').focus();
                },
                onBeforeClose: function() {
                    var overlay = this.getOverlay();
                    $('.message', overlay).empty();
                },
                oneInstance: false,
                closeOnClick: false,
                fixed: false,
                top:'20%'
            });
            elem.data('overlay').load();
        },

        error: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('error');
            this.message(message);
        },

        info: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('info');
            this.message(message);
        },

        warning: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('warning');
            this.message(message);
        },

        dialog: function(options, callback) {
            var elem = $('#ajax-dialog');
            elem.removeData('overlay');
            elem.overlay({
                mask: {
                    color: '#fff',
                    loadSpeed: 200
                },
                onBeforeLoad: function() {
                    var overlay = this.getOverlay();
                    var closefunc = this.close;
                    $('.text', overlay).html(options.message);
                    $('button', overlay).unbind();
                    $('button.submit', overlay).bind('click', function() {
                        closefunc();
                        callback(options);
                    });
                    $('button.cancel', overlay).bind('click', function() {
                        closefunc();
                    });
                },
                oneInstance: false,
                closeOnClick: false,
                fixed: false,
                top:'20%'
            });
            elem.data('overlay').load();
        },

        // B/C: bind ajax form handling to all forms providing ajax css class
        bind_ajax_form: function(context) {
            bdajax.prepare_ajax_form($('form.ajax', context));
        },

        // prepare form desired to be an ajax form
        prepare_ajax_form: function(form) {
            form.append('<input type="hidden" name="ajax" value="1" />');
            form.attr('target', 'ajaxformresponse');
            form.unbind().bind('submit', function(event) {
                bdajax.spinner.show();
            });
        },

        // called by iframe response, renders form (i.e. if validation errors)
        render_ajax_form: function(payload, selector, mode) {
            if (!payload) {
                return;
            }
            this.spinner.hide();
            this.fiddle(payload, selector, mode);
        },

        _dispatching_handler: function(event) {
            event.preventDefault();
            event.stopPropagation();
            var elem = $(this);
            var options = {
                elem: elem,
                event: event
            };
            if (elem.attr('ajax:confirm')) {
                options.message = elem.attr('ajax:confirm');
                bdajax.dialog(options, bdajax._do_dispatching);
            } else {
                bdajax._do_dispatching(options);
            }
        },

        _do_dispatching: function(options) {
            var elem = options.elem;
            var event = options.event;
            if (elem.attr('ajax:action')) {
                bdajax._handle_ajax_action(elem, event);
            }
            if (elem.attr('ajax:event')) {
                bdajax._handle_ajax_event(elem);
            }
            if (elem.attr('ajax:overlay')) {
                bdajax._handle_ajax_overlay(elem, event);
            }
            if (elem.attr('ajax:path')) {
                bdajax._handle_ajax_path(elem, event);
            }
        },

        _handle_ajax_path: function(elem, event) {
            var path = elem.attr('ajax:path');
            if (path === 'target') {
                var target;
                if (event.ajaxtarget) {
                    target = event.ajaxtarget;
                } else {
                    target = this.parsetarget(elem.attr('ajax:target'));
                }
                path = target.path;
            }
            this.path(path);
        },

        _handle_ajax_event: function(elem) {
            var target = elem.attr('ajax:target');
            var defs = this._defs_to_array(elem.attr('ajax:event'));
            for (var i = 0; i < defs.length; i++) {
                var def = defs[i];
                def = def.split(':');
                this.trigger(def[0], def[1], target);
            }
        },

        _ajax_action_success: function(data) {
            if (!data) {
                bdajax.error('Empty response');
                bdajax.spinner.hide();
            } else {
                bdajax.fiddle(data.payload, data.selector, data.mode);
                bdajax.continuation(data.continuation);
            }
        },

        _perform_ajax_action: function(options) {
            options.params['bdajax.action'] = options.name;
            options.params['bdajax.mode'] = options.mode;
            options.params['bdajax.selector'] = options.selector;
            this.request({
                url: bdajax.parseurl(options.url) + '/ajaxaction',
                type: 'json',
                params: options.params,
                success: options.success
            });
        },

        _handle_ajax_action: function(elem, event) {
            var target;
            if (event.ajaxtarget) {
                target = event.ajaxtarget;
            } else {
                target = this.parsetarget(elem.attr('ajax:target'));
            }
            var actions = this._defs_to_array(elem.attr('ajax:action'));
            for (var i = 0; i < actions.length; i++) {
                var defs = actions[i].split(':');
                this.action({
                    name: defs[0],
                    selector: defs[1],
                    mode: defs[2],
                    url: target.url,
                    params: target.params
                });
            }
        },

        _handle_ajax_overlay: function(elem, event) {
            var target;
            if (event.ajaxtarget) {
                target = event.ajaxtarget;
            } else {
                target = this.parsetarget(elem.attr('ajax:target'));
            }
            var overlay_attr = elem.attr('ajax:overlay');
            if (overlay_attr.indexOf(':') > -1) {
                var defs = overlay_attr.split(':');
                var options = {
                    action: defs[0],
                    selector: defs[1],
                    url: target.url,
                    params: target.params
                };
                if (defs.length === 3) {
                    options.content_selector = defs[2];
                }
                this.overlay(options);
            } else {
                this.overlay({
                    action: overlay_attr,
                    url: target.url,
                    params: target.params
                });
            }
        },

        _defs_to_array: function(str) {
            // XXX: if space in selector when receiving def str, this will fail
            var arr = str.replace(/\s+/g, ' ').split(' ');
            return arr;
        }
    };

})(jQuery);


/**
 * @license
 * jQuery Tools @VERSION Overlay - Overlay base. Extend it.
 *
 * NO COPYRIGHTS OR LICENSES. DO WHAT YOU LIKE.
 *
 * http://flowplayer.org/tools/overlay/
 *
 * Since: March 2008
 * Date: @DATE
 */
(function($) {

    // static constructs
    $.tools = $.tools || {version: '@VERSION'};

    $.tools.overlay = {

        addEffect: function(name, loadFn, closeFn) {
            effects[name] = [loadFn, closeFn];
        },

        conf: {
            close: null,
            closeOnClick: true,
            closeOnEsc: true,
            closeSpeed: 'fast',
            effect: 'default',

            // since 1.2. fixed positioning not supported by IE6
            fixed: !/msie/.test(navigator.userAgent.toLowerCase()) || navigator.appVersion > 6,

            left: 'center',
            load: false, // 1.2
            mask: null,
            oneInstance: true,
            speed: 'normal',
            target: null, // target element to be overlayed. by default taken from [rel]
            top: '10%'
        }
    };


    var instances = [], effects = {};

    // the default effect. nice and easy!
    $.tools.overlay.addEffect('default',

        /*
            onLoad/onClose functions must be called otherwise none of the
            user supplied callback methods won't be called
        */
        function(pos, onLoad) {

            var conf = this.getConf(),
                 w = $(window);

            if (!conf.fixed)  {
                pos.top += w.scrollTop();
                pos.left += w.scrollLeft();
            }

            pos.position = conf.fixed ? 'fixed' : 'absolute';
            this.getOverlay().css(pos).fadeIn(conf.speed, onLoad);

        }, function(onClose) {
            this.getOverlay().fadeOut(this.getConf().closeSpeed, onClose);
        }
    );


    function Overlay(trigger, conf) {

        // private variables
        var self = this,
             fire = trigger.add(self),
             w = $(window),
             closers,
             overlay,
             opened,
             maskConf = $.tools.expose && (conf.mask || conf.expose),
             uid = Math.random().toString().slice(10);


        // mask configuration
        if (maskConf) {
            if (typeof maskConf == 'string') { maskConf = {color: maskConf}; }
            maskConf.closeOnClick = maskConf.closeOnEsc = false;
        }

        // get overlay and trigger
        var jq = conf.target || trigger.attr("rel");
        overlay = jq ? $(jq) : null || trigger;

        // overlay not found. cannot continue
        if (!overlay.length) { throw "Could not find Overlay: " + jq; }

        // trigger's click event
        if (trigger && trigger.index(overlay) == -1) {
            trigger.click(function(e) {
                self.load(e);
                return e.preventDefault();
            });
        }

        // API methods
        $.extend(self, {

            load: function(e) {

                // can be opened only once
                if (self.isOpened()) { return self; }

                // find the effect
                var eff = effects[conf.effect];
                if (!eff) { throw "Overlay: cannot find effect : \"" + conf.effect + "\""; }

                // close other instances?
                if (conf.oneInstance) {
                    $.each(instances, function() {
                        this.close(e);
                    });
                }

                // onBeforeLoad
                e = e || $.Event();
                e.type = "onBeforeLoad";
                fire.trigger(e);
                if (e.isDefaultPrevented()) { return self; }

                // opened
                opened = true;

                // possible mask effect
                if (maskConf) { $(overlay).expose(maskConf); }

                // position & dimensions
                var top = conf.top,
                     left = conf.left,
                     oWidth = overlay.outerWidth(true),
                     oHeight = overlay.outerHeight(true);

                if (typeof top == 'string')  {
                    top = top == 'center' ? Math.max((w.height() - oHeight) / 2, 0) :
                        parseInt(top, 10) / 100 * w.height();
                }

                if (left == 'center') { left = Math.max((w.width() - oWidth) / 2, 0); }


                // load effect
                eff[0].call(self, {top: top, left: left}, function() {
                    if (opened) {
                        e.type = "onLoad";
                        fire.trigger(e);
                    }
                });

                // mask.click closes overlay
                if (maskConf && conf.closeOnClick) {
                    $.mask.getMask().one("click", self.close);
                }

                // when window is clicked outside overlay, we close
                if (conf.closeOnClick) {
                    $(document).on("click." + uid, function(e) {
                        if (!$(e.target).parents(overlay).length) {
                            self.close(e);
                        }
                    });
                }

                // keyboard::escape
                if (conf.closeOnEsc) {

                    // one callback is enough if multiple instances are loaded simultaneously
                    $(document).on("keydown." + uid, function(e) {
                        if (e.keyCode == 27) {
                            self.close(e);
                        }
                    });
                }


                return self;
            },

            close: function(e) {

                if (!self.isOpened()) { return self; }

                e = e || $.Event();
                e.type = "onBeforeClose";
                fire.trigger(e);
                if (e.isDefaultPrevented()) { return; }

                opened = false;

                // close effect
                effects[conf.effect][1].call(self, function() {
                    e.type = "onClose";
                    fire.trigger(e);
                });

                // unbind the keyboard / clicking actions
                $(document).off("click." + uid + " keydown." + uid);

                if (maskConf) {
                    $.mask.close();
                }

                return self;
            },

            getOverlay: function() {
                return overlay;
            },

            getTrigger: function() {
                return trigger;
            },

            getClosers: function() {
                return closers;
            },

            isOpened: function()  {
                return opened;
            },

            // manipulate start, finish and speeds
            getConf: function() {
                return conf;
            }

        });

        // callbacks
        $.each("onBeforeLoad,onStart,onLoad,onBeforeClose,onClose".split(","), function(i, name) {

            // configuration
            if ($.isFunction(conf[name])) {
                $(self).on(name, conf[name]);
            }

            // API
            self[name] = function(fn) {
                if (fn) { $(self).on(name, fn); }
                return self;
            };
        });

        // close button
        closers = overlay.find(conf.close || ".close");

        if (!closers.length && !conf.close) {
            closers = $('<a class="close"></a>');
            overlay.prepend(closers);
        }

        closers.click(function(e) {
            self.close(e);
        });

        // autoload
        if (conf.load) { self.load(); }

    }

    // jQuery plugin initialization
    $.fn.overlay = function(conf) {

        // already constructed --> return API
        var el = this.data("overlay");
        if (el) { return el; }

        if ($.isFunction(conf)) {
            conf = {onBeforeLoad: conf};
        }

        conf = $.extend(true, {}, $.tools.overlay.conf, conf);

        this.each(function() {
            el = new Overlay($(this), conf);
            instances.push(el);
            $(this).data("overlay", el);
        });

        return conf.api ? el: this;
    };

})(jQuery);

