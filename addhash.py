"""Automatically add commit hash after footer of pages.

That is, if current folder is a git project.
"""

from subprocess import check_output

from pathlib import Path


try:
    full_hash = check_output('git rev-parse HEAD'.split()).decode('ascii').strip()

except Exception as err:

    print("Didn't manage to retrieve hash of HEAD")
    print()
    print(err)

else:

    hash_head = full_hash[:7]
    hash_tail = full_hash[7:]

    hash_html = f"hash: <b>{hash_head}</b>{hash_tail}"

    output_dir = Path(__file__).parent / '_output'

    html_pages = output_dir.glob('**/*.html')
    
    search_text = 'source</a>'

    for page in html_pages:

        text = page.read_text(encoding='utf-8')

        try:
            index = text.rindex(search_text)

        except ValueError:
            continue

        else:

            new_text = text.replace(search_text, f'{search_text} ({hash_html})')
            page.write_text(new_text, encoding='utf-8')
