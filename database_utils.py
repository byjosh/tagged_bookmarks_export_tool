from sqlite3 import connect


# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html


# following retrieves tech bookmarks tagID is 688
# title_urls_from_IDs(bookmarks_fk_set(get_results(db_cursor(db_connect()),qs["by_tag"](688))))
# tags have parent of 4 and type of 2
# retrieve id and title with get_results qs["tags"] as query

# gets tags dict
# tag_dict(get_results(db_cursor(db_connect()),qs["tags"]))

# First run iteration of program (getting used to wxPython)
# This tag_dict is used to build a checkbox list after opening file dialogue with the tag ID as the checkbox ID and the tag text as the label

# The checkbox checked event adds the tuple of tag ID and text to a object property that is a list of tuples and if only 1 checkbox is checked that opens a window with the requisite links

# the links are produced by the ID used to search for type 1 entries in moz_bookmarks where parent is the tag ID to get foreign key IDs
# title_urls_from_IDs then uses the foreign keys to get the URL and title from moz_places and checks if moz_bookmarks has a longer title for the URL to produce URLs and titles as list of tuples - this is used to make HTML of page

# Second run - need to accommodate intersection of tags - at least two. It seems better to pre-compute if which two tag combos actually produce a list of links. Storing and passing the IDs and the precomputation of the combinations that do not produce zero results are the two major changes. The title/URL tuples could be put into a set and then extracted and sorted to produce a unified list.
# Extending the Checkbox class to have a property that is a list of tags & names and appending combination tags to the a tags dict seems the straightforward was to do it. Precomputing the combinations however will likely give links so do that first to see if the results should be saved somewhere.

# Using intermediate in-memory dict instead of calls to database speeded up dual_tag_non_zero_dict function a hundredfold 23.9 down to .245 or .219 seconds

# START basic database functions
def file_path(path=[], **kw):
    """Use this to have a single location accessible from this module for the name of the current database file. TODO: check if there is a good singleton pattern to use"""
    if "filepath" in kw:
        # if already a filename in path remove it to add new one
        if len(path) == 1:
            path.pop()
        path.append(kw["filepath"])
        return path[0]
    if len(path) == 1:
        return path[0]


def db_connect():
    global pathname

    conn = connect(file_path())
    return conn


def db_cursor(conn):
    """ return a cursor """
    return conn.cursor()


def get_results(curs, query):
    """ takes a cursor returns all the results as list of tuples
    Following doc example is dependent on places.sqlite file used.
    >>> print("Following four tests depend on data in places.sqlite used for test & mostly alert you to that file or qs dictionary having changed if these fail")
    Following four tests depend on data in places.sqlite used for test & mostly alert you to that file or qs dictionary having changed if these fail

    >>> file_path(filepath='places.sqlite')
    'places.sqlite'
    >>> get_results(db_cursor(db_connect()),qs["by_tag"](8))
    [(9, 1, 8, None, 6), (11, 1, 8, None, 7), (13, 1, 8, None, 8), (19, 1, 8, None, 10)]

    >>> get_results(db_cursor(db_connect()),qs["tags"])
    [(15, 2, 4, 'book'), (8, 2, 4, 'factchecking'), (23, 2, 4, 'programming'), (26, 2, 4, 'python')]

    >>> get_results(db_cursor(db_connect()),qs["moz_places"])
    [(6, 'https://hapgood.us/2019/06/19/sift-the-four-moves/', 'SIFT (The Four Moves) – Hapgood'), (7, 'https://cor.inquirygroup.org/curriculum/lessons/intro-to-lateral-reading/', 'Intro to Lateral Reading | Civic Online Reasoning'), (8, 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994', 'Lateral Reading: Reading Less and Learning More When Evaluating Digital Information by Sam Wineburg, Sarah McGrew :: SSRN'), (9, 'https://libro.fm/audiobooks/9781508279532-good-and-mad', 'Libro.fm | Good and Mad Audiobook'), (10, 'https://uk.bookshop.org/p/books/verified-how-to-think-straight-get-duped-less-and-make-better-decisions-about-what-to-believe-online-mike-caulfield/7439531?ean=9780226822068', 'Verified: How to Think Straight, Get Duped Less, and Make Better Decisions about What to Believe Online a book by Mike Caulfield and Sam Wineburg.'), (11, 'https://leanpub.com/b/python-craftsman', 'The Python Craftsman'), (12, 'https://wiki.mozilla.org/File:Places.sqlite.schema.pdf', 'File:Places.sqlite.schema.pdf - MozillaWiki'), (13, 'https://wxpython.org/', 'Welcome to wxPython! | wxPython')]

    """
    result = curs.execute(query)
    return result.fetchall()


# END basic database functions

def places_by_tag(tagID):
    """ takes a tagID and returns all places - the foreign key is important field """
    return """SELECT id,type,parent,title,fk from moz_bookmarks WHERE parent == {} AND type == 1 ORDER BY title;""".format(
        tagID)


qs = {"tags": """SELECT id,type,parent,title from moz_bookmarks WHERE parent == 4 AND type == 2 ORDER BY title;""",
      "by_tag": places_by_tag,
      "moz_places": """SELECT id,url,title from moz_places;"""}


def print_results(results):
    """ takes results as list of tuples and prints one per line - used for debugging purposes when importing module to query db"""
    for result_tuple in results:
        print(result_tuple)


def tag_dict(results):
    """Using list of results from qs['tags'] as in get_results(db_cursor(db_connect()),qs['tags']) return a dict of {name: ID} format 
    
    >>> tag_dict([(1,'A'),(2,'B')])
    {'A': 1, 'B': 2}
    """

    tagID_location = 0
    # following does not care what is between tagID and tagName as long as it is last field in tuple
    tagName_location = -1
    return {result[tagName_location]: result[tagID_location] for result in results}


def dual_tag_dict(tag_dict):
    """Takes tag names as dict and returns a single sorted dict of all possible tag name combinations of two
    >>> dual_tag_dict({'A': 5748, 'B': 12126})
    {'A && B': (5748, 12126)}
    
    """
    tagID_location = 0
    tagName_location = -1

    def get_tagName(el):
        return el[-1]

    output_dict = {}
    results_list = [(tag_dict[tag], tag) for tag in tag_dict]
    sorted(results_list, key=get_tagName)
    for result in results_list:
        current_index = results_list.index(result)
        for remaining in results_list[current_index + 1:]:
            output_dict[f'{result[tagName_location]} && {remaining[tagName_location]}'] = (
                result[tagID_location], remaining[tagID_location])
    return output_dict


def dual_tag_non_zero_dict(dual_tag_dict):
    """ {'A & B ': (5748, 12126), } is dual tag dict input
    output dict is {'A & B': [277529], }
    """
    output_dict = {}
    intermediate_dict = {}
    for entry in dual_tag_dict:
        this_dual_tag_combo = [(dual_tag_dict[entry][0], []), (dual_tag_dict[entry][1], [])]
        for item in this_dual_tag_combo:
            tag, result = item
            if tag in intermediate_dict:
                item[1].extend(intermediate_dict[tag])
                continue
            fk_list_result = bookmarks_fk_set(get_results(db_cursor(db_connect()), qs["by_tag"](tag)))
            intermediate_dict[tag] = fk_list_result
            item[1].extend(fk_list_result)

        links_tagged_with_both_tags = set(this_dual_tag_combo[0][1]).intersection(set(this_dual_tag_combo[1][1]))
        if len(links_tagged_with_both_tags) > 0:
            output_dict[entry] = {"IDs": dual_tag_dict[entry], "links": [x for x in links_tagged_with_both_tags]}
    # print(f'with intermediate dict & continue statements using sets it took {end - start} seconds')
    # without intermediate dict using sets it took 23.129372119903564 seconds - 23129372000
    # with intermediate dict & continue statements using sets it took 0.24512314796447754 seconds - 245123000
    return output_dict


def bookmarks_fk_set(results):
    """takes results from moz_bookmarks searched with places_by_tag and returns fk fields as list for retrieval from moz_places
    
    >>> bookmarks_fk_set([(2377, 1, 2376, None, 47723), (2397, 1, 2376, None, 47852), (2593, 1, 2376, None, 50222), (2906, 1, 2376, None, 20066), (3242, 1, 2376, None, 59288), (4020, 1, 2376, None, 71910), (4339, 1, 2376, None, 76463), (6887, 1, 2376, None, 122759), (12330, 1, 2376, None, 197177), (13656, 1, 2376, None, 217901), (16359, 1, 2376, None, 264719), (16641, 1, 2376, None, 269755), (16750, 1, 2376, None, 270757), (17063, 1, 2376, None, 273252)])
    [47723, 47852, 50222, 20066, 59288, 71910, 76463, 122759, 197177, 217901, 264719, 269755, 270757, 273252]

    """
    id_list = []
    fk_location = -1  # fk should be last in tuple
    for result in results:
        if result[fk_location] not in id_list:
            id_list.append(result[fk_location])
        elif result[fk_location] in id_list:
            print(result[fk_location], " in ", result)
    return id_list


def title_urls_from_IDs(ids):
    """takes fk list from moz_bookmarks which is id in moz_places and returns a list of IDs, urls and titles as tuples"""

    def get_url(el):
        return el[1]

    output_list = []
    for id in ids:
        results = get_results(db_cursor(db_connect()),
                              """SELECT id,url,title from moz_places WHERE moz_places.id == {} ORDER BY url,title;""".format(
                                  id))
        # print("moz_places_result",results)
        if len(results) != 1:
            print("length not 1 results : ", results)
        if len(results) == 1:
            """ if results[0][-1] is not None:
                output_list.append(results[0])# if title is not blank
            elif results[0][-1] is None: """
            title = results[0][-1]
            if title is None:
                title = ""

            bookmarks_fk_result = get_results(db_cursor(db_connect()),
                                              """SELECT id,type,parent,title,fk from moz_bookmarks WHERE fk == {} AND type == 1 ORDER BY title;""".format(
                                                  results[0][0]))
            # print("moz_bookmarks_result",bookmarks_fk_result)
            for each_result in bookmarks_fk_result:
                if (each_result[-2] is not None) and len(each_result[-2]) > len(title):
                    title = each_result[-2]
            constructed_tuple = (results[0][0], results[0][1], title)
            output_list.append(constructed_tuple)
            # print("success - constructed tuple ", constructed_tuple )
            # test_result = bookmarks_fk_result[0][-2] is None
            # print("Test result", test_result)



        elif len(results) > 1 or len(results) == 0:
            print("id=", id)
            print("results:", results)

    return sorted(output_list, key=get_url)


def urls_from_tagID(id):
    """given a single id for a tag from moz_bookmarks table return the urls and IDs (via retrieval of the foreign keys)"""
    return title_urls_from_IDs(bookmarks_fk_set(get_results(db_cursor(db_connect()), qs["by_tag"](id))))


def urls_from_combinedtagname(combinedtagname, dual_tag_non_zero_dict):
    """given multiple IDs present on checkbox for a tag from moz_bookmarks table return the urls and IDs (via retrieval of the foreign keys)"""
    list_full = title_urls_from_IDs(dual_tag_non_zero_dict[combinedtagname]["links"])

    def get_url(el):
        return el[1]

    return sorted(list_full, key=get_url)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
