#!/usr/bin/env python3

import re
import shutil
from functools import reduce
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


def generate_light_and_dark_css_versions(src):
    basename = src.relative_to(SRCDIR)
    dst_auto = BUILDDIR / basename
    dst_dark = BUILDDIR / basename.with_name(basename.name.replace('.css', '-dark.css'))
    dst_lght = BUILDDIR / basename.with_name(basename.name.replace('.css', '-light.css'))

    auto = []
    lght = []
    dark = []
    vars = {'light': {}, 'dark': {}}
    processing = 'normal'
    with open(src) as f:
        for line in f:
            auto.append(line)
            # Matching the special comments that mark the light/dark variables.
            match line.replace('/*', '').replace('*/', '').strip():
                case 'START LIGHT':
                    processing = 'light'
                    continue
                case 'START DARK':
                    processing = 'dark'
                    continue
                case 'END LIGHT' | 'END DARK':
                    processing = 'normal'
                    continue
            # Processing the rest of the lines.
            match processing:
                case 'normal':
                    # We should replace the variables with their values.
                    # Why? Because (old) e-ink readers have ancient browsers that do not support CSS variables.
                    lght.append(reduce(
                        lambda s, rep: s.replace(rep[0], rep[1]),
                        vars['light'].items(),
                        line
                    ))
                    dark.append(reduce(
                        lambda s, rep: s.replace(rep[0], rep[1]),
                        vars['dark'].items(),
                        line
                    ))
                case 'light' | 'dark':
                    # If we are processing the light/dark variables, we store them.
                    if line.strip() == '':
                        continue
                    if match := re.match(r'(--[-a-zA-Z0-9]+): *([^;]+);', line.strip()):
                        vars[processing]['var({})'.format(match.group(1))] = match.group(2)

    dst_auto.write_text(''.join(auto))
    dst_dark.write_text(''.join(dark))
    dst_lght.write_text(''.join(lght))


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

    COPY_THESE_DIRS = [ 'img' ]
    for subdir in COPY_THESE_DIRS:
        shutil.copytree(SRCDIR / subdir, BUILDDIR / subdir)

    # Copying and preparing the HTML files.
    for htmlfile in SRCDIR.glob('*.html'):
        generate_light_and_dark_html_versions(htmlfile)

    # Copying and preparing the CSS files.
    (BUILDDIR / 'css').mkdir(parents=True, exist_ok=True)
    for cssfile in SRCDIR.glob('css/*.css'):
        generate_light_and_dark_css_versions(cssfile)



if __name__ == '__main__':
    main()
