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

Then in another terminal, you can use ``curl`` or whatever to send a
symbolication request. For example::

    curl -d '{"jobs": [{"stacks":[[[0,6516407],[0,12856365]]],"memoryMap":[["xul.pdb","09F9D7ECF31F60E34C4C44205044422E1"],["wntdll.pdb","D74F79EB1F8D4A45ABCD2F476CCABACC2"]]}]}' http://localhost:5000/symbolicate/v5


Set up for production
=====================

Don't use this in production--it's a prototype.


Symbolication requests
======================

:URL: ``/symbolicate/v5``
:Method: POST
:Payload: JSON

The request payload consists of one or more jobs. Each job contains an array of
stacks to symbolicate and an array of modules.

For example::

  {
    "jobs": [
      {
        "stacks": [
          [
            [0, 6516407],
            [0, 12856365]
          ]
        ],
        "memoryMap": [
          ["xul.pdb", "09F9D7ECF31F60E34C4C44205044422E1"],
          ["wntdll.pdb","D74F79EB1F8D4A45ABCD2F476CCABACC2"]
        ]
      }
    ]
  }

This payload has a single job in it with a single stack to symbolicate. It has
two known modules.

The response contains a "results" object which is an array of job results--one
for each job sent in.

For example::

  {
    "results": [
      {
        "found_modules": {
          "wntdll.pdb/D74F79EB1F8D4A45ABCD2F476CCABACC2": null,
          "xul.pdb/09F9D7ECF31F60E34C4C44205044422E1": true
        },
        "stacks": [
          [
            {
              "frame": 0,
              "function": "mozilla::ConsoleReportCollector::FlushReportsToConsole(unsigned long long, nsIConsoleReportCollector::ReportAction)",
              "function_offset": "0x207",
              "line": 72,
              "module": "xul.pdb",
              "module_offset": "0x636eb7"
            },
            {
              "frame": 1,
              "function": "mozilla::net::HttpBaseChannel::MaybeFlushConsoleReports()",
              "function_offset": "0x6d",
              "line": 4503,
              "module": "xul.pdb",
              "module_offset": "0xc42c2d"
            }
          ]
        ]
      }
    ]
  }

Each frame has the following:

* frame: The frame of the stack.
* function: The symbol.
* function offset: The module offset - sym addr in hex.
* line: The line number.
* module: The module name.
* module_offset: The module offset in hex.


References
==========

https://github.com/getsentry/symbolic/blob/master/README.md
   Symbolic README

https://docs.rs/symbolic/
   Symbolic docs

https://chromium.googlesource.com/breakpad/breakpad/+/master/docs/symbol_files.md
   Breakpad symbols docs

https://chromium.googlesource.com/breakpad/breakpad/+/master/docs/stack_walking.md
   Breakpad stackwalking docs

https://tecken.readthedocs.io/en/latest/symbolication.html
   Tecken symbolication docs
