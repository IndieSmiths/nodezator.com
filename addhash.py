"""Automatically add commit hash after footer of pages.

That is, if current folder is a git project.
"""

from subprocess import check_output

from pathlib import Path

from shlex import split



GIT_COMMAND = 'git rev-parse HEAD'
GIT_COMMAND_ELEMENTS = split(GIT_COMMAND)


try:

    full_hash = (

        check_output(GIT_COMMAND_ELEMENTS)
        .decode('ascii')
        .strip()

    )

except Exception as err:

    print("Didn't manage to retrieve hash of HEAD")
    print()
    print(err)

else:

    hash_head = full_hash[:7]
    hash_tail = full_hash[7:]

    hash_html = f" (hash: <b>{hash_head}</b>{hash_tail})"

    output_dir = Path(__file__).parent / '_output'
    
    search_text = '<!-- hash placeholder -->'

    html_pages = output_dir.glob('**/*.html')

    for page in html_pages:

        text = page.read_text(encoding='utf-8')

        if search_text in text:

            new_text = text.replace(search_text, hash_html)
            page.write_text(new_text, encoding='utf-8')
