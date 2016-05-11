import datetime


FILE = "/home/jumblesale/shares"


# add a new share
def add(user, page, description=""):
    dt = datetime.datetime.utcnow()
    with open(FILE, "a") as f:
        f.write(";".join([dt.isoformat(), user, page, description]))
        f.write("\n")
        f.close()


# load shares
def load(n=0, since=None):
    print since
    with open(FILE, "r") as f:
        lines = []
        if n == 0 and since is None:
            lines = f.read().splitlines()
            f.close()
        else:
            i = 0
            while i < n or n == 0:
                line = f.readline().rstrip()
                # end of file?
                if "" == line:
                    break
                # check date
                if since is not None:
                    # compare the dates
                    if _deserialize_date(line.split(";")[0]) < since:
                        continue
                lines.append(line)
                if n != 0:
                    i += 1
        f.close()
        return _format_lines(lines)


def _deserialize_date(date):
    # gosh
    return datetime.datetime.strptime(
        date, "%Y-%m-%dT%H:%M:%S.%f"
    )


# turns lines in the file into a hash
def _format_lines(lines):
    shares = []
    for line in lines:
        share = {}
        parts = line.split(";")
        # gosh
        share["date"] = _deserialize_date(parts[0])
        share["user"] = parts[1]
        share["page"] = parts[2]
        share["description"] = ";".join(parts[3:])
        shares.append(share)
    return shares
