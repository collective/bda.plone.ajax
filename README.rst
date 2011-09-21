Integration package
===================

This is the plone integration package for
`bdajax <http://pypi.python.org/pypi/bdajax/>`_.


Installation
============

  * make egg available in your instance
  
  * apply extension profile


Usage
=====

This package ships with demos. See examples folder in source code for more
details.

This package ships with AJAX continuation helper objects and functions.
See ``bda.plone.ajax.__init__`` for details.


Contributors
============

    - Robert Niederreiter <rnix@squarewave.at>


Changes
=======

1.2.1
-----

- display ``bdajax.message`` with traceback if ``ajaxaction`` throws uncaught
  exception
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
