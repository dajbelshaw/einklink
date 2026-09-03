#!/usr/bin/env python3

import re
import shutil
from pathlib import Path


def change_html_source_code(code, mode):
    '''Modifies an HTML source-code to either auto|dark|light mode.

    This function does two changes:

    * Adds a CSS class to the <html> element.
    * Adds a '-dark' or '-light' suffix to href="…" attributes that are marked with AUTOLIGHTDARK.

    This function is stupid. It is stupidly simple.
    This function does not understand HTML, XML, or any logic.
    This function does a simple text substitution (i.e. search-and-replace).

    A more complicated function would be more powerful, but isn't needed for our purposes here.
    '''

    match mode:
        case 'auto':
            html_class = 'auto'
            file_suffix = ''
        case 'light' | 'dark':
            html_class = mode
            file_suffix = '-' + mode
        case _:
            raise ValueError('Unsupported mode: {!r}'.format(mode))

    return re.sub(
        r'(\.[a-z0-9]+") AUTOLIGHTDARK',
        r'{}\1'.format(file_suffix),
        re.sub(
            r'(<html class=")',
            r'\1{} '.format(html_class),
            code
        )
    )


def generate_light_and_dark_html_versions(src):
    basename = src.relative_to(SRCDIR)
    dst_auto = BUILDDIR / basename
    dst_dark = BUILDDIR / basename.with_name(basename.name.replace('.html', '-dark.html'))
    dst_lght = BUILDDIR / basename.with_name(basename.name.replace('.html', '-light.html'))

    source_code = src.read_text()
    dst_auto.write_text(change_html_source_code(source_code, 'auto'))
    dst_dark.write_text(change_html_source_code(source_code, 'dark'))
    dst_lght.write_text(change_html_source_code(source_code, 'light'))


def main():
    global SRCDIR, BUILDDIR
    SRCDIR = Path('.').resolve()
    BUILDDIR = Path('./build/').resolve()

    # Preparing the output directory.
    if BUILDDIR.exists():
        shutil.rmtree(BUILDDIR)
    BUILDDIR.mkdir(parents=True, exist_ok=True)

    COPY_THESE_FILES = [ 'CNAME' ]
    for file in COPY_THESE_FILES:
        shutil.copy2(SRCDIR / file, BUILDDIR / file)

    COPY_THESE_DIRS = [ 'img', 'css' ]
    for subdir in COPY_THESE_DIRS:
        shutil.copytree(SRCDIR / subdir, BUILDDIR / subdir)

    # Copying and preparing the HTML files.
    for htmlfile in SRCDIR.glob('*.html'):
        generate_light_and_dark_html_versions(htmlfile)



if __name__ == '__main__':
    main()
