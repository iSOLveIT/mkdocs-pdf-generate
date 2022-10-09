# from bs4 import BeautifulSoup


def get_stylesheet() -> str:
    return """
.md-container {
    display: block;
    padding-top: 0;
}

.md-main {
    display: block;
    height: inherit;
}

.md-main__inner {
    height: inherit;
    padding-top: 0;
}

.md-typeset .codehilitetable .linenos {
    display: none;
}

.md-typeset .footnote-ref {
    display: inline-block;
}

.md-typeset a.footnote-backref {
    transform: translateX(0);
    opacity: 1;
}

"""


def modify_html(html: str, href: str) -> str:

    # SVG 'file-download' size 2x from fontawesome: https://fontawesome.com/icons/file-download?style=solid
    # resized to 16px width * height
    a_tag = '<a class="md-content__button md-icon" id="pdf_download" href="{}" download title="Download PDF">'.format(
        href
    )
    span_tag = "<span>Download </span>"
    icon = (
        '<svg viewBox="47.404 4.597 13.5 18" xmlns="http://www.w3.org/2000/svg">'
        '<path id="Icon_awesome-file-pdf" data-name="Icon awesome-file-pdf" '
        'd="M 53.799 13.597 C 53.64 13.061 53.616 12.495 53.729 11.948 C 54.024 11.952 '
        "53.996 13.249 53.799 13.597 Z M 53.739 15.256 C 53.461 16.013 53.127 "
        "16.749 52.739 17.456 C 53.451 17.133 54.191 16.875 54.95 16.686 C 54.452 "
        "16.3 54.04 15.814 53.739 15.26 L 53.739 15.256 Z M 50.431 19.647 C 50.431 "
        "19.675 50.895 19.457 51.658 18.234 C 51.161 18.621 50.745 19.101 50.431 19.647 Z M "
        "56.123 10.222 L 60.904 10.222 L 60.904 21.753 C 60.905 22.22 60.527 22.598 60.06 "
        "22.597 L 48.248 22.597 C 47.781 22.598 47.403 22.22 47.404 21.753 L 47.404 "
        "5.441 C 47.403 4.974 47.781 4.596 48.248 4.597 L 55.279 4.597 L 55.279 9.378 C 55.28 "
        "9.844 55.657 10.221 56.123 10.222 Z M 55.842 16.262 C 55.135 15.828 54.604 15.158 54.342 "
        "14.371 C 54.585 13.645 54.659 12.873 54.56 12.114 C 54.474 11.442 53.693 11.115 53.154 "
        "11.526 C 53.034 11.617 52.94 11.737 52.88 11.875 C 52.761 12.787 52.858 13.715 53.165 "
        "14.582 C 52.737 15.611 52.258 16.617 51.728 17.597 C 51.728 17.597 51.728 17.597 "
        "51.721 17.597 C 50.768 18.086 49.134 19.161 49.805 19.988 C 50.001 20.201 50.272 20.327 "
        "50.561 20.34 C 51.19 20.34 51.816 19.707 52.709 18.167 C 53.614 17.828 54.542 17.556 "
        "55.486 17.351 C 56.176 17.744 56.944 17.979 57.736 18.037 C 58.436 18.055 58.894 17.308 "
        "58.559 16.693 C 58.523 16.627 58.48 16.566 58.429 16.511 C 57.94 16.033 56.52 16.17 "
        "55.841 16.258 L 55.842 16.262 Z M 60.658 8.289 L 57.213 4.843 C 57.054 4.685 56.839 "
        "4.596 56.615 4.597 L 56.404 4.597 L 56.404 9.097 L 60.904 9.097 L 60.904 8.883 C 60.904 "
        "8.66 60.816 8.446 60.658 8.288 L 60.658 8.289 Z M 58.053 17.264 C 58.197 17.169 57.965 16.846 56.553 "
        '16.948 C 57.852 17.503 58.053 17.264 58.053 17.264 Z" fill="red"/></svg>'
    )
    button_tag = a_tag + span_tag + icon + "</a>"

    # insert into HTML
    insert_point = '<article class="md-content__inner md-typeset">'
    html = html.replace(insert_point, insert_point + button_tag)

    return html
