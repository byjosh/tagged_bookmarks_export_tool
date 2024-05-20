# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
import html
from datetime import datetime


def html_with_plain_url(url, title):
    return f'<p><a href="{html.escape(url)}">{html.escape(title)}</a>, {html.escape(url)}</p>'


def html_only(url, title):
    return f'<p><a href="{html.escape(url)}">{html.escape(title)}</a></p>'


def html_csv(url, title):
    return f'<br />{html.escape(url)},"{html.escape(title)}"'

tag_text = ["000"]
urls_titles = ["000"]

def get_fragments_dict(**kw):
    global tag_text
    global urls_titles
    if "tag_text" in kw:
        tag_text = kw["tag_text"]
    if "urls_titles" in kw:
        urls_titles = kw["urls_titles"]
    # old current timestamp for fragments int(datetime.now().timestamp())
    # 1st Jan 1990 timestamp used 631155661
    # attributes no longer used for folded - ADD_DATE="{631155661}" LAST_MODIFIED="{631155661}"
    return {
    "standard_html":{
        "start": f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{tag_text.replace("&&", "&")} links</title></head><body><main><h1>{tag_text.replace("&&", "&")} links bookmarked</h1><p>number of links: {len(urls_titles)}</p>{instructional_text}',
        "doc_section_start": '<section id="links">',
        "doc_section_end": '</section>',
        "item_start":'<p>',
      "item_end":'</p>',
        "end":'</main></body></html>',
       

    },
    "netscape_bookmark_format":{
        "start":"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<HTML>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
""",

      "doc_section_start":f'''{instructional_text}
<DT><H3 FOLDED >{tag_text.replace("&&", "&quot;")}</H3>
        <DL><p>
            ''',
      "doc_section_end": '''
        </DL><p>''',
      "item_start":'''
            <DT>'''
    ,
      "item_end":'''''',
      "end":'''
</HTML>
''',
    }
}




instructional_text = f'<p>Click links to open in browser or perform action.</p><p>Selecting with mouse then Ctrl+C (or Cmd+C) in this window copies only plain text.<br />To paste HTML text with clickable links <a href="#">save as HTML file</a> then copy/paste from browser <br />or <a href="##">copy all text below inc. any links to clipboard as HTML</a></p><br />'


def make_list_source_from_urls_titles(urls_titles,style_key):
    '''Take a list of tuples from titles_urls_from_IDs
    
    >>> make_list_source_from_urls_titles([("https://www.example.com","Example.com Homepage"),("http://example.com","Example.com domain")])
    '<section id="links"><p><a href="https://www.example.com">Example.com Homepage</a>, https://www.example.com</p><p><a href="http://example.com">Example.com domain</a>, http://example.com</p></section>'
    
    '''
    frag_dict = get_fragments_dict(urls_titles=urls_titles)[style_key]
    
    fragment = frag_dict["doc_section_start"]
    id_position = 0
    url_position = 1
    title_position = -1
    for url_title in urls_titles:
        i = 0
        length = len(url_title)-1
        for field in url_title:

            if i == 0:
                fragment += f'{frag_dict["item_start"]}{field}'

            elif i > 0 and i != length:
                fragment += f', {field}'
            elif i == length:
                fragment += f', {field}'
                fragment += frag_dict["item_end"]

            i = i + 1

    fragment += frag_dict["doc_section_end"]
    return fragment


def full_html(urls_titles, tag_text,style_key):
    """ This generates full page html

    >>> full_html([('https://www.example.com','Example.com Homepage'),('http://example.com','Example.com domain')],'TagTest')
    '<html><head><title>My links</title></head><body><main><h1>TagTest links bookmarked</h1><p>number of links: 2</p><p>Click links to open in browser or perform action.</p><p>Selecting with mouse then Ctrl+C (or Cmd+C) in this window copies only plain text.<br />To paste HTML text with clickable links <a href="#">save as HTML file</a> then copy/paste from browser <br />or <a href="##">copy all text below inc. any links to clipboard as HTML</a></p><br /><section id="links"><p><a href="https://www.example.com">Example.com Homepage</a>, https://www.example.com</p><p><a href="http://example.com">Example.com domain</a>, http://example.com</p></section></main></body></html>'
    
    """
    fragments = get_fragments_dict(urls_titles=urls_titles,tag_text=tag_text)
    
    #print(urls_titles)
    page = fragments[style_key]['start']
    page += make_list_source_from_urls_titles(urls_titles,style_key)
    page += fragments[style_key]['end']
    return page


if __name__ == "__main__":
    import doctest

    doctest.testmod()
