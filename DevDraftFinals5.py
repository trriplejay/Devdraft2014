#pylint: disable=all
import sys
import unittest


class Address:

    def __init__(self, addressLine):
        self.addressLine = addressLine

    def getStreetAddress(self):
        #take everything before the first comma
        ###devdraft: documentation states that the street address could
        ###         possibly extend through to the second comma if the
        ###         address contains a second line, so we need to check
        ###         which case, and send back info up to the second comma
        ###         if there are two address lines
        return self.addressLine.split(",")[0].strip()

    def getCityName(self):
        #the city appears after the first (OR SECOND) comma
        ###devdraft: Since the specification explains that the address
        ###         could have a second address line, separated by a commma
        ###         from the street number and street name, we should not
        ###         assume that the city name will be contained in item [1]
        ###     There are really 2 cases here.  One where the second line st
        ###         address is specified, and one where it is not.  If the
        ###         former is true, we should look at [2] instead of [1],
        ###         otherwise look at [1].  This can be determined by length
        ###         of string after a split
        splitline = self.addressLine.split(",")
        #length of 3 implies no second address line
        if len(splitline) == 3:
            return splitline[1].strip()
        else:
            return splitline[2].strip()

    def getState(self):
        #state appears after 2 (OR 3) commas
        ###devdraft: again, if the street address takes up two lines, the
        ###         stateline could occur at [3] instead of [2]
        splitline = self.addressLine.split(",")
        if len(splitline) == 3:
            stateLine = splitline[2].strip()
        else:
            stateLine = splitline[3].strip()
        return stateLine.split(" ")[0].strip()

    def getZipCode(self):
        consecutiveDigits = 0

        #search for something that matches 5 consecutive digits
        ###devdraft: what if the street address has 5 digits?
        ###         we can safely assume based on the normalized
        ###         addresses that we will only have zip codes at the very
        ###         end of the text, which after a split, could be
        ###         obtained by using "len(splitline)-1".  So we only
        ###         need to search that location.  Also assuming that
        ###         state field will not be a series of digits
        splitline = self.addressLine.split(",")
        correctline = splitline[len(splitline)-1]
        for i in range (len(correctline)):
            c = correctline[i]
            if c.isdigit():
                consecutiveDigits+=1
                if consecutiveDigits == 5:
                    return int(correctline[i-4: i+1])
            else:
                consecutiveDigits = 0;

        #should never happen
        ###devdraft: but what if it does? maybe we should return
        ###         an error, or "None", since a zip of 0 would
        ###         actually result in a valid (but incorrect)
        ###         shipping calculation
        return None


class TaxCalculator:

    @staticmethod
    def calculateTax(orderAmount, state):
        ###devdraft: adjust for four possibilities:
        ###     1) the state might not be capitalized
        ###     2) the state could be "None" if the parsing fails
        ###     3) orderAmount could be None
        ###     4) orderAmount might not be an int (and we try to / with it)
        ###     should handle these cases gracefully
        if state is not None and orderAmount is not None and isinstance(orderAmount, int):
            state = state.lower()
            if state == "arizona":
                return orderAmount / 100 * 5
            elif state == "washington":
                return orderAmount / 100 * 9
            elif state == "california":
                return orderAmount / 100 * 6
            elif state == "delaware":
                return 0
            else:
                return orderAmount / 100 * 7
        else: return None


class ShippingCalculator:

    @staticmethod
    def calculateShipping(zipCode):
        ###devdraft: description says "zip codes higher than 75,000", but
        ###         the first condition checked >=, not >, so a zip code of
        ###         exactly 75,000 would return 10 when it should return 20
        ###     also need to make sure that zipcode is a number (not None)
        if zipCode is not None and isinstance(zipCode, int):
            if zipCode > 75000:
                return 10
            elif zipCode >= 25000:
                return 20
            else:
                return 30
        else:
            return None


class UnitTests(unittest.TestCase):

    def test_Zips(self):
        zipRange = {
            0: 30,
            24999: 30,
            25000: 20,
            25001: 20,
            74999: 20,
            75000: 20,
            75001: 10,
            99999: 10,
            123456: 10,
            None: None
        }
        for zip, exp in zipRange.iteritems():
            self.assertEquals(ShippingCalculator.calculateShipping(zip), exp)
        self.assertEquals(ShippingCalculator.calculateShipping("not an int"), None)

    def test_StateTax(self):
        basevalue = 100
        stateRange = {
            "Arizona": 5,
            "arizona": 5,
            "Washington": 9,
            "washington": 9,
            "Delaware": 0,
            "delaware": 0,
            "California": 6,
            "california": 6,
            "Kentucky": 7,
            "kentucky": 7,
            "djslkfjeoiwfdjkls": 7,
            None: None,
            "New HampShire": 7
        }
        for state, expresult in stateRange.iteritems():
            self.assertEqual(TaxCalculator.calculateTax(basevalue, state), expresult)
        basevalue = None
        self.assertIsNone(TaxCalculator.calculateTax(basevalue, state))
        basevalue = "i'm a string!"
        self.assertIsNone(TaxCalculator.calculateTax(basevalue, state))

    def test_GetCityName(self):
        myaddrlong = Address("add line 1, add line 2, mycity, mystate myzip")
        myaddrshort = Address("add line 1, mycity, mystate myzip")

        self.assertEqual(myaddrlong.getCityName(), "mycity")
        self.assertEqual(myaddrshort.getCityName(), "mycity")

    def test_GetStateName(self):
        myaddrlong = Address("add line 1, add line 2, mycity, mystate myzip")
        myaddrshort = Address("add line 1, mycity, mystate myzip")

        self.assertEqual(myaddrlong.getState(), "mystate")
        self.assertEqual(myaddrshort.getState(), "mystate")

    def test_GetZipCode(self):

        myaddr = Address("add line 1, add line 2, mycity, mystate 12345")
        self.assertEqual(myaddr.getZipCode(), 12345)

        myaddr = Address("add line 1, mycity, mystate 90210")
        self.assertEqual(myaddr.getZipCode(), 90210)

        myaddr = Address("7654321 add line 1, mycity, mystate 90210")
        self.assertNotEqual(myaddr.getZipCode(), 76543)
        self.assertEqual(myaddr.getZipCode(), 90210)


#main
if __name__ == '__main__':
    #unittest.main()

    numTestCases = int(sys.stdin.readline().strip())

    for i in range(numTestCases):
        basePrice = int(sys.stdin.readline().strip())
        addressString = sys.stdin.readline().strip()
        addr = Address(addressString)

        taxAmount = TaxCalculator.calculateTax(basePrice, addr.getState())
        shippingAmount = ShippingCalculator.calculateShipping(addr.getZipCode())

        print (basePrice + taxAmount + shippingAmount)
