"""Facility for loading and distributing translated text."""

### standard library imports

from collections import deque

from itertools import takewhile



### module level helper
is_space = lambda c: c == ' '


### function to create translation namespace

def get_translations_namespace(filepath):
    """Load translated texts, gather them in namespace and return it."""

    ptm = {} # parent tracking map
    lines_deque = deque()

    ###

    path = filepath

    tln = TranslationNode()

    ptm.clear()

    # parent of node of level 0 have the sheet as their parent node
    ptm[0] = tln

    ### grab lines
    lines = path.read_text(encoding='utf-8').splitlines()

    ### store lines in a deque

    lines_deque.extend(lines)

    identifier_to_be_registered = ''

    watch_out_for_translations = False

    previous_level = 0

    for line in lines:

        ###
        lines_deque.popleft()
        ###

        stripped_line = line.strip()

        ### empty lines or lines starting with '#' are ignored

        if (
            not stripped_line
            or stripped_line[0] == '#'
        ):
            continue

        ### determine current level based on number of spaces
        ### 0 spaces == level 1
        ### 4 spaces == level 2
        ### 8 spaces == level 3
        ### and so on

        spaces = ''.join(takewhile(is_space, line))

        no_of_spaces = len(spaces)

        current_level = (no_of_spaces // 4) + 1

        ###
        remaining_text = line[no_of_spaces:]

        ###

        if current_level < previous_level:
            watch_out_for_translations = False

        ### if we are dealing with translations, simply
        ### store the translation in the parent object
        ### using the locale code as the attribute name

        if watch_out_for_translations:

            _locale, _, translation = remaining_text.partition(' ')

            # get formatted locale
            formatted_locale = format_locale(_locale)

            # store translation in parent's translation map

            parent = ptm[current_level-2]

            tmap = (
                parent._translation_map
                [identifier_to_be_registered]
            )

            tmap[formatted_locale] = translation

        else:

            identifier_to_be_registered = ''

            # peek into next lines to see if we are dealing
            # with translations or identifiers
            #
            # if dealing with translations, we use the leaf
            # class, otherwise we use the node class

            for deque_line in lines_deque:

                stripped_deque_line = deque_line.strip()

                if (
                    not stripped_deque_line
                    or stripped_deque_line[0] == '#'
                ):
                    continue

                if ' ' in stripped_deque_line:
                    watch_out_for_translations = True

                break

            parent = ptm[current_level-1]

            if watch_out_for_translations:

                if not parent._has_translation_map:

                    parent._translation_map = {}
                    parent._has_translation_map = True

                parent._translation_map[remaining_text] = {}
                identifier_to_be_registered = remaining_text

            else:

                # instantiate and store object in parent's attribute

                node = TranslationNode()
                setattr(parent, remaining_text, node)

                # store it as a parent obj
                ptm[current_level] = node

        ### mark current level as the previous level
        previous_level = current_level

    ### clear the lines deque
    lines_deque.clear()

    ### clear the helper map
    ptm.clear()

    ### return namespace
    return tln


### helper class;
###
### simple class that falls back to en_us translation
### when another locale fails when retrieved

class TranslationNode():

    # placeholder class attribute
    _locale = None

    def __init__(self):
        self._has_translation_map = False

    def __getattr__(self, attr_name):

        if (
            not self._has_translation_map
            or attr_name not in self._translation_map
        ):

            raise AttributeError(
                f"TranslationNode obj doesn't have '{attr_name}' attribute."
            )

        return (
            self._translation_map[attr_name]
            .get(self._locale, 'en_us')
        )

### helper function

def format_locale(locale):

    return (
        locale
        .lower()           # ensure lowercase
        .replace('-', '_') # ensure '-' is replaced with '_'
    )
