import os


def get_user_home_dirs(homedir="/home"):
    users = []
    iter_users = os.walk(homedir)
    # skip the first entry - will be /home
    next(iter_users)
    for user in iter_users:
        users.append(user[0])
    return users


def user_exists(user):
    return os.path.exists("%s/%s" % ("/home", user))


def get_subscribed_user_home_dirs():
    subscribed_users = []
    all_home_dirs = get_user_home_dirs()
    for home_dir in all_home_dirs:
        share_path = "%s/%s" % (home_dir, ".share")
        print share_path
        if os.path.isfile(share_path):
            subscribed_users.append(home_dir)
    return subscribed_users


def get_subscribed_users():
    all_subscribed_home_dirs = get_subscribed_user_home_dirs()
    subscribed_users = []
    for home_dir in all_subscribed_home_dirs:
        # get rid of "/home
        user = home_dir[len("/home/"):]
        subscribed_users.append(user)
    return subscribed_users


def user_page_exists(user, page):
    if not user_exists(user):
        return False
    if os.path.isfile("%s/%s/%s/%s" % ("/home", user, "public_html", page)):
        return True
    return False


if __name__ == "__main__":
    print user_page_exists("jumblesale", "ksp/index.html")
