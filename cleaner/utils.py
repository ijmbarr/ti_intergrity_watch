from __future__ import division
import urllib2


def download_file(url, download_to):
    """
    Download files from url to download_to
    """
    # proxy = urllib.request.ProxyHandler({'http': 'thproxy.internet.point:8080',
    #                                     'https': 'thproxy.internet.point:8080'})
    # opener = urllib.request.build_opener(proxy)
    # urllib.request.install_opener(opener)
    # urllib.request.urlretrieve(url, download_to)
    with open(download_to, 'wb') as f:
        f.write(urllib2.urlopen(url).read())
        f.close()


def get_file_name(url):
    download_to = "../data/raw/"
    link_format = url.split(".")[-1]
    file_name = url.split("/")[-1]
    local_file_path = download_to + file_name
    return local_file_path


def get_row_template(row):
    """
    Creates a row to be filled out.
    """
    return {
        "department": row.Department,
        "minister": row.Minister,
        "period": row.Period,
        "source": row.Source,
        "link": row.Link,
        "date": None,
        "organisation": None,
        "purpose": None
    }


def normalise(s):
    """
    Normalises string s
    """
    to_replace = [
        ("&", "and")
    ]

    s = s.lower().strip()

    for old, new in to_replace:
        s = s.replace(old, new)

    return s.lower().strip()


def like(s1, s2):
    """
    Returns if s1 contains a term similar one in the list of strings s2.
    """
    s1_normed = normalise(s1)
    for s in s2:
        if s in s1_normed:
            return True
    return False


def find_column(cols, like_strings):
    """
    Returns the column that is most like one in like_strings.

    Will throw an error if there is not exactly one found.
    """
    col = [x for x in cols if like(x, like_strings)]
    assert (len(col) == 1)
    return col[0]


def format_for_csv(s):
    if s is None:
        return ""
    if "," in s:
        return '"' + s + '"'
    return s
