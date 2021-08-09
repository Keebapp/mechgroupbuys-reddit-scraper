import os
import re
import praw as p
from GroupBuy import GroupBuy


def getType(title):
    keeb = {"108", "104", "19x", "80", "88", "tkl", "8x", "75", "84", "65", "67", "68", "sixty five",
            "sixty-five", "sixtyfive", "60", "61", "64", "40", "44", "47"}

    keycap_types = {"kat", "gmk", "kam", "epbt", "sa", "jtk", "filco", "akko", "npkc", "pbt", "abs", "domikey"}
    # may be missing some, feel free to check :)
    words = title.split(" ")
    for word in words:
        if word.lower() in keycap_types:
            return 0
    # if this code executes, then it isn't a keycap
    if re.search(".*switch.*", title.lower()) is not None:  # if title contains the word switch, it's probably a switch
        return 1
    if re.search(".*deskmat.*", title.lower()) is not None:
        return 2
    for keyword in keeb:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return 3
    return 4


def getKeebSize(title):
    full_size = {"108", "104", "19x"}
    tkl = {"80", "88", "tkl", "8x"}
    seventy_five = {"75", "84"}
    sixty_five = {"65", "67", "68", "sixty five", "sixty-five", "sixtyfive"}
    sixty = {"60", "61", "64"}
    forty = {"40", "44", "47"}

    for word in full_size:
        search_term = ".*" + word + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Full-Size"

    for word in tkl:
        search_term = ".*" + word + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "TKL"

    for word in seventy_five:
        search_term = ".*" + word + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Seventy-five"
    for word in sixty_five:
        search_term = ".*" + word + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Sixty-five"
    for word in sixty:
        search_term = ".*" + word + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Sixty"
    for word in forty:
        search_term = ".*" + word + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Forty"
    raise ModuleNotFoundError("Keyboard keywords not found in title. Please reassign to misc.")


def getVendors(mod_comment: str):
    vendors_temp = dict()
    comment_sections = str(mod_comment).split("---")
    for section in comment_sections:
        section_match = re.search(".*Vendor.?:", section)
        if section_match is not None:  # section contains list of vendors
            list_of_vendors = section.split("**")[2].split("\n\n")
            for each_vendor in list_of_vendors:
                if len(each_vendor) > 1:
                    vendor_tuple = vendor.split(" ")
                    # first section contains region, second
                    # contains vendor name + link
                    vendors_temp[vendor_tuple[0]] = vendor_tuple[1]
            return vendors_temp


def getPrices(mod_comment: str, item_type: str):
    temp_prices = dict()
    comment_sections = str(mod_comment).split("---")
    regex_for_price = "[\w]+:\s\**\$[.?\d]+\**"  # not switches
    regex_for_switch_price = "\$[\d+\.]+"
    if item_type == "Switches":
        price_match = re.search(regex_for_switch_price, mod_comment)
        if price_match is not None:
            temp_prices['Per switch'] = price_match.group()
            return temp_prices
    else:
        for section in comment_sections:
            std_price_match = re.search(".*Price.?:.*", section)
            if std_price_match is not None:  # section contains prices
                piece = (section.split("\n"))
                for line in piece:
                    kits = re.search(regex_for_price, line)
                    if kits is not None:
                        if line.split(":")[0] not in temp_prices and len(line.split(":")) > 1:
                            valid_chars = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "$"}
                            price_without_special_chars = ""
                            for character in line.split(":")[1]:
                                if character in valid_chars:
                                    price_without_special_chars = price_without_special_chars + str(character)
                            temp_prices[line.split(":")[0]] = price_without_special_chars
                return temp_prices


if __name__ == '__main__':
    reddit = p.Reddit(client_id="_Y3HSItMMu-ihcSuySwMXA",
                      client_secret="hPZBFzWt_TFAFDV6yXbqA-qC9umTWg", password=os.environ['PASSWORD'],
                      username=os.environ['USERNAME'],
                      user_agent="User-Agent: MechGroupBuy Crawler :V0 (by u/HansTheIV)")
    subredditPosts = reddit.subreddit('MechGroupBuys').new(limit=4)
    GroupBuys = []
    for submission in subredditPosts:

        m = re.search(r"\[GB]", submission.title)
        n = re.search(".*in.?stock.*", submission.title)
        if m is not None or n is not None:
            submissionLink = (submission.title + "[" + submission.permalink + "]")
            GB_name = str(submission.title).split("//")[0].split("]")[1]
            modComment = submission.comments[0]
            gb1 = GroupBuy(GB_name, submissionLink, modComment)
            gb1.setItemType(getType(gb1.getTitle()))
            prices = getPrices(modComment.body, gb1.getItemType())
            for label in prices:
                gb1.addPrice(label, prices[label])
            vendors = getVendors(modComment.body)
            for vendor in vendors:
                gb1.addVendor(vendor, vendors[vendor])

            GroupBuys.append(gb1)
    for gb in GroupBuys:
        # print(gb.getModComment().body)
        gb.toString()
        pass
    # print(GroupBuys)
