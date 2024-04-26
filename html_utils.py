# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
import html


def make_list_source_from_urls_titles(urls_titles):
    '''Take a list of tuples from titles_urls_from_IDs
    
    >>> make_list_source_from_urls_titles([(1,"https://www.example.com","Example.com Homepage"),(2,"http://example.com","Example.com domain")])
    '<p>number of links: 2</p><section id="links"><p><a href="https://www.example.com">Example.com Homepage</a><br/> (url is https://www.example.com)</p><p><a href="http://example.com">Example.com domain</a><br/> (url is http://example.com)</p></section>'
    
    '''
    number = f'<p>number of links: {len(urls_titles)}</p>'
    fragment = number + '<section id="links">'
    id_position = 0
    url_position = 1
    title_position = 2
    for url_title in urls_titles:
        url = url_title[url_position]
        title = url_title[title_position]
        if url is not None and title is not None:
            fragment += f'<p><a href="{html.escape(url)}">{html.escape(title)}</a><br/> (url is {html.escape(url_title[url_position])})</p>'
        elif url is None or title is None:
            print("one of these was none of out url,title", url, title)
    fragment += '</section>'
    return fragment


def full_html(urls_titles, tag_text):
    """ This generates full page html

    >>> full_html([(1,'https://www.example.com','Example.com Homepage'),(2,'http://example.com','Example.com domain')],'TagTest') 
    '<html><head><title>My links</title></head><body><main><h1>TagTest links bookmarked</h1><a href="#">Save as HTML file</a><br /><p>number of links: 2</p><section id="links"><p><a href="https://www.example.com">Example.com Homepage</a><br/> (url is https://www.example.com)</p><p><a href="http://example.com">Example.com domain</a><br/> (url is http://example.com)</p></section></main></body></html>'
    
    """
    page = f'<html><head><title>My links</title></head><body><main><h1>{tag_text.replace("&&", "&")} links bookmarked</h1><a href="#">Save as HTML file</a><br />'
    page += make_list_source_from_urls_titles(urls_titles=urls_titles)
    page += '</main></body></html>'
    return page


if __name__ == "__main__":
    import doctest
    doctest.testmod()
