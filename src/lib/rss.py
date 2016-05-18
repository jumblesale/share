# uses ~karlen's magnificent rss tool
def add(user, page, description):
    tildeurl = "http://tilde.town/~" + user + "/" + page
    newItem = """<item>
    <title>%s</title>
    <link>%s</link>
    <guid>%s</guid>
    <description>%s</description>
    </item> """ % (page,tildeurl,tildeurl,description)
    print newItem

def header():
    Feedtitle = "tilde town share feed"
    link = "http://tilde.town"
    description = "share link for feels from tone town"
    rsslink = "http://tilde.town/~jumblesale/sharefeed.xml"
    feedname = "/home/jumblesale/public_html/sharefeed.xml"
    header = """<?xml version='1.0' encoding='UTF-8' ?>
    <rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>
    <channel>
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
    <atom:link href='%s' rel='self' type='application/rss+xml' /> """ % (Feedtitle,link,description,rsslink)
    print header

def footer():
    print "</channel>\n\n</rss>"

header()
add("jumblesale","ksp/index.html","pugs")
footer()
