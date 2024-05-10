# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
import sqlite3
import sys
import os
from datetime import datetime

"""import logging

logging.basicConfig(level=logging.DEBUG)
log_database = logging.getLogger(name="database_utils DATABASE")
log_general = logging.getLogger(name="database_utils GENERAL")
log_database.setLevel(logging.ERROR)
log_general.setLevel(logging.ERROR)

Use find and replace in IDE to uncomment # from log_general and log_database
with commented out logging calls it cuts time in half 1.25 seconds
DEBUG:tbet MAIN:star: 39.776178
DEBUG:tbet MAIN:end:  41.030925
compared with the logging calls present by log level set so as not to show anything 2.47 seconds
DEBUG:tbet MAIN:star: 2.370496
DEBUG:tbet MAIN:end:  4.8413792"""


class db_util:
    # START basic database functions
    def __init__(self, file_path):
        """Init the instance with a file path to the database
        :param file_path: path to the sqlite database file
        :type file_path: str
        """
        self.file_path = None
        if file_path is None:
            return
        if os.path.exists(file_path) is True and os.path.isfile(file_path) is True:
            self.file_path = file_path

        else:
            print("Not a valid file selected - try another using specify_file_path(file_path='new_file_path')")

    def specify_file_path(self, path=[], **kw):
        """Use this to reset the instance variable for the file path"""
        import os.path
        if self.file_path is not None and os.path.exists(self.file_path):
            return self.file_path
        if "file_path" in kw and os.path.exists(kw["file_path"]) is True and os.path.isfile(kw["file_path"]) is True:
            # if already a filename in path remove it to add new one
            self.file_path = kw["file_path"]
            return self.file_path
        elif "file_path" in kw and (
                os.path.exists(kw["file_path"]) is False or os.path.isfile(kw["file_path"]) is False):
            print("That was not a valid file you selected - about to return the previous file")

    def db_connect(self):
        global pathname
        conn = sqlite3.connect(self.specify_file_path())
        return conn

    def db_cursor(self, conn):
        """ return a cursor - deprecated for with use of db_connect().execute().fetchall() allowing for prepared statements """
        return conn.cursor()

    def get_results(self, curs, query):
        """ takes a cursor returns all the results as list of tuples
        Following doc example is dependent on places.sqlite file used.
        >>> print("Following four tests depend on data in places.sqlite used for test & mostly alert you to that file or qs dictionary having changed if these fail")
        Following four tests depend on data in places.sqlite used for test & mostly alert you to that file or qs dictionary having changed if these fail

        >>> self.specify_file_path(file_path='places.sqlite')
        'places.sqlite'





        [(6, 'https://hapgood.us/2019/06/19/sift-the-four-moves/', 'SIFT (The Four Moves) – Hapgood'), (7, 'https://cor.inquirygroup.org/curriculum/lessons/intro-to-lateral-reading/', 'Intro to Lateral Reading | Civic Online Reasoning'), (8, 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994', 'Lateral Reading: Reading Less and Learning More When Evaluating Digital Information by Sam Wineburg, Sarah McGrew :: SSRN'), (9, 'https://libro.fm/audiobooks/9781508279532-good-and-mad', 'Libro.fm | Good and Mad Audiobook'), (10, 'https://uk.bookshop.org/p/books/verified-how-to-think-straight-get-duped-less-and-make-better-decisions-about-what-to-believe-online-mike-caulfield/7439531?ean=9780226822068', 'Verified: How to Think Straight, Get Duped Less, and Make Better Decisions about What to Believe Online a book by Mike Caulfield and Sam Wineburg.'), (11, 'https://leanpub.com/b/python-craftsman', 'The Python Craftsman'), (12, 'https://wiki.mozilla.org/File:Places.sqlite.schema.pdf', 'File:Places.sqlite.schema.pdf - MozillaWiki'), (13, 'https://wxpython.org/', 'Welcome to wxPython! | wxPython')]

        """
        result = curs.execute(query)
        return result.fetchall()

    # END basic database functions

    def places_by_tag(self, tagID):
        """ takes a tagID and returns all links with that tag i.e. parent field - the foreign key is important field """
        # old db_query
        db_query = """SELECT id,type,parent,dateAdded, title,fk from moz_bookmarks WHERE parent == ? AND type == 1 ORDER BY title;"""
        # Following select statement - will only select those where there is a title - so have to later retrieve timestamp & title
        # db_query = "SELECT b2.dateAdded, b2.title, b1.fk from moz_bookmarks AS b1, moz_bookmarks as b2 WHERE b1.parent == ? AND b2.parent == 3 AND b1.fk == b2.fk"
        # log_database.debug(f'Database call in function { sys._getframe(  ).f_code.co_name }')
        # log_database.debug(f'Database query was: {db_query}')
        results = self.db_connect().execute(db_query, (tagID,)).fetchall()
        # log_database.debug(f'{ sys._getframe(  ).f_code.co_name } results are { results}')
        return results

    def get_tags(self):
        db_query = """SELECT id,type,parent,title from moz_bookmarks WHERE parent == 4 AND type == 2 ORDER BY title"""
        # log_database.debug(f'Database call in function {sys._getframe().f_code.co_name}')
        # log_database.debug(f'Database query was: {db_query}')
        return self.db_connect().execute(db_query).fetchall()

    def is_bookmarks_file(self) -> bool:
        """Checks if two key tables are present moz_places and moz_bookmarks returns True if so else False
        Used for file processing logic in main app"""
        try:
            result = self.get_database_table_names()
            # log_general.debug(f"Retrieved tables names as follows:-{self.specify_file_path(),result} - which should be a result")
            return ('moz_places',) in result and ('moz_bookmarks',) in result
        except (sqlite3.DatabaseError, NameError) as error:
            print("There has been an error:- ", error)
            return False

    def print_results(self, results):
        """ takes results as list of tuples and prints one per line - used for debugging purposes when importing module to query db"""
        for result_tuple in results:
            print(result_tuple)

    def get_tag_dict(self, results):
        """Using list of results from get_tags() return a dict of {name: ID} format

        >>> self.get_tag_dict([(1,'A'),(2,'B')])
        {'A': 1, 'B': 2}
        """

        tagID_location = 0
        # following does not care what is between tagID and tagName as long as it is last field in tuple
        tagName_location = -1
        return {result[tagName_location]: result[tagID_location] for result in results}

    def get_dual_tag_dict(self, tag_dict):
        """Takes tag names as dict and returns a single sorted dict of all possible tag name combinations of two
        >>> self.get_dual_tag_dict({'A': 5748, 'B': 12126})
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

    def dual_tag_non_zero_dict(self, double_tag_dict):
        """tag combinations that have overlap - i.e. non_zero_result
        {'A & B ': (5748, 12126), } is dual tag dict input
        output dict is {'A & B': [277529], }
        >>> self.specify_file_path(file_path="places.sqlite")
        'places.sqlite'
        >>> len(self.dual_tag_non_zero_dict(self.get_dual_tag_dict(self.get_tag_dict(self.get_tags())))) == 4
        True



        :param double_tag_dict: a dictionary indexed by the addition of tagnames, 'tagA & tagB' containing tuple of IDs (tagA_ID,tagB_ID)
        :type double_tag_dict: dict
        :return: dictionary of links referenced by both tags (i.e. set intersection)
        :rtype: dict
        """
        output_dict = {}
        intermediate_dict = {}
        for entry in double_tag_dict:
            first_tag = double_tag_dict[entry][0]
            second_tag = double_tag_dict[entry][1]
            this_dual_tag_combo = [(first_tag, []), (second_tag, [])]
            for item in this_dual_tag_combo:
                tag, result = item
                if tag in intermediate_dict:
                    # extend the list of tag_ids in list
                    item[1].extend(intermediate_dict[tag])
                    continue
                fk_list_result = list(self.bookmarks_fk_dict(self.places_by_tag(tag)))
                intermediate_dict[tag] = fk_list_result
                item[1].extend(fk_list_result)

            links_tagged_with_both_tags = set(this_dual_tag_combo[0][1]).intersection(set(this_dual_tag_combo[1][1]))
            if len(links_tagged_with_both_tags) > 0:
                output_dict[entry] = {"IDs": double_tag_dict[entry], "links": [x for x in links_tagged_with_both_tags]}
        # print(f'with intermediate dict & continue statements using sets it took {end - start} seconds')
        # without intermediate dict using sets it took 23.129372119903564 seconds - 23129372000
        # with intermediate dict & continue statements using sets it took 0.24512314796447754 seconds - 245123000
        return output_dict

    def bookmarks_fk_dict(self, results):
        """takes results from moz_bookmarks searched with places_by_tag
        and returns dict indexed by fk fields for retrieval from moz_places
        >>> self.bookmarks_fk_dict([(16, 1, 15, 1714075546194000, None, 9), (18, 1, 15, 1714075583047000, None, 10), (21, 1, 15, 1714075691336000, None, 11)])
        [9, 10, 11]

        :param results: list of tuples retrieved from moz_bookmarks with places_by_tag
        :type results: list
        :return: dict indexed by foreign key
        :rtype: list
        """
        bookmarks_by_fk = []
        fk_location = -1  # fk should be last in tuple
        # log_database.debug(f' {sys._getframe().f_code.co_name} results {results} END results {sys._getframe().f_code.co_name} ENDED')
        for result in results:
            # log_database.debug(f' {sys._getframe().f_code.co_name} result (singular) {result} END result (singular) {sys._getframe().f_code.co_name} ENDED')
            if result[fk_location] not in bookmarks_by_fk:
                bookmarks_by_fk.append(result[fk_location])
            elif result in bookmarks_by_fk:
                print(result, " in ", results, " was seen in bookmarks_by_fk ", bookmarks_by_fk)
        return bookmarks_by_fk

    def get_database_table_names(self):
        """returns table names from sqlite_schema table
        Troubleshooting function - used for developing table queries when this file is imported

        :return: names as tuples in a list
        :rtype: list
        """
        db_query = "SELECT name from sqlite_schema WHERE type='table';"
        # log_database.debug(f'Database call in function {sys._getframe().f_code.co_name}')
        # log_database.debug(f'Database query was: {db_query}')
        return self.db_connect().execute(db_query).fetchall()

    def get_table_schema(self, table_name):
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
            db_query = 'SELECT 1 FROM sqlite_master WHERE type="table" and name= ?;'
            # log_database.debug(f'Database call in function {sys._getframe().f_code.co_name}')
            # log_database.debug(f'Database query was: {db_query}')
            if self.db_connect().execute(db_query, (sanitised_name,)).fetchall() is not None:
                # OK table exists as is - so use table name
                return self.get_results(self.db_cursor(db_connect()), f"PRAGMA table_info({sanitised_name});")
        finally:
            print("Finally happened - an error?")

    def get_description_via_fk(self, fk):
        """given URL fetch description
        Not currently in use
        """
        db_query = "SELECT description from moz_places where id = ? ;"
        # log_database.debug(f'Database call in function {sys._getframe().f_code.co_name}')
        # log_database.debug(f'Database query was: {db_query}')
        return self.db_connect().execute(db_query, (fk,)).fetchall()[0][0]

    """
    date.fromtimestamp(timeone[0]/1000000)
    datetime.date(2024, 4, 25)
    
    """

    def title_urls_from_IDs(self, ids):
        """takes fk list from moz_bookmarks which is id in moz_places and returns a list of urls and titles as tuples

        :param ids: list of foreign key ids from moz_bookmarks which are IDs in moz_places
        :type ids: list
        :return: list of tuples of urls and titles
        :rtype: list
        """

        def get_url(el):
            return el[1]

        output_list = []
        # log_database.debug(f'This is the ids {ids} END ids  {sys._getframe().f_code.co_name} ENDED')
        for id in ids:
            db_query = """SELECT id,url,description,title from moz_places WHERE moz_places.id == ? ORDER BY url,title;"""
            # log_database.debug(f'Database call in function {sys._getframe().f_code.co_name}')
            # log_database.debug(f'Database query was: {db_query}')
            results = self.db_connect().execute(db_query, (
                id,)).fetchall()
            # print("moz_places_result",results)
            if len(results) != 1:
                # log_general.info(f"length not 1 - results : {results}")
                print(f"length not 1 - results : {results}")
            if len(results) == 1:
                """ if results[0][-1] is not None:
                    output_list.append(results[0])# if title is not blank
                elif results[0][-1] is None: """
                title = results[0][-1]
                url = results[0][1]
                description = results[0][2]
                if title is None:
                    title = ""

                """in places_by_tag we are looking for entries with a parent of the tagID (of which there are multiple entries so UNION does not work - but ones with title have parent of 3 AND using a fancy join selects only where the title is changed - following line does do replacements that are necessary - particularly expanded links"""
                db_query = """SELECT id,type,parent,dateAdded, title,fk from moz_bookmarks WHERE fk == ? AND type == 1 ORDER BY title;"""
                # log_database.debug(f'Database call in function {sys._getframe().f_code.co_name}')
                # log_database.debug(f'Database query was: {db_query}')
                bookmarks_fk_result = self.db_connect().execute(db_query, (results[0][0],)).fetchall()

                # log_database.debug(f"moz_bookmarks_result {bookmarks_fk_result}")
                for each_result in bookmarks_fk_result:
                    if (each_result[-2] is not None) and len(each_result[-2]) > len(title):
                        # log_general.info(f'OLD title of : { title } style replaced a title with {each_result[-2]} \n')
                        title = each_result[-2]

                timestamp = str(datetime.fromtimestamp(bookmarks_fk_result[0][-3]/1000000))
                constructed_tuple = (results[0][0], url, timestamp, description, title)
                output_list.append(constructed_tuple)
                # log_general.debug(f"success - constructed tuple {constructed_tuple}, output_list {output_list}" )
                # test_result = bookmarks_fk_result[0][-2] is None
                # print("Test result", test_result)



            elif len(results) > 1 or len(results) == 0:
                print("id=", id)
                print("results:", results)

        return sorted(output_list, key=get_url)

    def urls_from_tagID(self, id):
        """given a single id for a tag from moz_bookmarks table return the urls and titles (via retrieval of the foreign keys)"""
        result = self.title_urls_from_IDs(self.bookmarks_fk_dict(self.places_by_tag(id)))
        # log_general.debug(f' {sys._getframe().f_code.co_name} result is {result}')
        return result

    def urls_from_combinedtagname(self, combinedtagname, dual_tag_non_zero_dict):
        """given multiple IDs present on checkbox for a tag from moz_bookmarks table return the urls and IDs (via retrieval of the foreign keys)"""

        def get_url(el):
            return el[1]

        list_full = self.title_urls_from_IDs(dual_tag_non_zero_dict[combinedtagname]["links"])
        result = sorted(list_full, key=get_url)
        # log_general.debug(f' {sys._getframe().f_code.co_name} result is {result}')
        return result


if __name__ == "__main__":
    import doctest

    doctest.testmod(extraglobs={"self": db_util('places.sqlite')})
