from setuptools import setup


setup(
    name="mkdocs-pdf-generate",
    version="0.1.1",
    description="An MkDocs plugin to generate individual PDF files from content pages.",
    long_description="The pdf-generate plugin will generate separate PDF files for each markdown page "
    "in your MkDocs repository using WeasyPrint. "
    "The exported documents support many advanced features such as "
    "table of contents, customisable cover page, "
    "support for CSS paged media module, and using MkDocs page metadata to generate cover page.",
    keywords="mkdocs pdf export generate weasyprint",
    url="https://github.com/iSOLveIT/mkdocs-pdf-generate",
    author="Duodu Randy",
    author_email="duodurandy19@gmail.com",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "mkdocs>=1.3.0",
        "weasyprint>=54.0",
        "beautifulsoup4>=4.6.3",
        "jinja2>=3.0.0",
        "pathlib>=1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["mkdocs_pdf_generate"],
    package_dir={"mkdocs_pdf_generate": "mkdocs_pdf_generate"},
    package_data={
        "mkdocs_pdf_generate": [
            "styles/*",
            "preprocessor/*",
            "templates/*",
            "themes/*",
            "preprocessor/*/*",
            "templates/*/*",
        ]
    },
    entry_points={
        "mkdocs.plugins": [
            "pdf-generate = mkdocs_pdf_generate.plugin:PdfGeneratePlugin"
        ]
    },
)
