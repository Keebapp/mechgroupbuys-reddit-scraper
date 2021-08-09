import json


class GroupBuy:

    def __init__(self, title: str, link: str, mod_comment):
        self.__name = title
        self.__postLink = link
        self.__imgLink = str()  # TODO
        self.__price = dict()  # index prices by kit name (i.e "base kit" : "$134", "alphas", "$40", etc)
        self.__endDate = str()  # TODO
        self.__vendors = dict()  # index vendor links by vendor names (i.e "kbdfans" : "kbdfans.com")
        self.__modComment = mod_comment
        self.__purchaseMethod = str()  # TODO

        self.__itemTypes = list()
        self.__itemTypes.append("Keycaps")
        self.__itemTypes.append("Switches")
        self.__itemTypes.append("Deskmat")
        self.__itemTypes.append("Keyboard")
        self.__itemTypes.append("Misc")
        self.__itemType = int()
        self.__writtenItemType = str()

    def setItemType(self, index: int):
        self.__itemType = index
        self.__writtenItemType = self.__itemTypes[self.__itemType]

    def getPrice(self):
        return self.__price

    def getItemType(self):
        if self.__itemType in range(0, 4):
            return self.__writtenItemType
        else:
            raise ModuleNotFoundError("An item type for group buy '" + self.__name + "' has not been set.")

    def getPurchaseMethod(self):
        return self.__purchaseMethod

    def getTitle(self):
        return self.__name

    def getLink(self):
        return self.__postLink

    def getEndDate(self):
        return self.__endDate

    def getVendors(self):
        return self.__vendors

    def getModComment(self):
        return self.__modComment

    def addPrice(self, label: str, amount: str):  # amount should be a string starting with $
        if label in self.__price.keys():
            raise KeyError("Kit already exists within this group buy.")
        else:
            self.__price[label] = amount
            return True

    def setEnd(self, date: str):
        self.__endDate = date
        return True

    def addVendor(self, vendor_name: str, vendor_link: str):
        if vendor_name in self.__vendors:
            raise KeyError("Vendor already established for this group buy.")
        else:
            self.__vendors[vendor_name] = vendor_link

    def vendorDictString(self):
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

    def toString(self):
        vendor_string = self.vendorDictString()
        print(self.__name + ", " + str(self.__price) + " | vendors: " + vendor_string)

    def jsonOut(self):
        py_dict = {
                  "title": self.__name,
                  "item_type": self.__writtenItemType,
                  "prices": self.__price,
                  "end_date": self.__endDate,
                  "vendors": self.__vendors,
                  "purchase_type": self.__purchaseMethod,
                  "link": self.__postLink,
                  "img_link": self.__imgLink,
                  "raw_info": self.__modComment
                  }
        json_dict = json.dumps(py_dict)
        return json_dict
