import csv
import xml.etree.ElementTree as ET

from json import load
from typing import Dict, List, Tuple, Text, Set


def webprocessing(a: Dict, b: List, c: Text, d: Text = "") -> Tuple[Dict, Text]:
    """

    :param a: temporary account storage
    :param b: ref to xml object (groups, accounts, logins)
    :param c: switcher
    :param d: group id or GID
    :return: temporary storage and GID
    """
    if c == "group" and d != "":
        if d == "-5":
            a["-5"] = {"Name": None}
            return a, "-5"
        else:
            for i in b:
                for j in i:
                    if a.get(f"{j.get('ID')}") is None:
                        a[f"{j.get('ID')}"] = {"Name": j.get("Name")}
                        return a, j.get("ID")
    elif c == "account" and d != "":
        for i in b:
            for j in i:
                GID_: Text = j.get("ParentID")
                if a.get(GID_) is not None and GID_ == d:
                    loginlink: List = j.findall("LoginLinks/Login")
                    for login_ in loginlink:
                        if a[GID_].get("Account") is None:
                            if j.get("Comments") is None:
                                if login_.get("ParentID") == j.get("ID"):
                                    a[GID_]["Account"] = [[j.get("Name"), j.get("ID"), j.get("Link"),
                                                          login_.get("SourceLoginID")]]
                            else:
                                if login_.get("ParentID") == j.get("ID"):
                                    a[GID_]["Account"] = [[j.get("Name"), j.get("ID"), j.get("Link"), j.get("Comments"),
                                                          login_.get("SourceLoginID")]]
                        elif a[GID_].get("Account") is not None:
                            if j.get("Comments") is None:
                                if login_.get("ParentID") == j.get("ID"):
                                    a[GID_]["Account"].append([j.get("Name"), j.get("ID"), j.get("Link"),
                                                              login_.get("SourceLoginID")])
                            else:
                                if login_.get("ParentID") == j.get("ID"):
                                    a[GID_]["Account"].append([j.get("Name"), j.get("ID"), j.get("Link"), j.get("Comments"),
                                                              login_.get("SourceLoginID")])
            return a, d
    elif c == "login" and d != "":
        for i in b:
            for j in i:
                record = a[d]["Account"]
                for n in range(0, len(a[d]["Account"])):
                    if type(record[n][len(record[n]) - 1]) is not dict and type(record[n][len(record[n]) - 1]) is str:
                        if record[n][len(record[n]) - 1] == j.get("ID"):
                            a[d]["Account"][n][len(record[n]) - 1] = {"Login": j.get("Name"), "Password": j.get("Password")}
            return a, d


if __name__ == '__main__':
    """
    
    """
    with open("config.json") as config:
        cfg = load(config)

    tree: List = ET.parse(cfg["stickypasswordWebPath"])
    root = tree.getroot()

    group: List = root.findall("./Database/Groups")
    account: List = root.findall("./Database/Accounts")
    login: List = root.findall("./Database/Logins")

    storage: Dict = {}
    control: Set = set()

    for accounts in account:
        for elem in accounts:
            if elem.get("ParentID") not in control:
                control.add(elem.get("ParentID"))
                storage, GID = webprocessing(storage, group, "group", elem.get("ParentID"))
                storage, GID = webprocessing(storage, account, "account", d=GID)
                storage, GID = webprocessing(storage, login, "login", d=GID)

    nordpasstemplate: List[Text] = ["name", "url", "username", "password", "note",
                                    "cardholdername", "cardnumber", "cvc", "expirydate",
                                    "zipcode", "folder", "full_name", "phone_number", "email",
                                    "address1", "address2", "city", "country", "state"]

    with open('nordpass.csv', "w", newline="", encoding="utf8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(nordpasstemplate)

        for g in storage:
            if g != "-5":
                nordfolder: List = [storage[g]["Name"]]
                for i in range(0, len(nordpasstemplate) - 1):
                    nordfolder.append("")
                csvwriter.writerow(nordfolder)

        for gids in storage:
            for account in storage[gids]["Account"]:
                if type(account[3]) is str:
                    nordrecord: List = [account[0], account[2], account[4]["Login"], account[4]["Password"], account[3]]
                    for i in range(len(nordpasstemplate) - 5):
                        nordrecord.append("")
                    if gids != "-5":
                        nordrecord[10] = storage[gids]["Name"]
                elif type(account[3]) is dict:
                    nordrecord: List = [account[0], account[2], account[3]["Login"], account[3]["Password"]]
                    for i in range(len(nordpasstemplate) - 4):
                        nordrecord.append("")
                    if gids != "-5":
                        nordrecord[10] = storage[gids]["Name"]
                csvwriter.writerow(nordrecord)
