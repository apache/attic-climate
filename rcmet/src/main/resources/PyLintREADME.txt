OVERVIEW:

The code within RCMES has been linted using a project specific set of parameters.  We have blended Python's PEP-8
while also including some Java formatting (namely camelCase instead of underscores).

You don't really need to know all the particulars, but if you are curious you can look at the pyLintRcFile.txt in 
this directory for full details.


HOW TO LINT THE CODE:

If you are contributing to this code base then you will need to comply with the code convention standards set forth
by the project team.  We have used PyLint to check for code correctness, and the included pyLintRcFile.txt can be
used with PyLint (http://pypi.python.org/pypi/pylint/).

After you have installed pylint follow these directions.  Happy linting!

Assuming you want to lint the metrics.py file within lib/rcmes, do the following

$> cd rcmes/rcmet/src/main/python/lib/rcmes
$> pylint --rcfile=../../../resources/pyLintRcFile.txt metrics.py

You will be presented with a Report of any Warnings, Conventions, Errors, or Refactoring opportunities as well as
variable name conventions, etc..  For more about the meaning of the report look up the PyLint documentation online.

This will help the team keep the codebase clean and consistent as multiple team members contribute code.