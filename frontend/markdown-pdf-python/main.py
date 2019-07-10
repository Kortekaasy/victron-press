import argparse
import base64
import os
from os import path

from typing import List

import jinja2
import markdown
import glob
import pdfkit

# Define input and output directories
__dirname = path.dirname(path.realpath(__file__))
inputDir = path.join(__dirname, '../../data/docs')
outputDir = path.join(__dirname, '../../data/build/pdf')

# Load in CSS and logo
pdfCSS          = "".join(open(path.join(__dirname, 'pdf.css'), 'r').readlines())
bookletCSS      = "".join(open(path.join(__dirname, 'booklet.css'), 'r').readlines())
frontpageCSS    = "".join(open(path.join(__dirname, 'frontpage.css'), 'r').readlines())
logoSVG         = open(path.join(__dirname, '../vuepress/theme/images/victron-logo.svg'), 'rb').read()

# Add fonts to CSS
MuseoSans300    = open(path.join(__dirname, '../vuepress/theme/fonts/MuseoSans/MuseoSans-300.woff'), 'rb').read()
MuseoSans700    = open(path.join(__dirname, '../vuepress/theme/fonts/MuseoSans/MuseoSans-700.woff'), 'rb').read()
pdfCSS = '''
    @font-face {
        font-family: 'Museo Sans';
        src: url('data:font/woff;base64,%s') format('woff');
        font-weight: 300;
    }
    @font-face {
        font-family: 'Museo Sans';
        src: url('data:font/woff;base64,%s') format('woff');
        font-weight: 700;
    }
    %s
''' % (str(base64.b64encode(MuseoSans300), 'utf-8'), str(base64.b64encode(MuseoSans700), 'utf-8'), pdfCSS)

# Logic
def readFile(path: str):
    return "".join(open(path, 'r').readlines())

def getFilePaths(files: List[str]):
    from os import path 

    # glob all files
    result = glob.glob(path.join(inputDir, '**/*.md'), recursive=True)

    # remove redundant part of path
    result = map(lambda x: x[len(inputDir) + 1:], result)

    # Filter out the README.md file
    result = filter(lambda x: 'README.md' not in x, result)

    # Only return files matching to `files` whitelist, if they exist
    if len(files) > 0:
        result = filter(lambda x: x in files, result)
    
    # Return evaluated list
    return list(result)


def generate_body(md_content: str):
    """
    Generate HTML from a markdown file
    """
    global path

    md = markdown.Markdown(extensions=[
        'abbr',
        'footnotes', 
        'toc', 
        'meta', 
        'tables',
        # 'markdown_markup_emoji.markup_emoji',
        # 'mdx_linkify'
    ])
    html = md.convert(md_content)
    return md.Meta, html


def generate_HTML_page(frontmatter, body: str):
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{inferredTitle}}</title>
        <style>{{css}}</style>
    </head>
        <body>{{html}}</body>
    </html>
    """
    # doc = jinja2.Template(template).render(inferredTitle=meta['title'][0], css=pdfCSS, html=body)
    doc = jinja2.Template(template).render(inferredTitle='title', css=pdfCSS, html=body)
    return doc


def generate_HTML_header():
    global path

    template = """
    <!DOCTYPE html>
    <html>
        <head>
            <style>{{css}}</style>
        </head>
        <body>
            <header>
                <img src="{{link}}" class="logo">
            </header>
        </body>
    </html>
    """
    #<img src="data:image/svg+xml;base64,{{logo}}" class="logo" />
    doc = jinja2.Template(template).render(
        css=pdfCSS, 
        link='./victron-logo.png'
        # logo=str(base64.b64encode(logoSVG), 'utf-8')
    )
    open(path.join(__dirname, 'header.html'), 'w').write(doc)


def generate_PDF(frontmatter, body: str, output_path: str):
    global path

    template = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>{{inferredTitle}}</title>
            <style>{{css}}</style>
        </head>
        <body>
            <div class="page-break">
                {{html}}
            </div>
        </body>
    </html>
    """
    doc = jinja2.Template(template).render(
        inferredTitle='title', 
        css=pdfCSS, 
        html=body)

    pdfkit.from_string(doc, output_path, options={
        'page-size': 'A4',
        'margin-top': '25mm',
        'margin-right': '10mm',
        'margin-bottom': '25mm',
        'margin-left': '10mm',
        '--header-html': path.join(__dirname, 'header.html'),
        '--header-spacing': 8,
        '--footer-spacing': 5,
        '--footer-center': '[page] / [topage]',
        '--footer-font-size': 9,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Markdown files to HTML')
    parser.add_argument('files', metavar='file', nargs='*', help='file to parse (default is all files)')
    args = parser.parse_args()

    files = getFilePaths(args.files)
    for f in files:
        meta, body = generate_body(readFile(path.join(inputDir, f)))
        page = generate_HTML_page(meta, body)
        generate_HTML_header()
        generate_PDF(meta, body, path.join(outputDir, f.replace('.md', '.pdf')))
