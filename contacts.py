from collections import OrderedDict
import Contacts


class Contact:
    def __init__(self, given_name :str, family_name :str, company_name :str, phone_numbers :dict[str, str]):
        self.givenName = given_name
        self.familyName = family_name
        self.companyName = company_name
        self.phoneNumber = Contact.best_phone_number(phone_numbers)

    @staticmethod
    def best_phone_number(phone_numbers) -> str:
        for key, val in phone_numbers.items():
            lower_key = str(key)
            if 'mobile' in str(key).lower():
                return str(val)
        return str(next(iter(phone_numbers.values())))

    def to_string(self) -> str:
        ret = '%s %s' % (self.givenName, self.familyName)
        if len(self.companyName.strip()) > 0:
            ret = '%s (%s)' % (ret.strip(), self.companyName.strip())
        if len(self.phoneNumber.strip()) > 0:
            ret = '%s -- %s' % (ret.strip(), self.phoneNumber.strip())
        return ret

    def key(self):
        ret = ''
        if len(self.givenName.strip()) > 0:
            ret += self.givenName.strip() + ' '
        if len(self.familyName.strip()) > 0:
            ret += self.familyName.strip()
        if len(ret.strip()) > 0:
            return ret.strip()
        return self.companyName.strip()


def add_contact(contact, stop):
    if contact.isKeyAvailable_(Contacts.CNContactPhoneNumbersKey):
        given_name = str(contact.givenName())
        family_name = str(contact.familyName())
        company_name = str(contact.organizationName())
        phone_numbers = {}

        for val in contact.phoneNumbers():
            phone_numbers[str(val.label())] = str(val.value().stringValue())
        if len(phone_numbers) > 0:
            new_contact = Contact(given_name, family_name, company_name, phone_numbers)
            ContactCache.cache[new_contact.key()] = new_contact
    else:
        print("Contact without phone number(s)")
    return False

class ContactCache:
    cache = {}

    def __init__(self):
        self.fetch_all_contacts()

    def fetch_all_contacts(self) -> None:
        if len(self.cache) > 0:
            return None
        fetch_request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_([
            Contacts.CNContactPhoneNumbersKey,
            Contacts.CNContactGivenNameKey,
            Contacts.CNContactFamilyNameKey,
            Contacts.CNContactOrganizationNameKey
        ])
        store = Contacts.CNContactStore.alloc().init()
        ok, error = store.enumerateContactsWithFetchRequest_error_usingBlock_(
            fetch_request, None, add_contact
            )
        if not ok:
            print("Fetching contacts failed", error)

        tmp_cache = self.cache
        self.cache = OrderedDict(sorted(tmp_cache.items(), key=lambda kv: (kv[1].familyName, kv[1].givenName)))
        return None

    def get_contacts(self, preposition = None):
        for key, val in self.cache.items():
            if preposition is None or preposition(val):
                yield val
