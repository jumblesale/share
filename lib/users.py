import os


def user_exists(user):
    return os.path.exists("%s/%s" % ("/home", user))


def user_page_exists(user, page):
    return False

if __name__ == "__main__":
    print user_exists("jumblesale")
