#!/usr/bin/env python3
"""
https://askubuntu.com/questions/1516422/cgi-script-works-locally-but-fails-with-404-error-on-server
"""

import cgi

print("Content-Type: text/html")
print()
print("<html><body><h1>Test CGI Script for mysite.com</h1>")
# kudos to https://stackoverflow.com/a/3582540
arguments = cgi.FieldStorage()
for i in arguments.keys():
    print("<p>" + arguments[i].value + "</p>")
# kudos to https://docs.python.org/3/library/cgi.html#cgi.print_environ_usage
print("<br>")
cgi.print_environ_usage()
print("</body></html>")
