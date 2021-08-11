import json


class GroupBuy:

    def __init__(self, title: str, link: str, mod_comment):

        self.__default_start_date = "No start date set"
        self.__default_end_date = "No end date set"
        self.__default_units = "# units not specified"

        self.__name = title
        self.__post_link = link
        self.__img_link = str()  # TODO
        self.__price = dict()  # index prices by kit name (i.e "base kit" : "$134", "alphas", "$40", etc)
        self.__end_factors = [self.__default_start_date, self.__default_end_date, self.__default_units]  # TODO maybe? Still WIP
        self.__vendors = dict()  # index vendor links by vendor names (i.e "kbdfans" : "kbdfans.com")
        self.__mod_comment = mod_comment
        self.__purchase_method = str()  # TODO

        self.__item_types = list()
        self.__item_types.append("Keycaps")
        self.__item_types.append("Switches")
        self.__item_types.append("Deskmat")
        self.__item_types.append("Keyboard")
        self.__item_types.append("Misc")
        self.__item_type = int()
        self.__written_item_type = str()

    def set_Item_Type(self, index: int):
        self.__item_type = index
        self.__written_item_type = self.__item_types[self.__item_type]

    def get_price(self):
        return self.__price

    def get_item_type(self):
        if self.__item_type in range(0, 4):
            return self.__written_item_type
        else:
            # raise ModuleNotFoundError("An item type for group buy '" + self.__name + "' has not been set.")
            print("An item type for group buy '" + self.__name + "' has not been set.")
            return "An item type for group buy '" + self.__name + "' has not been set."

    def get_purchase_method(self):

        return self.__purchase_method

    def get_title(self):
        return self.__name

    def get_link(self):
        return self.__post_link

    def get_end_date(self):
        return self.__end_factors

    def get_vendors(self):
        return self.__vendors

    def get_mod_comment(self):
        return self.__mod_comment

    def add_price(self, label: str, amount: str):  # amount should be a string starting with $
        if label in self.__price.keys():
            raise KeyError("Kit already exists within this group buy.")
        else:
            self.__price[label] = amount
            return True

    def set_end(self, date: list):
        self.__end_factors = date
        return True

    def add_vendor(self, vendor_name: str, vendor_link: str):
        if vendor_name in self.__vendors:
            raise KeyError("Vendor already established for this group buy.")
        else:
            self.__vendors[vendor_name] = vendor_link

    def vendor_dict_string(self):
        special_characters = {'[', ']', '\\'}
        build_string = ""
        for vendor in self.__vendors:
            vendor_name = self.__vendors[vendor].split("(")[0]
            fixed_vendor_name = ""
            for character in vendor_name:
                if character not in special_characters:
                    fixed_vendor_name = fixed_vendor_name + str(character)
            build_string = build_string + fixed_vendor_name + ", "
        return build_string

    def end_date(self):
        return self.__end_factors[0] + " - " + self.__end_factors[1] + " (" + self.__end_factors[2] + ")"

    def to_string(self):
        vendor_string = self.vendor_dict_string()
        date_string = self.end_date()
        return (self.__name + ", " + str(self.__price) + " | vendors: " + vendor_string + " | " + date_string)

    def json_out(self):
        py_dict = {
                  "title": self.__name.strip(),
                  "item_type": self.__written_item_type,
                  "prices": self.__price,
                  "end_date": self.__end_factors,
                  "vendors": self.__vendors,
                  "purchase_type": self.__purchase_method,
                  "link": self.__post_link,
                  "img_link": self.__img_link,
                  "raw_info": self.__mod_comment.body
                  }
        json_dict = json.dumps(py_dict)
        return json_dict
