========================
Sherwin Syms (prototype)
========================

Prototype web app for symbolicating stacks. Built on top of `symbolic
<https://github.com/getsentry/symbolic>`_.

:License: MPLv2
:Code: https://github.com/willkg/sherwin-syms/
:Issues: https://github.com/willkg/sherwin-syms/issues


Set up for hacking
==================

1. Clone the repository
2. ``make my.env`` and edit ``my.env`` file
3. ``make build`` to build the app image
4. ``make run`` to run the web app locally in development mode


Set up for production
=====================

Don't use this in production--it's a prototype.


Symbolication requests
======================

:URL: ``/symbolicate/v6``
:Method: POST
:Payload: JSON

FIXME(willkg): define request and response structures here
