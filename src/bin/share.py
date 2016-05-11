import sys
import os
import argparse

# import our libs
LIB_PATH = "%s/../%s" % (os.path.dirname(os.path.abspath(__file__)), "lib")
sys.path.append(LIB_PATH)

import client


parser = argparse.ArgumentParser(description='share a wonderful creation')
parser.add_argument('--user', metavar='U', type=str, required=True,
                    help='the user who created this beautiful artifact')
parser.add_argument('--page', metavar='P', type=str, required=True,
                    help='the location wondrous page - http://tilde.town/<user>/<page>')
parser.add_argument('--description', metavar='D', type=str, default="",
                    help="a description of the thing you'd like to share")


args = parser.parse_args()

client.share(args.user, args.page, args.description)

print "thank you for sharing %s/%s! users on tilde.town will be notified" % (args.user, args.page)
