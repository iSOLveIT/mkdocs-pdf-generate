# MkDocs PDF Generate 

*An MkDocs plugin to generate individual PDF files from content pages.*

The pdf-generate plugin will generate separate PDF files for each markdown page
in your MkDocs repository using [WeasyPrint](http://weasyprint.org/). 
The exported documents support many advanced features such as table of contents, customisable cover page
, support for CSS paged media module [CSS paged media module](https://developer.mozilla.org/en-US/docs/Web/CSS/@page)
, and using MkDocs page metadata to generate cover page.

## Requirements

1. This package requires MkDocs version 1.0 or higher (0.17 works as well)
2. Python 3.8 or higher
3. WeasyPrint depends on cairo, Pango and GDK-PixBuf which need to be installed separately. Please follow the installation instructions for your platform carefully:
    - [Linux][weasyprint-linux]
    - [MacOS][weasyprint-macos]
    - [Windows][weasyprint-windows]
4. Explicit support for your mkdocs theme is probably required. As of now, the only supported theme is [mkdocs-material][mkdocs-material]. 
   A generic version will just generate the PDF files and put the download link into a `<link>` tag.

## Installation

Install the package with pip:

**Linux & MacOS**
```bash
python -m pip install -e "git+https://github.com/iSOLveIT/mkdocs-pdf-generate/#egg=mkdocs-pdf-generate"
```

**Windows**
```powershell
C:> python -m pip install -e "git+https://github.com/iSOLveIT/mkdocs-pdf-generate/#egg=mkdocs-pdf-generate"
```

Install from source repository in a virtual environment:

```bash
cd [YOUR_PROJECT_DIRECTORY]
git clone https://github.com/iSOLveIT/mkdocs-pdf-generate
cd mkdocs-pdf-generate
pip install -e .
```

Enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
    - search
    - pdf-generate
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

More information about plugins in the [MkDocs documentation][mkdocs-plugins].

## Testing

When building your repository with `mkdocs build`, you should now see the following message at the end of your build output:

> Converting 17 files to PDF took 15.6s

In your `site_dir` you should now have a PDF file for every markdown page.

## Options

For more information on options, visit the [plugin's documentation](https://isolveit.github.io/mkdocs-pdf-generate/).

## Adjusting the output

The resulting PDF can be customized easily by adding a custom stylesheet such as the following:

```
@page {
    size: a4 portrait;
    margin: 25mm 10mm 25mm 10mm;
    counter-increment: page;
    font-family: "Roboto","Helvetica Neue",Helvetica,Arial,sans-serif;
    white-space: pre;
    color: grey;
    @top-left {
        content: '© 2018 My Company';
    }
    @top-center {
        content: string(chapter);
    }
    @top-right {
        content: 'Page ' counter(page);
    }
}
```
For this to take effect, use the `extra_css` directive in mkdocs.yml, as described in the [MkDocs user guide][extra-css].

### Contributing

From reporting a bug to submitting a pull request: every contribution is appreciated and welcome. Report bugs, ask questions and request features using [GitHub issues][github-issues].

If you want to contribute to the code of this project, please read the [Contribution Guidelines][contributing].

### **Special thanks**
- [Terry Zhao][terry] the author of the [MkDocs PDF Export Plugin][mkdocs-pdf-export-plugin] the source of our inspiration. We've used some of his code in this project.

[github-issues]: https://github.com/iSOLveIT/mkdocs-pdf-generate/issues
[terry]: https://github.com/zhaoterryy
[mkdocs-pdf-export-plugin]: https://github.com/zhaoterryy/mkdocs-pdf-export-plugin
[weasyprint-linux]: https://weasyprint.readthedocs.io/en/latest/install.html#linux
[weasyprint-macos]: https://weasyprint.readthedocs.io/en/latest/install.html#os-x
[weasyprint-windows]: https://weasyprint.readthedocs.io/en/latest/install.html#windows
[mkdocs-plugins]: http://www.mkdocs.org/user-guide/plugins/
[mkdocs-material]: https://github.com/squidfunk/mkdocs-material
[contributing]: CONTRIBUTING.md
[extra-css]: https://www.mkdocs.org/user-guide/configuration/#extra_css
