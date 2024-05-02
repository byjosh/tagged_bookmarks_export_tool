# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
import sqlite3


# START basic database functions
def specify_file_path(path=[], **kw):
    """Use this to have a single location accessible from this module for the name of the current database file. TODO: check if there is a good singleton pattern to use"""
    import os.path
    if "file_path" in kw and os.path.exists(kw["file_path"]) is True and os.path.isfile(kw["file_path"]) is True:
        # if already a filename in path remove it to add new one
        if len(path) == 1:
            path.pop()
        path.append(kw["file_path"])
        return path[0]
    elif "file_path" in kw and (os.path.exists(kw["file_path"]) is False or os.path.isfile(kw["file_path"]) is False):
        print("That was not a valid file you selected - about to return the previous file")
    if len(path) == 1:
        return path[0]


def db_connect():
    global pathname
    conn = sqlite3.connect(specify_file_path())
    return conn


def db_cursor(conn):
    """ return a cursor - deprecated for with use of db_connect().execute().fetchall() allowing for prepared statements """
    return conn.cursor()


def get_results(curs, query):
    """ takes a cursor returns all the results as list of tuples
    Following doc example is dependent on places.sqlite file used.
    >>> print("Following four tests depend on data in places.sqlite used for test & mostly alert you to that file or qs dictionary having changed if these fail")
    Following four tests depend on data in places.sqlite used for test & mostly alert you to that file or qs dictionary having changed if these fail

    >>> specify_file_path(file_path='places.sqlite')
    'places.sqlite'





    [(6, 'https://hapgood.us/2019/06/19/sift-the-four-moves/', 'SIFT (The Four Moves) – Hapgood'), (7, 'https://cor.inquirygroup.org/curriculum/lessons/intro-to-lateral-reading/', 'Intro to Lateral Reading | Civic Online Reasoning'), (8, 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994', 'Lateral Reading: Reading Less and Learning More When Evaluating Digital Information by Sam Wineburg, Sarah McGrew :: SSRN'), (9, 'https://libro.fm/audiobooks/9781508279532-good-and-mad', 'Libro.fm | Good and Mad Audiobook'), (10, 'https://uk.bookshop.org/p/books/verified-how-to-think-straight-get-duped-less-and-make-better-decisions-about-what-to-believe-online-mike-caulfield/7439531?ean=9780226822068', 'Verified: How to Think Straight, Get Duped Less, and Make Better Decisions about What to Believe Online a book by Mike Caulfield and Sam Wineburg.'), (11, 'https://leanpub.com/b/python-craftsman', 'The Python Craftsman'), (12, 'https://wiki.mozilla.org/File:Places.sqlite.schema.pdf', 'File:Places.sqlite.schema.pdf - MozillaWiki'), (13, 'https://wxpython.org/', 'Welcome to wxPython! | wxPython')]

    """
    result = curs.execute(query)
    return result.fetchall()


# END basic database functions

def places_by_tag(tagID):
    """ takes a tagID and returns all links with that tag i.e. parent field - the foreign key is important field """
    return db_connect().execute(
        """SELECT id,type,parent,title,fk from moz_bookmarks WHERE parent == ? AND type == 1 ORDER BY title;""",
        (tagID,)).fetchall()


def get_tags(conn):
    return conn.execute(
        """SELECT id,type,parent,title from moz_bookmarks WHERE parent == 4 AND type == 2 ORDER BY title""").fetchall()


def is_bookmarks_file() -> bool:
    """Checks if two key tables are present moz_places and moz_bookmarks returns True if so else False
    Used for file processing logic in main app"""
    try:
        result = get_database_table_names()
        return ('moz_places',) in result and ('moz_bookmarks',) in result
    except (sqlite3.DatabaseError, NameError) as error:
        # print(error)
        return False


def print_results(results):
    """ takes results as list of tuples and prints one per line - used for debugging purposes when importing module to query db"""
    for result_tuple in results:
        print(result_tuple)


def tag_dict(results):
    """Using list of results from get_tags() return a dict of {name: ID} format
    
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

    :param tag_dict: dictionary of tag IDs indexed by tag name
    :type tag_dict: dict
    :return: dictionary of
    :rtype:
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
    """tag combinations that have overlap - i.e. non_zero_result
    {'A & B ': (5748, 12126), } is dual tag dict input
    output dict is {'A & B': [277529], }



    :param dual_tag_dict: a dictionary indexed by the addition of tagnames, 'tagA & tagB' containing tuple of IDs (tagA_ID,tagB_ID)
    :type dual_tag_dict: dict
    :return: dictionary of links referenced by both tags (i.e. set intersection)
    :rtype: dict
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
            fk_list_result = bookmarks_fk_set(places_by_tag(tag))
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

    :param results: list of tuples retrieved from moz_bookmarks with places_by_tag
    :type results: list
    :return: list of foreign keys
    :rtype: list
    """
    id_list = []
    fk_location = -1  # fk should be last in tuple
    for result in results:
        if result[fk_location] not in id_list:
            id_list.append(result[fk_location])
        elif result[fk_location] in id_list:
            print(result[fk_location], " in ", result)
    return id_list


def get_database_table_names():
    """returns table names from sqlite_schema table
    Troubleshooting function - used for developing table queries when this file is imported

    :return: names as tuples in a list
    :rtype: list
    """
    return db_connect().execute("SELECT name from sqlite_schema WHERE type='table';").fetchall()


def get_table_schema(table_name):
    """returns column info for given table name
    Troubleshooting function - used for developing table queries when this file is imported

    :param table_name: name of table
    :type table_name: str
    :return: schema as list of tuples detailing field details
    :rtype: list
    """
    # allow tables names that are alphanumeric or with underscores or dashes
    sanitised_name = "".join([a for a in table_name if a.isalnum() or a in [c for c in "_-"]])
    try:
        if db_connect().execute('SELECT 1 FROM sqlite_master WHERE type="table" and name= ?;',
                                (sanitised_name,)).fetchall() is not None:
            # OK table exists as is - so use table name
            return get_results(db_cursor(db_connect()), f"PRAGMA table_info({sanitised_name});")
    finally:
        print("Finally happened - an error?")


def get_description_via_url(url):
    """given URL fetch description
    Not currently in use
    """
    return db_connect().execute("SELECT description from moz_places where url = ? ;",(url,)).fetchall()


def title_urls_from_IDs(ids):
    """takes fk list from moz_bookmarks which is id in moz_places and returns a list of urls and titles as tuples

    :param ids: list of foreign key ids from moz_bookmarks which are IDs in moz_places
    :type ids: list
    :return: list of tuples of urls and titles
    :rtype: list
    """
    def get_url(el):
        return el[1]

    output_list = []
    for id in ids:
        results = db_connect().execute("""SELECT id,url,title from moz_places WHERE moz_places.id == ? ORDER BY url,title;""",(
                                  id,)).fetchall()
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

            bookmarks_fk_result = db_connect().execute("""SELECT id,type,parent,title,fk from moz_bookmarks WHERE fk == ? AND type == 1 ORDER BY title;""",(
                                                  results[0][0],)).fetchall()
            # print("moz_bookmarks_result",bookmarks_fk_result)
            for each_result in bookmarks_fk_result:
                if (each_result[-2] is not None) and len(each_result[-2]) > len(title):
                    title = each_result[-2]
            constructed_tuple = (results[0][0],results[0][1], title)
            output_list.append(constructed_tuple)
            # print("success - constructed tuple ", constructed_tuple )
            # test_result = bookmarks_fk_result[0][-2] is None
            # print("Test result", test_result)



        elif len(results) > 1 or len(results) == 0:
            print("id=", id)
            print("results:", results)

    return sorted(output_list, key=get_url)


def urls_from_tagID(id):
    """given a single id for a tag from moz_bookmarks table return the urls and titles (via retrieval of the foreign keys)"""
    return title_urls_from_IDs(bookmarks_fk_set(places_by_tag(id)))


def urls_from_combinedtagname(combinedtagname, dual_tag_non_zero_dict):
    """given multiple IDs present on checkbox for a tag from moz_bookmarks table return the urls and IDs (via retrieval of the foreign keys)"""
    list_full = title_urls_from_IDs(dual_tag_non_zero_dict[combinedtagname]["links"])

    def get_url(el):
        return el[1]

    return sorted(list_full, key=get_url)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
