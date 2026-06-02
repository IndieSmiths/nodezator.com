"""Script for generating Nodezator's static website.

https://nodezator.com
"""

### standard library imports

from pathlib import Path

from shutil import copytree, rmtree

from string import Template

from ast import literal_eval

from datetime import datetime

from warnings import warn

from functools import partial


### third-party import
from markdown import Markdown


### local import
from .processtranslations import get_translations_namespace, format_locale



### constants and module level objs

MANDATORY_PAGE_METADATA = (
    'authors',
    'description',
    'keywords',
)

MANDATORY_POST_METADATA = (
    'publish-date',
    'author-urls',
    *MANDATORY_PAGE_METADATA,
)


md = Markdown(extensions=['meta', 'extra', 'sane_lists'])

get_publish_date = lambda item: item['publish-date'][0]

### grab relevant paths

TOPDIR = Path(__file__).parent.parent

SOURCEPATH = TOPDIR / 'content'
TARGETPATH = TOPDIR / '_output'


### make sure '_output' folder exists and is empty

if TARGETPATH.is_dir():
    rmtree(str(TARGETPATH))

else:
    TARGETPATH.mkdir()

### copy images folder as-is

copytree(
    str(SOURCEPATH / 'images'),
    str(TARGETPATH / 'images'),
)

### grab and process label translations
tlns = get_translations_namespace(SOURCEPATH / '_label_translations.txt')

### grab templates

_templates_dir = SOURCEPATH / '_templates'

(

page_template,
page_header_and_nav_template,
page_footer_template,
post_template,
metadata_for_post_template,
post_item_in_index_template,
redirect_template,
comment_script_template,

) = (

    Template(

        (_templates_dir / template_filename)
        .read_text(encoding='utf-8')

    )

    for template_filename in (

        'page.html',
        'page_header_and_nav.html',
        'page_footer.html',
        'post.html',
        'metadata_for_post.html',
        'post_item_in_index_template.html',
        'post_item_in_index',
        'redirect.html',
        'giscus.html',

    )

)

### comment related module-level value
INCLUDE_COMMENT_SECTION_DEFAULT = ('False',)


def generate_site():
    """Generate en-US site and translations."""
    ### iterate over top directories, ignoring "images" and treating each
    ### additional one as a website for a specific locale;
    ###
    ### "en-us" is the only one whose files will be generated at the top
    ### of the domain (thus the default website shown); all other locales
    ### are generated in their own dedicated folders (for instance "pt-br")

    for path in SOURCEPATH.iterdir():

        if path.name.startswith('_') or path.name == 'images':
            continue

        else:
            generate_site_for_locale(path)


def generate_site_for_locale(locale_path):
    """Process contents to generate website."""

    ### reference locale dir name locally
    locale_dir_name = locale_path.name

    ### create a "lang" string to use in "lang" attributes

    _language, _sep, _country = locale_dir_name.partition('-')
    lang = _language + _sep + _country.upper()

    ### also alias the _language part for usage in the comment script
    ### (because for some reason it only works when solely the language
    ### part of the locale is given as the "lang" attribute, instead of
    ### the full locale; that is, for instance, only "en", not "en-US")
    ###
    ### so we only use that part
    comment_script_lang = _language

    ### define target path for locale

    targetpath = (

        TARGETPATH
        if locale_dir_name == 'en-us'

        else TARGETPATH / locale_dir_name

    )

    ### create it if doesn't exist already

    if not targetpath.exists():
        targetpath.mkdir()

    ### set locale for labels's translations
    tlns.__class__._locale = format_locale(locale_dir_name)

    ### get content for header and nav bar

    t = tlns.page.header_and_nav

    header_and_nav_content = (

        page_header_and_nav_template.substitute(

            {

                'header_text': t.header_text,

                'logo_alt': t.logo_alt,

                'pip_text': (

                    t
                    .pip_text
                    .format(
                        pip_command='pip install nodezator',
                        nodezator_command='nodezator'
                    )

                )

                'home': t.home,

                'home_link': '/' + (
                    ''
                    if locale_dir_name == 'en-us'
                    else f'{locale_dir_name}'
                ),

                'about': t.about,

                'about_link': '/' + (
                    ''
                    if locale_dir_name == 'en-us'
                    else f'{locale_dir_name}/'
                ) + f'{t.about_link}.html',

                'apps_and_games': t.apps_and_games,

                'apps_and_games_link': '/' + (
                    ''
                    if locale_dir_name == 'en-us'
                    else f'{locale_dir_name}/'
                ) + f'{t.apps_and_games_link}.html',

                'essays': t.essays,

                'essays_link': '/' + (
                    ''
                    if locale_dir_name == 'en-us'
                    else f'{locale_dir_name}/'
                ) + f'{t.essays_link}',

                'discord_link': '/' + (
                    ''
                    if locale_dir_name == 'en-us'
                    else f'{locale_dir_name}/'
                ) + f'discord.html',

                'donate': t.donate,

                'donate_link': '/' + (
                    ''
                    if locale_dir_name == 'en-us'
                    else f'{locale_dir_name}/'
                ) + f'{t.donate_link}.html',

                'site_search_placeholder': t.site_search_placeholder,

                'site_search_url': (

                    'indiesmiths.com' + (

                        ''
                        if locale_path.name == 'en-us'

                        else ('/' + locale_path.name)

                    )

                ),

            }

        )

    )

    ### get content for footer

    t = tlns.page.footer

    footer_content = (

        page_footer_template.substitute(

            {

                name: getattr(t, name)

                for name in (

                    'useful_links',
                    'developer',
                    'consider_supporting',
                    'more_options',
                    'present',
                    'website_source',

                )

            }

        )
    )

    ### get content for comment script

    comment_script_content = (
        comment_script_template.substitute(lang=comment_script_lang)
    )

    ### get translation node for page filenames
    filenames_node = tlns.page.filenames

    ### text for posts and post-related content

    _date_format_text = tlns.post.date_format
    year_month_day_text = tlns.post.year_month_day
    date_format_extended_text = f'{_date_format_text}: {year_month_day_text}'

    ### iterate over the website content directory generating the .html pages

    for path in locale_path.iterdir():

        ### ignore paths whose name start with '_'

        path_name = path.name

        if path_name.startswith('_'):
            continue

        ## if path is a .md file, it is a page that must be built

        elif path.suffix.lower() == '.md':

            ## grab content

            content = path.read_text(encoding='utf-8')

            html_text = md.convert(content)
            meta = md.Meta

            missing_keys = tuple(

                key
                for key in MANDATORY_PAGE_METADATA
                if key not in meta

            )

            if missing_keys:

                raise KeyError(
                    f"{path} page missing following keys: {missing_keys}"
                )

            ##

            include_comment_section = (

                literal_eval(
                    meta.get(
                        'include-comment-section',
                        INCLUDE_COMMENT_SECTION_DEFAULT,
                    )[0]
                )

            )

            ## prepare data

            page_data = {
                'lang': lang,
                'title': get_title(html_text),
                'authors': get_authors_meta(meta['authors']),
                'description': meta['description'][0],
                'keywords': ', '.join(meta['keywords']),
                'lang_keywords': tlns.page.lang_keywords,
                'header_and_nav': header_and_nav_content,
                'content': html_text,
                'comment_section': (

                    comment_script_content
                    if include_comment_section

                    else ''

                ),
                'footer': footer_content,
            }

            final_html_text = page_template.substitute(page_data)

            if path_name == 'index.md':
                filename = 'index.html'

            else:

                translation_attrname = path.stem.replace('-', '_')

                try:
                    translated_stem = (
                        getattr(filenames_node, translation_attrname)
                    )

                except AttributeError:
                    filename = path.stem + '.html'

                else:
                    filename = translated_stem + '.html' 


            destination = targetpath / filename

            ## copy the generated html content to its final destination
            destination.write_text(final_html_text, encoding='utf-8')


        ## if path is a folder, it holds .md posts rather than .html pages
        ##
        ## here we build .html pages for each .md file and a central index.html
        ## page with links to the posts

        elif path.is_dir():

            ## grab translations for specific category of post
            ## (articles/blogs/etc.)
            category_info = getattr(tlns.post.category_info, path_name)

            ## grab destination folder for posts

            posts_dest_dir = targetpath / category_info.target_folder_name
            posts_dest_dir.mkdir()

            ## grab title for pages in this category
            category_title = category_info.title

            ## build individual post pages

            posts_meta = []

            for post_path in path.iterdir():

                ###

                extension = post_path.suffix.lower()

                if extension != '.md':

                    warn(
                        f"Posts must be .md files, not {extension} files.",
                        category=RuntimeWarning,
                    )

                    continue

                ###

                translated_stem_for_post = (

                    getattr(
                        category_info.filenames,
                        post_path.stem.replace('-', '_')
                    )

                )

                post_dest_path = (
                    posts_dest_dir / f'{translated_stem_for_post}.html'
                )

                post_html = md.convert(post_path.read_text(encoding='utf-8'))
                post_meta = md.Meta

                missing_keys = tuple(

                    key
                    for key in MANDATORY_POST_METADATA
                    if key not in post_meta

                )

                if missing_keys:

                    raise KeyError(
                        f"{post_path} post missing following keys:"
                        f" {missing_keys}"
                    )

                post_title = get_title(post_html)
                post_meta['title'] = post_title

                post_image_src = get_image_src(post_html)
                post_meta['image_src'] = post_image_src

                post_image_alt = get_image_alt(post_html)
                post_meta['image_alt'] = post_image_alt

                post_meta['urlname'] = post_dest_path.name

                posts_meta.append(post_meta)

                post_description = post_meta['description'][0]

                post_html = (

                    insert_meta_into_post(
                        post_meta,
                        post_html,
                        post_description,
                        year_month_day_text,
                    )

                )

                post_data = {

                    'category_title': category_title,
                    'title': post_title,
                    'article': post_html,

                }

                final_post_text = post_template.substitute(post_data)

                include_comment_section = (

                    literal_eval(
                        post_meta.get(
                            'include-comment-section',
                            INCLUDE_COMMENT_SECTION_DEFAULT,
                        )[0]
                    )

                )

                post_page_data = {
                    'lang': lang,
                    'title': post_title,
                    'authors': get_authors_meta(post_meta['authors']),
                    'description': post_description,
                    'keywords': ', '.join(post_meta['keywords']),
                    'lang_keywords': tlns.page.lang_keywords,
                    'header_and_nav': header_and_nav_content,
                    'content': final_post_text,
                    'comment_section': (

                        comment_script_content
                        if include_comment_section

                        else ''

                    ),
                    'footer': footer_content,
                }

                ###

                final_html_content = page_template.substitute(post_page_data)
                post_dest_path.write_text(final_html_content, encoding='utf-8')

            ### build index page for posts

            t = getattr(tlns.post.category_info, path_name)

            description = t.description
            keywords = t.keywords

            posts_meta.sort(key=get_publish_date, reverse=True)

            posts_index_html = (
                f'<h1>{category_title}</h1>\n\n<p>{description}.</p>'
                f'\n\n<p>({date_format_extended_text})</p>\n\n'
                '<section class="d-flex flex-wrap">'
            )

            last_updated_text = tlns.post.metadata.last_updated_on.lower()
            read_more_text = tlns.post.read_more

            for post_meta in posts_meta:

                date_info = post_meta['publish-date'][0]

                if 'last-updated' in post_meta:

                    ldate = post_meta['last-updated'][0]
                    date_info += f' ({last_updated_text}: {ldate})'

                title = post_meta['title']
                urlname = post_meta['urlname']
                image_src = post_meta['image_src']
                image_alt = post_meta['image_alt']
                description = post_meta['description'][0]

                posts_index_html += (

                    post_item_in_index_template.substitute(
                        urlname=urlname,
                        title=title,
                        image_src=image_src,
                        image_alt=image_alt,
                        description=description,
                        date_info=date_info,
                        read_more=read_more_text,
                    )

                )

                posts_index_html += '\n'

            posts_index_html += '\n</section>'

            ## write index

            page_data = {
                'lang': lang,
                'title': category_title,
                'authors': get_authors_meta(['Kennedy Richard S. Guerra']),
                'description': description,
                'keywords': keywords,
                'lang_keywords': tlns.page.lang_keywords,
                'header_and_nav': header_and_nav_content,
                'content': posts_index_html,
                'comment_section': '',
                'footer': footer_content,
            }

            final_html_text = page_template.substitute(page_data)

            (
                posts_dest_dir
                / 'index.html'
            ).write_text(final_html_text, encoding='utf-8')


    ### grab and process redirections

    ### we don't translate stems for redirections; also, urls are used
    ### as-is; all of this means they must be ready, not needing any sort
    ### of extra processing;

    ## redirection data

    redirections_data = (
        literal_eval(
            (locale_path / '_redirections.pyl').read_text(encoding='utf-8')
        )
    )

    ## process each item

    t = tlns.redirect_page

    for key, value in redirections_data.items():

        ## prepare data

        html_content = redirect_template.substitute(
            title=t.title,
            message=t.message,
            link=value,
        )

        ## prepare/define destination

        subdirpath = targetpath / key
        subdirpath.mkdir()

        content_destination = subdirpath / 'index.html'

        ## copy the generated html content to its final destination
        content_destination.write_text(html_content, encoding='utf-8')


### helper functions

def get_title(html_text):

    return html_text[
        html_text.index('<h1>') + 4
        : html_text.index('</h1>')
    ]

def get_image_attr(attr_name, html_text):

    first_img = html_text.index('img')

    ### starting after ocurrence of '[attr_name]="' that exists after
    ### first 'img'

    length = len(attr_name) + 2 # length of attr name + '="' characters
    start = html_text.index(f'{attr_name}="', first_img) + length

    ### ending at '"' that exists after the 'start' defined previously
    end = html_text.index('"', start)

    return html_text[start:end]

get_image_src = partial(get_image_attr, 'src')
get_image_alt = partial(get_image_attr, 'alt')

def get_authors_meta(authors):

    return '\n'.join(
        f'  <meta name="author" content="{author}" />'
        for author in authors
    )

def get_comma_separated_anchors(items, urls):

    return ', '.join(

        f'<a href="{url}">{item}</a>'
        for item, url in zip(items, urls)

    )

def insert_meta_into_post(
    post_meta,
    post_html,
    post_description,
    year_month_day_text,
):

    authors = get_comma_separated_anchors(
                  post_meta['authors'],
                  post_meta['author-urls'],
              )

    created = post_meta['publish-date'][0]

    ###

    t = tlns.post.metadata

    updated_label_text = t.last_updated_on

    post_updated = (

        (
            f'<li>{updated_label_text}: '
            + post_meta['last-updated'][0]
            + '</li>'
        )
        if 'last-updated' in post_meta
        else ''
    )

    meta_content = metadata_for_post_template.substitute(

        post_description=post_description,

        written_by=t.written_by,
        post_authors=authors,

        year_month_day=year_month_day_text,

        created_on=t.created_on,
        post_created=created,

        post_updated=post_updated,

    )

    metalines = meta_content.splitlines()

    ###

    if 'translators' in post_meta:

        translated_by = tlns.translated_by

        post_translators = get_comma_separated_anchors(
                               post_meta['translators'],
                               post_meta['translator-urls'],
                           )

        metalines.insert(5, f'<li>{translated_by}: {post_translators}</li>')

    ###
    metalines.reverse()

    lines = post_html.splitlines()

    for i, line in enumerate(lines):
        if '<h1>' in line:
            break

    for line in metalines:
        lines.insert(i+1, line)

    return '\n'.join(lines)

