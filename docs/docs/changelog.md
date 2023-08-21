---
pdf:
  filename: Changelog
  title: Changelog & License for MkDocs PDF Generate Plugin
  type: Changelog
  revision: 0.2.2   
  toc_txt: true
  csv_name: Plugin Changelog
---

# Changelog & License

## License

MIT License

Copyright (c) 2023 Randy Duodu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Changelog

0.2.2
-----
Released: **under development**

* Removed disclaimer Jinja variable from the list of variables you can use in your custom Jinja template.
* Added code comments and docstrings to help contributors understand the code base.
* Added support for inserting customised legal information and disclaimer into generated PDF documents'.
* Updated documentation.
* Fix MkDocs build failure issue.
* Improvement: Compatibility with MkDocs >= 1.5 and Markdown 3.4.4. Fix for issue [#20](https://github.com/iSOLveIT/mkdocs-pdf-generate/issues/20).

0.2.1
-----
Released: **22-03-2023**

* Updated documentation and made minor changes to plugin code.
* Added the `csv_name` local option.
* Improvement: Added feature to generate a CSV file for all documents with the `toc_txt` local option set to `true`.
* Improvement: Added changes that appends the revision number of a document to the filename.
* Bugfix: Added default URL to use if `site_url` is not defined in mkdocs.yml. Fix for issue [#15](https://github.com/iSOLveIT/mkdocs-pdf-generate/issues/15).
* Improvement: Added the `toc_txt` local option that allows users to build TXT file containing the Table of Contents.
* Minor improvements: Rewrote logging messages.

0.2.0
-----
Released: **14-02-2023**

* Package setup: Changed package from using setuptools to pyproject.toml.

