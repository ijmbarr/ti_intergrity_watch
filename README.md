# Introduction

A set of short scripts designed to parse released documents from UK ministerial meetings and aggregate the results into a common format. 

These scripts were written quickly to do a one off job. As such they are provided "as is" and with no guarantee of support or maintenance from me.

If there is interest in the work here, certain elements could be built up into stand alone tools, but give the work required to do this, the end would need to justify the means.

# What's going on?
Most of the development took place in jupyter notebooks inside the "notebook" directory. notebook/explore.ipynb is the entry point for the script.

The script runs over the links in the excel file "data/Ministerial meetings - working file-1.xlsx", provided by transparency international (TI), downloading each file and attempting to parse it using tool in the cleaner directory.

# TODO
- separate the logic that extracts tables from documents from the code that looks for specific tables about meetings
- stop using error checking to catch unwanted tables
- add unit testing
- standardise the interfaces between parsers
- document everything
- finish the .doc parser
