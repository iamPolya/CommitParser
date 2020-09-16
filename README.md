# CommitParser

**This is a little parser for collecting commits from github.**

**Simple structure:**

* parser.py
* notebook.ipynb


parser.py parses commits of selected repository and then it makes a folder with:
 * json files for every commit with changes
 * csv dataset with general data
 
 There are some information in notebook.ipynb:
 * sorted list of authors by count of commits
 * authors with the biggest commit
 * authors with the smallest commit
 * files sorted by frequency of changes
 