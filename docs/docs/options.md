---
pdf:
  filename: Plugin Options
  title: Options for MkDocs PDF Generate Plugin
  type: Options
  revision: 0.2    
---

# Options

The plugin allows users to pass in both global and local options.

!!! note

    Local options has a higher precedence than global options.


## Global Options

Some of these global options are used as default options when local options are not set.
The global options are passed to the plugin through `mkdocs.yml`:

```yaml
plugins:
    - pdf-generate:
        author: "Randy Duodu"
        author_logo: img/logo.svg
        copyright: "Copyright © 2022 - MkDocs PDF Generate"
        disclaimer: "Disclaimer: Content can change at anytime and best to refer to website for latest information."
        cover: true
        cover_title: TITLE TEXT
        cover_subtitle: SUBTITLE TEXT
        custom_template_path: TEMPLATES PATH
        toc: false
        toc_level: 3
        toc_title: TOC TITLE TEXT
        toc_numbering: true
        cover_images:
          default: img/default.svg
          type1: img/type1.png
          type2: https://example.com/cover.svg
        enabled_if_env: ENABLE_PDF_EXPORT
```

### for Cover

#### `cover`

Set the value to `false` if you don't need a cover page. <br>  
**default**: `true`

#### `cover_title`

Set the title text in cover page. 

!!! note
  
    The following rule is applied when setting the value for cover title text in cover page.

    Cover Title precedence:

    1. [title](#title) (local pdf metadata option) 
    2. H1 heading for page 
    3. [cover title](#cover_title) (global) 
    4. `site_name` variable in your project's `mkdocs.yml`

**default**: use `site_name` in your project's `mkdocs.yml`

#### `cover_subtitle`

Set the subtitle text in cover page.

!!! note
  
    The following rule is applied when setting the value for cover subtitle text in cover page.

    Cover Subtitle precedence:

    1. [subtitle](#subtitle) (local pdf metadata option) 
    2. [type](#type) (local pdf metadata option)
    3. [cover subtitle](#cover_subtitle) (global) 

**default**: `None`

#### `author`

Set the author text. <br>  
**default**: use `site_author` in your project's `mkdocs.yml`

#### `author_logo`

Provide a logo image which you can use in the cover page. <br>

!!! tip
    
    Using an SVG image as the value for author logo is recommended.

**default**: use `theme.logo` in your project's `mkdocs.yml`

#### `copyright`

Set the copyright text. <br>  
**default**: use `copyright` in your project's `mkdocs.yml`

#### `disclaimer`

Set the disclaimer text. <br>  
**default**: `None`

#### `cover_images`

Set the cover image for specific document types. 

The option takes a `key-value` pair where the `key` must be the same value as you specified for the [type](#type) 
local pdf metadata option.

The `value` for a `key` must be the path to the image.
<br>  

**Example:**
```yaml
- pdf-generate:
    cover_images:
      default: img/home-banner.svg
      home: img/manual-banner.svg
      options: img/project-banner.svg
      customize: img/tutorial-banner.svg
```

!!! note
    
    Apart from the `default` key-value pair under cover_images, the other key-value pairs can have user-defined values.

    Recommended: You must specify an image path for the `default` key-value pair. We will use the image as 
    the cover image for any document that does not specify the [type](#type) local pdf metadata option.

**default**: `None`

### for Heading and TOC

#### `toc`

Set the value to `false` if you don't need a table of content section in the PDF document. <br>  
**default**: `true`

#### `toc_title`

Set the title text for _Table of Contents_. <br>  
**default**: `Table of Contents`  

#### `toc_level`

Set the level of _Table of Contents_. This value is enabled in the range of from `1` to `3`. <br>  
**default**: `3`

!!! note

    The developers are working on extending the range for `toc_level` option from a value between
    `1-3` to a value between `1-6`.

#### `toc_numbering`

Set the value to `false` if you don't want your table of contents to be numbered in the PDF document. <br>  
**default**: `true`


### ... and more

#### `custom_template_path`

The path where your custom cover template (e.g. `cover.html`) is located.<br>

!!! info

    The custom template's filename should be `cover` with any of these file extensions
    `.html.j2`, `.html.jinja2`, `.html`, or `.htm`.

    You can refer to this [example](customise/customisation.md#using-custom-cover-template) 
    about how to use a custom cover template. 

**default**: `templates`  

#### `enabled_if_env`

Setting this option will generate PDF files only if there is an environment variable set to 1. 
The environment variable must match the value of `enabled_if_env`.

This is useful to disable building the PDF files during development, since it can take a long time to export all files. <br>  
**default**: `None`

PDF generation can take significantly longer than HTML generation which can slow down MkDocs built-in dev-server.

Adding `enabled_if_env: ENABLE_PDF_EXPORT` disables PDF generation during development and runs the dev-server normally:

```bash
$ mkdocs serve
INFO     -  Building documentation...
INFO     -  PDF export is disabled (set environment variable ENABLE_PDF_EXPORT to 1 to enable)
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.54 seconds
INFO     -  [08:51:24] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO     -  [08:51:24] Serving on http://127.0.0.1:8000/

```

and to build PDF files, set the `ENABLE_PDF_EXPORT=1` environment variable:

```bash
$ ENABLE_PDF_EXPORT=1 mkdocs build
...
INFO    -  Converting 2 files to PDF took 1.82s
INFO    -  Documentation built in 2.29 seconds
```
  
#### `verbose`

Setting this to `true` will show all WeasyPrint debug messages during the build. <br> 
**default**: `false`

#### `media_type` 

Allows you to use a different CSS media type (or a custom one like `pdf-generate`) for the PDF export. <br>
**default**: `print`

#### `theme_handler_path`

Allows you to specify a custom theme handler module. This path must be ***relative to your project root*** (See example below). <br>
**default**: `None`

`mkdocs.yml`:
```yaml
plugins:
	- pdf-generate:
		theme_handler_path: theme-handler

```

```bash
project-root

├── theme-handler.py

├── docs

├── mkdocs.yml

├── site

.

.

```

## Local Options

The plugin allows you to set document specific options using the Markdown page metadata. 
If a page metadata is specified, it has higher precedence than the [global options](#global-options).

The local options are specified in the specific Markdown document you want to use:

```markdown
---
pdf:
  - build: false  
  - filename: Plugin Options
  - title: Options for MkDocs PDF Generate Plugin
  - type: Manual
  - revision: 0.2
---
```

The following options are available:

* build
* title
* subtitle
* type
* filename
* revision

### `build`

Allows you to specify whether to generate a PDF file for a Markdown file. Value is `true` or `false`.

!!! note 

    The function of the build option is different from that of the [enabled_if_env](#enabled_if_env).
    The `build` option disables PDF generation for a single Markdown file while 
    `enabled_if_env` disables PDF generation for the entire project.

**default**: `true`

### `title`

Set the title text in cover page. 

### `subtitle`

Set the subtitle text in cover page. 

### `type`

Set the document type. <br>
**NB:** We use the value for this option in selecting the document's cover image from 
the [cover_images](#cover_images) option.

### `filename`

Set the filename to use for a specific page when downloading the PDF document.

!!! note

    Filename precedence: 

    1. [filename](#filename) (local pdf metadata) - formatted such that all are valid characters
    2. [title](#title) (local pdf metadata) - formatted such that all are valid characters 
    3. H1 - formatted such that all are valid characters

### `revision`

Set the revision text in cover page. 
