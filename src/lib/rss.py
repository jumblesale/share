import settings
import store


# uses ~karlen's magnificent rss tool
def add(
        user="", page="", description="",
        feed_location=settings.rss_location,
):
    shares = _get_shares_from_store()
    xml = "\n".join(
        _header() + _create_items_xml(shares) + _footer()
    )
    with open(feed_location, "w") as f:
        f.write(xml)
    return xml


def _get_shares_from_store(limit=settings.rss_limit):
    return store.load(limit)


def _create_items_xml(shares):
    xml = []
    for share in shares:
        share_xml = "\n".join(_create_item_xml(
            share['user'],
            share['page'],
            share['description']
        ))
        xml.append(share_xml)
    return xml


def _create_item_xml(user, page, description):
    tilde_url = "http://tilde.town/~" + user + "/" + page
    new_item = """
\t\t<item>
\t\t\t<title>%s</title>
\t\t\t<link>%s</link>
\t\t\t<guid>%s</guid>
\t\t\t<description>%s</description>
\t\t\t<author>%s@tilde.town</author>
\t\t</item> """.lstrip("\n")\
               % (page, tilde_url, tilde_url, description, user)
    return new_item.split("\n")


def _header():
    feed_title = "tilde town share feed"
    link = "http://tilde.town"
    description = "share link for feels from tone town"
    rss_link = "http://tilde.town/~jumblesale/sharefeed.xml"
    feed_name = "/home/jumblesale/public_html/sharefeed.xml"
    header = """
<?xml version='1.0' encoding='UTF-8' ?>
<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>
\t<channel>
\t\t<title>%s</title>
\t\t<link>%s</link>
\t\t<description>%s</description>
\t\t<atom:link href='%s' rel='self' type='application/rss+xml' />"""\
        .lstrip("\n")\
        % (feed_title, link, description, rss_link)
    return header.split("\n")


def _footer():
    return "\n\t</channel>\n</rss>".split("\n")

if __name__ == "__main__":
    print add()
