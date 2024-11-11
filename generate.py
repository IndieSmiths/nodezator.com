"""Script for generating Nodezator's static website.

https://nodezator.com
"""

### standard library imports

from pathlib import Path

from shutil import copytree, rmtree

from string import Template

from collections import deque

from operator import truediv

from functools import reduce

from ast import literal_eval




### grab relevant paths

HERE = Path(__file__).parent
sourcepath = HERE / 'content'
targetpath = HERE / 'output'


### make sure 'output' folder exists and is empty

if targetpath.is_dir():
    rmtree(str(targetpath))

else:
    targetpath.mkdir()

### copy images folder as-is
copytree(str(sourcepath / 'images'), str(targetpath / 'images'))

### grab templates

templates_dir = sourcepath / '_templates'
page_template = Template((templates_dir / 'page.html').read_text(encoding='utf-8'))
redirect_template = Template((templates_dir / 'redirect.html').read_text(encoding='utf-8'))


### grab default values

with open(str(sourcepath / '_defaults.pyl'), mode='r', encoding='utf-8') as f:
    defaults = literal_eval(f.read())

### create a deque
dirnames = deque()


### grab website content data (pages, posts, etc.)

with open(str(sourcepath / '_site.pyl'), mode='r', encoding='utf-8') as f:
    data = literal_eval(f.read())


### iterate over the website content data generating the .html pages

for key, value in data.items():

    ## if key is a string which ends with '.html', it refers to html content
    ## that must be built; in this case, the value is expected to be a dict
    ## with extra data about the page

    if key.endswith('.html'):

        ## grab content

        parts = Path(key).parts

        content_source = reduce(truediv, parts, sourcepath)

        with open(str(content_source), mode='r', encoding='utf-8') as f:
            value['content'] = f.read()

        ## ensure directories exist on target path

        dirnames.clear()

        parent = content_source.parent

        while True:

            if parent != sourcepath:
                dirnames.appendleft(parent.name)

            else:
                break

            parent = parent.parent


        current = targetpath

        for dirname in dirnames:

            current = current / dirname

            if not current.exists():
                current.mkdir()

        ## prepare data

        page_data = defaults.copy()
        page_data.update(value)


        html_content = page_template.substitute(page_data)

        ## define destination
        content_destination = reduce(truediv, Path(key).parts, targetpath)

    ## otherwise, if value is a string, treat is as an URL for redirection

    elif isinstance(value, str):

        ## prepare data
        html_content = redirect_template.substitute(link=value)

        ## prepare/define destination

        subdirpath = targetpath / key
        subdirpath.mkdir()

        content_destination = subdirpath / 'index.html'

    ## copy the generated html content to its final destination
    content_destination.write_text(html_content, encoding='utf-8')

