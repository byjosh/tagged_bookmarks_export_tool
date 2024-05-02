# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
import html


def html_with_plain_url(url, title):
    return f'<p><a href="{html.escape(url)}">{html.escape(title)}</a>, {html.escape(url)}</p>'


def html_only(url, title):
    return f'<p><a href="{html.escape(url)}">{html.escape(title)}</a></p>'


def html_csv(url, title):
    return f'<br />{html.escape(url)},"{html.escape(title)}"'


def csv_only(urls_titles, filepath):
    import csv
    with open(filepath, mode="w") as file:
        csv.writer(file, dialect='excel', quoting=csv.QUOTE_ALL).writerows(urls_titles)


export_format_choices = {"HTML links": html_only, "HTML links + plaintext URL": html_with_plain_url,
                         "HTML file that could be copied to text editor for CSV": html_csv,
                         "CSV - save to CSV file (no preview)": csv_only}
instructional_text = f'<p>Click links to open in browser or perform action.</p><p>Selecting with mouse then Ctrl+C (or Cmd+C) in this window copies only plain text.<br />To paste HTML text with clickable links <a href="#">save as HTML file</a> then copy/paste from browser <br />or <a href="##">copy all text below inc. any links to clipboard as HTML</a></p><br />'

def make_list_source_from_urls_titles(urls_titles, processing_function=export_format_choices["HTML links + plaintext URL"]):
    '''Take a list of tuples from titles_urls_from_IDs
    
    >>> make_list_source_from_urls_titles([("https://www.example.com","Example.com Homepage"),("http://example.com","Example.com domain")])
    '<section id="links"><p><a href="https://www.example.com">Example.com Homepage</a>, https://www.example.com</p><p><a href="http://example.com">Example.com domain</a>, http://example.com</p></section>'
    
    '''

    fragment = '<section id="links">'
    id_position = 0
    url_position = 1
    title_position = 2
    for url_title in urls_titles:
        url = url_title[url_position]
        title = url_title[title_position]
        if url is not None and title is not None:
            fragment += processing_function(url, title)
        elif url is None or title is None:
            print("one of these was none of out url,title", url, title)
    fragment += '</section>'
    return fragment


def full_html(urls_titles, tag_text, processing_function=export_format_choices["HTML links + plaintext URL"]):
    """ This generates full page html

    >>> full_html([('https://www.example.com','Example.com Homepage'),('http://example.com','Example.com domain')],'TagTest')
    '<html><head><title>My links</title></head><body><main><h1>TagTest links bookmarked</h1><p>number of links: 2</p><p>Click links to open in browser or perform action.</p><p>Selecting with mouse then Ctrl+C (or Cmd+C) in this window copies only plain text.<br />To paste HTML text with clickable links <a href="#">save as HTML file</a> then copy/paste from browser <br />or <a href="##">copy all text below inc. any links to clipboard as HTML</a></p><br /><section id="links"><p><a href="https://www.example.com">Example.com Homepage</a>, https://www.example.com</p><p><a href="http://example.com">Example.com domain</a>, http://example.com</p></section></main></body></html>'
    
    """

    page = f'<html><head><title>My links</title></head><body><main><h1>{tag_text.replace("&&", "&")} links bookmarked</h1><p>number of links: {len(urls_titles)}</p>{instructional_text}'
    page += make_list_source_from_urls_titles(urls_titles=urls_titles, processing_function=processing_function)
    page += '</main></body></html>'
    return page


if __name__ == "__main__":
    import doctest

    doctest.testmod()
