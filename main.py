import pickle
import os
from collections import UserDict
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value=None):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self.__value = new_value

    def validate(self, value):
        pass

    def __str__(self):
        return str(self.__value)


class Name(Field):
    pass


class Phone(Field):
    def validate(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Invalid phone number")


class Birthday(Field):
    def validate(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

    @property
    def days_to_birthday(self):
        if self.value:
            today = datetime.now().date()
            birthdate = datetime.strptime(self.value, "%Y-%m-%d").date()
            next_birthday = datetime(today.year, birthdate.month, birthdate.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, birthdate.month, birthdate.day).date()
            days_remaining = (next_birthday - today).days
            return days_remaining


class Record:
    def __init__(self, name=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones[:]:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break
        else:
            raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        return f"Contact: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value}"


class AddressBook(UserDict):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                results.append(record)
            else:
                for phone in record.phones:
                    if query in phone.value:
                        results.append(record)
                        break
        return results

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, batch_size=5):
        records = list(self.data.values())
        for i in range(0, len(records), batch_size):
            yield records[i:i + batch_size]

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                self.data = pickle.load(f)


# Приклад використання:
book = AddressBook("address_book.pkl")

# Завантаження існуючих даних, якщо вони доступні
book.load()

# Додавання записів
john_record = Record("John", "1990-05-20")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")
book.add_record(john_record)

jane_record = Record("Jane", "1985-12-15")
jane_record.add_phone("9876543210")
book.add_record(jane_record)

jane_record = Record("Taras", "1920-10-05")
jane_record.add_phone("5556667770")
book.add_record(jane_record)

# Збереження адресної книги
book.save()

# Пошук контактів
search_query = "555"
results = book.find(search_query)
if results:
    print(f"Результати пошуку для '{search_query}':")
    for result in results:
        print(result)
else:
    print("Збігів не знайдено.")
