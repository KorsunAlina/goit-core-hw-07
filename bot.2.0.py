from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass 
        

class Phone(Field):
    def __init__(self, phone):
        if not phone.isdigit() or len(phone)!=10:
            raise ValueError("The number must have 10 digits!")
        super().__init__(phone)

        
class Birthday(Field):
    def __init__(self, value):
        try:
            date=datetime.strptime(value, "%d.%m.%Y").date()   
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone=Phone(phone_number)
        self.phones.append(phone)
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value==phone:
                return p
        return None    
    
    def remove_phone(self, phone_number):
        phone=self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)       
    
    def edit_phone(self, phone, new_phone):
        old = self.find_phone(phone)
        if not old:
            raise ValueError("Phone number not found.") 
        self.add_phone(new_phone)
        self.remove_phone(old.value)
        return True

    def add_birthday(self, date):
        self.birthday=Birthday(date)
        return True
           
    def __str__(self):
        birthday_str=self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "not added"
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value]=record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        self.data.pop(name, None)
    
    def find_next_weekday(self,start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    def adjust_for_weekend(self,birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday
            
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if not record.birthday:
                continue
            birthday_date = record.birthday.value
            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year=birthday_this_year.replace(year=today.year+1)

            days_until_birthday = (birthday_this_year - today).days

            if 0 <= days_until_birthday <= days:
                congratulation_date = self.adjust_for_weekend(birthday_this_year)
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date
                })

        return upcoming_birthdays
    
    def __str__(self):
        if not self.data:
            return "AddressBook is empty."
        
        result = []
        for record in self.data.values():
            phones = ", ".join(p.value for p in record.phones)
            result.append(f"Name: {record.name.value}\nPhones: {phones}")
        return "\n\n".join(result)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Enter correct arguments for this command please."
        except KeyError:
            return "Enter correct key for this command please."
        except IndexError:
            return "Enter correct index for this function please."
   
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book:AddressBook):
    name, phone, *_ = args
    record=book.find(name)
    message="Record is updated"
    if record is None:
        record=Record(name)
        book.add_record(record)
        message="Contact is added"
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book:AddressBook):
    name, phone, new_phone, *_ =args
    record=book.find(name)
    if record:
        record.edit_phone(phone, new_phone)
        return "Contact is changed."
    return "Contact is not found"
    
    """
    name, new_phone, *_ =args
    if name in contacts:
        contacts[name]=new_phone
        return "Contact is changed."
    else:
        return "Contact is not found"
    """
@input_error   
def username_phone(args,book:AddressBook):
    name=args[0]
    record=book.find(name)
    if not record:
        return "Contact is not found"
    return ", ".join(p.value for p in record.phones)    
    """
    name=args[0]
    if name in contacts:
        return contacts[name]
    else:
        return "Contact is not found"
    """
  
@input_error
def all_contacts(book:AddressBook):
    records=book
    return str(records)
   
@input_error
def add_birthday(args, book:AddressBook):
   name, date, *_ =args
   record=book.find(name)
   if record:
       record.add_birthday(date)
       return "Birthday is added"
   return "Contact is not found"
     
    
@input_error
def show_birthday(args, book:AddressBook):
   name, *_ =args
   record=book.find(name)
   if not record:
       return "Contact is not found"
   if not record. birthday:
       return "Birthday fo this contact is not added."
   return record.birthday.value.strftime("%d.%m.%Y")
  
       
@input_error
def birthdays(book:AddressBook):
    upcoming=book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    
    result_lines = []
    for b in upcoming:
        result_lines.append(
            f"{b['name']} - congratulate on {b['congratulation_date'].strftime('%d.%m.%Y')}"
        )
    return "\n".join(result_lines)
      

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command=="change":
            print(change_contact(args, book))
        elif command=="phone":
            print(username_phone(args, book))
        elif command=="all":
            print(all_contacts(book))
        elif command=="add-birthday":
            print(add_birthday(args, book))
        elif command=="show-birthday":
            print(show_birthday(args, book))
        elif command=="birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
