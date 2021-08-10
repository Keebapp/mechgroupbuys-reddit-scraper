import os
import re
import praw as p
from GroupBuy import GroupBuy
from datetime import date as d
debug = True  # enable print statements

def getType(title: str):
    keeb = {"108", "104", "19x", "80", "88", "tkl", "8x", "75", "84", "65", "67", "68", "sixty five",
            "sixty-five", "sixtyfive", "60", "61", "64", "40", "44", "47", "keyboard", "ergo", "yeti"}

    keycap_types = {"kat", "gmk", "kam", "epbt", "sa", "jtk", "filco", "akko", "npkc", "pbt", "abs", "domikey", "dsa",
                    "dss", "mg"}
    # may be missing some, feel free to check :)
    words = title.split(" ")
    for word in words:
        if word.lower() in keycap_types:
            return 0
    # if this code executes, then it isn't a keycap
    if re.search(".*switch.*", title.lower()) is not None:  # if title contains the word switch, it's probably a switch
        return 1
    if re.search(".*mats?\s?", title.lower()) is not None:
        return 2
    for keyword in keeb:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return 3
    return 4


def getKeebSize(title: str):
    full_size = {"108", "104", "19x"}  # separate lists allow an updated naming scheme in the event of changes
    tkl = {"80", "88", "tkl", "8x"}  # 8x and 19x are exclusively related to the kbdfans boards but can't hurt
    seventy_five = {"75", "84"}
    sixty_five = {"65", "67", "68", "sixty five", "sixty-five", "sixtyfive"}
    sixty = {"60", "61", "64"}
    forty = {"40", "44", "47"}

    for keyword in full_size:  # duplicated code, could be more compact but then it would be less readable
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Full-Size"

    for keyword in tkl:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "TKL"

    for keyword in seventy_five:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Seventy-five"
    for keyword in sixty_five:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Sixty-five"
    for keyword in sixty:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Sixty"
    for keyword in forty:
        search_term = ".*" + keyword + ".*"
        if re.search(search_term, title.lower()) is not None:
            return "Forty"
    return "Misc Size"


def getEndFactors(title: str):  # gb name is separated from dates/quantity by "//".
    units_regex = "[\d]*\s?units"  # I don't think this will ever come into play.
    default_start_date = "No start date set"
    default_end_date = "No end date set"
    default_units = "# units not specified"
    returnable_factors = [default_start_date, default_end_date, default_units]
    # returnable_factors contains default values that will indicate the scraper's success.

    month_names = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "november",
                   "december"}
    limiting_factors = title.split("//")[1]  # will contain both the end date and the limiting quantity, if applicable
    for month in month_names:  # find first date
        key_phrase_first = month + "\s?[\d]+\s-"
        key_phrase_first_with_year = month + "+\s?[\d]+,\s[\d]{4}\s-"
        key_phrase_second = "-[\s]" + month + "\s?[\d]+"
        first_month = re.search(key_phrase_first, limiting_factors.lower())
        first_month_with_year = re.search(key_phrase_first_with_year, limiting_factors.lower())
        second_month = re.search(key_phrase_second, limiting_factors.lower())
        if first_month is not None:
            returnable_factors[0] = first_month.group()[:-2]
        if second_month is not None:
            returnable_factors[1] = second_month.group()[2:]
        if first_month_with_year is not None:
            returnable_factors[0] = first_month_with_year.group()[:-8]

    # now all dates have been added to the returnable list, if applicable. If the entries are both default values,
    # then whole title must refer to units
    if returnable_factors[0] == default_start_date and returnable_factors[1] == default_end_date:
        returnable_factors[2] = limiting_factors
        # if both dates are default, means that none of the restrictions are date focused,
        # therefore must be unit-based
    else:  # part of the title must be dates, so must parse out the units restriction
        units_restriction_matcher = re.search(units_regex, limiting_factors.lower())
        if units_restriction_matcher is not None:
            returnable_factors[2] = units_restriction_matcher.group()

    return returnable_factors  # after the last block, code has had an opportunity to overwrite
    # all of the elements of the list. If it doesn't, then that means the issues in question were not found


"""Returns a ISO8601 date.
Accepts two date strings consisting of "[month] [day digit]"
return a list of two strings of dates in ISO 8601 format (YYYY-MM-DD)
"""


def convertDatesToISO(date: str, date_2: str):
    """Assumes both dates are current system year. If the latter one occurs chronologically
before the former (i.e given "december 4 2021" and "january 4 2021", january comes first in the year.
This means that the second date is likely the next year, so we'll assume that. They will not be the same month
and different year, though: group buys don't run for 12 months
"""
    iso_date_1 = "0000-00-00"  # default values
    iso_date_2 = "0000-00-00"
    month_dict = {  # can't wait for python 3.10 when we get switch statements :D
        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12
    }
    try:
        current_year = d.today().year
        month_1 = date.split(" ")[0]
        month_1_int = month_dict[month_1]
        day_1 = date.split(" ")[1]
        month_2 = date_2.split(" ")[0]
        month_2_int = month_dict[month_2]
        day_2 = date_2.split(" ")[1]
    except KeyError:
        return {"Start date not set", "End date not set"}  # I'm not overly creative
    if month_1_int > month_2_int or \
            ((month_1_int == month_2_int) and day_1 > day_2):  # if the second date happens first
        iso_date_1 = str(current_year) + "-" + getISONumString(month_1_int) + "-" + getISONumString(int(day_1))
        iso_date_2 = str(int(current_year) + 1) + "-" + getISONumString(month_2_int) + getISONumString(int(day_2))
    else:
        iso_date_1 = str(current_year) + "-" + getISONumString(month_1_int) + "-" + getISONumString(int(day_1))
        iso_date_2 = str(current_year) + "-" + getISONumString(month_2_int) + "-" + getISONumString(int(day_2))
    return {iso_date_1, iso_date_2}

def getISONumString(number: int):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)


def getVendors(mod_comment: str):  # TODO: splitting each_vendor on a colon causes URLs to break. need to fix.
    vendors_temp = dict()
    comment_sections = str(mod_comment).split(
        "---")  # comment is split into sections based on the mods placing a "---"
    for section in comment_sections:
        if re.search(".*Vendor.?:", section) is not None:  # section contains list of vendors
            try:
                list_of_vendors = section.split("**")[2].split("\n\n")  # tab usually starts with
                # "**Vendor:**" or "**Vendors:**
                # when split it becomes '', 'vendor:', '[body of vendor section]
                for each_vendor in list_of_vendors:
                    if len(each_vendor) > 1:
                        vendor_tuple = each_vendor.split(":")  # must split on colon, otherwise
                        # "east asia: [vendor]" will use "asia" as the vendor link for "east"
                        # first section contains region, second
                        # contains vendor name + link
                        vendors_temp[vendor_tuple[0]] = vendor_tuple[1]
                return vendors_temp
            except IndexError:
                return None


def toJson(group_buy: GroupBuy):
    return group_buy.json_out()


def getPrices(mod_comment: str, item_type: str):
    temp_prices = dict()
    comment_sections = str(mod_comment).split("---")
    regex_for_price = "[\w]+:\s\**\$[.?\d]+\**"  # matches a word, then a colon, then a space, then asterisks,
    # then a dollar sign and a number ending at the last valid digit, then more asterisks

    regex_for_switch_price = "\$[\d+\.]+"  # searches the price for a number starting with a dollar sign
    # and ending at the last valid digit
    if item_type == "Switches":
        price_match = re.search(regex_for_switch_price, mod_comment)
        if price_match is not None:
            temp_prices['Per switch'] = price_match.group()
            '''this is dangerous and I know it. If a switch is priced 
            in the comments by pack, this will display as being $10
            per switch, instead of $10 per pack of 15. However, not
            exactly sure how to fix that.'''
            return temp_prices
    else:
        for section in comment_sections:
            std_price_match = re.search(".*Price.?:.*", section)
            if std_price_match is not None:  # section contains prices
                piece = (section.split("\n"))
                for line in piece:
                    kits = re.search(regex_for_price, line)
                    if kits is not None:
                        if line.split(':')[0] not in temp_prices and len(line.split(":")) > 1:
                            valid_chars = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '$', '.'}
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
    subreddit_posts = reddit.subreddit('MechGroupBuys').new(limit=100)
    subreddit_posts_flair = list()
    for submission in subreddit_posts:
        if submission.link_flair_text != "EXPIRED":
            # TODO: the flair can say "EXTENDED" and sometimes a date, this needs to be incorporated into end dates
            subreddit_posts_flair.append(submission)
    GroupBuys = []
    for submission in subreddit_posts_flair:
        GB_search = re.search(r"\[GB]", submission.title)
        in_stock_search = re.search(".*in.?stock.*", submission.title)
        if GB_search is not None or in_stock_search is not None:
            submission_link = (submission.title + "[" + submission.permalink + "]")
            GB_name = str(submission.title).split("//")[0].split("]")[1]
            modComment = submission.comments[0]
            gb1 = GroupBuy(GB_name, submission_link, modComment)
            gb1.set_Item_Type(getType(gb1.get_title()))
            prices = getPrices(modComment.body, gb1.get_item_type())
            if prices:
                for label in prices:
                    gb1.add_price(label, prices[label])
            vendors = getVendors(modComment.body)
            if vendors:
                for vendor in vendors:
                    gb1.add_vendor(vendor, vendors[vendor])
            if debug:
                print(gb1.to_string())
            end_factors = getEndFactors(str(submission.title))
            dates = convertDatesToISO(end_factors[0], end_factors[1])
            gb1.set_end(dates[0], dates[1], end_factors[2])
            GroupBuys.append(gb1)
    json_str = "["
    for gb in GroupBuys:
        json_str += gb.json_out()
        json_str += ", "
        pass
    json_str += "]"
    if debug:
        print(json_str)
        print(GroupBuys)
