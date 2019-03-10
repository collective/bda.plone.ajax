Changes
=======

2.0 (2019-03-10)
----------------

- Drop Plone 4 support (Needs 5.1+). 
  [agitator]
  
- Add Python 3 support.
  [agitator]
  
- Minimal custom jquerytools with overlay added, no more dependency on ``plone.app.jquerytools``.
  [agitator]


1.8 (2019-02-08)
----------------

- Depend on ``Products.CMFPlone`` instead of ``Plone`` to not fetch unnecessary dependencies.
  [thet]

- Check whether child is null before searching for elements by tag name in
  ajax form response.
  [rnix]

- Adopt to ``bdajax`` 1.10.
  [rnix]


1.7 (2017-03-10)
----------------

- Add ``_authenticator`` hidden field when rendering ajax forms in order to
  make CSRF protection work properly.
  [rnix]

- Plone 5 Update, registered as legacy bundle
  [agitator, rnix]


1.6 (2015-06-25)
----------------

- give ``ajaxaction`` response explicit ``Content-Type: application/json``
  [jensens, 2015-06-25]

- log formerly catched and hidden exceptions with severity error to error log.
  [jensens, 2015-06-25]

- Disable diazo theming in ``ajaxaction`` and ``ajaxform`` browser views.
  [rnix, 2014-12-10]

- Add ``AjaxPath`` continuation. Can be used as of ``bdajax`` 1.6.
  [rnix, 2014-12-10]


1.5
---

- Add ajaxform convenience browser page.
  [rnix, 2014-02-04]


1.4
---

- Cleanup docs.
  [rnix, 2013-10-21]

- Do not load examples by default.
  [rnix, 2013-10-21]

- Add abstract batch for buidling ajax batches.
  [rnix, 2013-10-20]


1.3
---

- Provide overlay configuration.
  [rnix, 2012-08-06]

- Provide form continuation.
  [rnix, 2012-08-06]


1.2.2
-----

- render viewlet in IPortalTop, so it pops up centered and not at the end of
  the site.
  [jensens, 2011-12-02]

- add z3c.autoinclude entry point.
  [jensens, 2011-12-02]


1.2.1
-----

- display ``bdajax.message`` with traceback if ``ajaxaction`` throws uncaught
  exception.
  [rnix]


1.2
---

- add ajax continuation support and continuation helper objects and functions.
  [rnix]


1.1
---

- add examples.
  [rnix]

- add ajaxaction view.
  [rnix]


1.0
---

- make it work.
  [rnix]
