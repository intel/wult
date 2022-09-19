.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

=========================
Viewing wult reports
=========================

:save_as: pages/howto-view-local.html

.. contents:: Table of Contents

Suppose you have already generated a *wult* HTML report using the `wult report` command. There are
a couple of ways that you can view this report. See below for details of the options wult offers for
viewing reports.

In addition, read `this warning <#securely-view-wult-html-reports>`_ for advice on how to securely
view wult HTML reports.

index.html
----------

As of v1.10.39, 'index.html' files in wult report directories can be used to view wult HTML reports
locally and on a web server. Simply open the file in your web browser of choice.

   When viewing a report locally, the browser may be unable to read report files due to a security
   restriction on web browsers. If this happens, the report page will prompt you to upload the report
   directory to the browser. Following upload, the report should render.

Python Script (serve_directory.py)
----------------------------------

To further facilitate browsing HTML reports, as of v1.10.30, wult HTML reports include a Python
script. Note that the script requires that your system already has Python 3.5 or higher installed.

The 'serve_directory.py' script found in the root directory of wult HTML reports can be used to view
one or more reports at the same time. Intended usage is as follows:

1. Run the script (e.g. by double-clicking on it in Windows Explorer).
2. Select a directory containing multiple reports when prompted to select a directory.
3. Once you have finished browsing the reports, make sure to stop the script you started in step 2.
   If a new terminal window was created when you ran the script in step 2, you can do this by
   closing this window.

View multiple reports locally
-----------------------------

If you want to view many reports in one session, consider starting the HTTP server in a parent
directory of the reports. This will allow you to navigate in the browser between different reports.

Do this by using a parent directory instead of the report directory for any of the above methods.

Securely view wult HTML reports
-------------------------------

Please consider disabling all untrusted browser extensions while viewing *wult* HTML reports.

Browser extensions have varying levels of permissions. For example, some extensions require that the
user allows them to access and distribute the data they are viewing in-browser. This means that it
is possible for some browser extensions to view and share the contents of *wult* HTML reports.

For Google chrome, you can inspect the permissions of your extensions by visiting
`chrome://extensions`. In Firefox, the same thing can be done at `about:addons`.
