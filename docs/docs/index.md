---
pdf:
  build: false  
  filename: Welcome Page
  title: Introduction for MkDocs PDF Generate Plugin
  subtitle: Overview   
  type: Home
  revision: 0.2.2
---

# MkDocs PDF Generate Plugin

The pdf-generate plugin will generate separate PDF files for each markdown page
in your MkDocs repository using [WeasyPrint](http://weasyprint.org/). 
The exported documents support many advanced features such as table of contents, customisable cover page, 
ability to control page orientation, support for CSS paged media module 
[CSS paged media module](https://developer.mozilla.org/en-US/docs/Web/CSS/@page)
, and using MkDocs page metadata to generate cover page.

## Requirements

1. This package requires MkDocs version 1.4.2 or higher (MkDocs <1.4.2 might work as well)
2. Python 3.8 or higher
3. WeasyPrint depends on cairo, Pango and GDK-PixBuf which need to be installed separately. Please follow the installation instructions for your platform carefully:
    - [Linux][weasyprint-linux]
    - [MacOS][weasyprint-macos]
    - [Windows][weasyprint-windows]
4. Explicit support for your mkdocs theme is probably required. As of now, the only supported theme is [mkdocs-material][mkdocs-material]. 
   A generic version will just generate the PDF files and put the download link into a `<link>` tag.

## Installation

**Install package with pip:**  

=== "Linux & MacOS"

    ```bash
    python -m pip install -e "git+https://github.com/iSOLveIT/mkdocs-pdf-generate/#egg=mkdocs-pdf-generate"
    ```

=== "Windows"

    ```powershell
    C:> python -m pip install -e "git+https://github.com/iSOLveIT/mkdocs-pdf-generate/#egg=mkdocs-pdf-generate"
    ```

**Install from source repository in a virtual environment:**

```bash
cd [YOUR_PROJECT_DIRECTORY]
git clone https://github.com/iSOLveIT/mkdocs-pdf-generate
cd mkdocs-pdf-generate
pip install -e .
```

**Enable the plugin in your `mkdocs.yml`:**

```yaml
plugins:
    - search
    - pdf-generate
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

More information about plugins in the [MkDocs documentation](http://www.mkdocs.org/user-guide/plugins/).

## Contributing

From reporting a bug to submitting a pull request: every contribution is appreciated and welcome. Report bugs, ask questions and request features using [Github issues][github-issues].

If you want to contribute to the code of this project, please read the [Contribution Guidelines][contributing].

### **Special thanks**

- [Terry Zhao][terry] the author of the [MkDocs PDF Export Plugin][mkdocs-pdf-export-plugin] the source of our inspiration. We've used some of his code in this project.

[github-issues]: https://github.com/iSOLveIT/mkdocs-pdf-generate/issues
[contributing]: https://github.com/iSOLveIT/mkdocs-pdf-generate/blob/main/CONTRIBUTING.md
[terry]: https://github.com/zhaoterryy
[mkdocs-pdf-export-plugin]: https://github.com/zhaoterryy/mkdocs-pdf-export-plugin
[weasyprint-linux]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#linux
[weasyprint-macos]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#macos
[weasyprint-windows]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
[mkdocs-material]: https://github.com/squidfunk/mkdocs-material