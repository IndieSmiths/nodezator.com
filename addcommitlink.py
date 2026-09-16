"""Automatically add link to specific commit after footer of pages.

That is, if current folder is a git project.
"""

from subprocess import check_output

from pathlib import Path

from shlex import split



GIT_COMMAND = 'git rev-parse HEAD'
GIT_COMMAND_ELEMENTS = split(GIT_COMMAND)


try:

    _full_hash = (

        check_output(GIT_COMMAND_ELEMENTS)
        .decode('ascii')
        .strip()

    )

except Exception as err:

    print("Didn't manage to retrieve hash of HEAD")
    print()
    print(err)

else:
    
    ### text to be replaced
    search_text = '<!-- hash placeholder -->'

    ### text to replace

    _hash_head = _full_hash[:7]
    _hash_tail = _full_hash[7:]

    commit_html = (
        ' (commit: <a href="https://github.com/IndieSmiths/nodezator.com/commit/'
        f'{_full_hash}">{_hash_head}</a>{_hash_tail})'
    )

    ### pages wherein to search and replace

    _output_dir = Path(__file__).parent / '_output'
    html_pages = _output_dir.glob('**/*.html')

    ### iterating over such pages performing the replacement

    for page in html_pages:

        text = page.read_text(encoding='utf-8')

        if search_text in text:

            new_text = text.replace(search_text, commit_html)
            page.write_text(new_text, encoding='utf-8')
