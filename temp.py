import datetime
import cooked_input as ci

def get_contact_info():
        name = ci.get_string(prompt="What is your name?")
        age = ci.get_int(prompt="How old are you?")
        birthday = ci.get_date(prompt="What is your birthday?")
        pizza = ci.get_yes_no(prompt="Do you like pizza?")
        return { 'name': name, 'age': age, "birthday": birthday, 'pizza': pizza}

#contact = get_contact_info()
#print(contact)

#cap_cleaner = ci.CapitalizationCleaner(style=ci.ALL_WORDS_CAP_STYLE)
#name = ci.get_string(prompt="What is your name?", cleaners=[cap_cleaner])
#print(name)

#age = ci.get_int(prompt="How old are you?", minimum=1)
#print(age)

#birthday = ci.get_date(prompt="How is your birthday?")
#print(birthday)

today = datetime.datetime.today()
birthday = ci.get_date(prompt="What is your birthday?", maximum=today)
print(birthday)

day = ci.get_date(prompt="Appointment date?", default="today")
print(day)



# today = datetime.datetime.today()
# birthday = ci.get_date(prompt="When is your next birthday (after today)?", minimum=today)
# print(birthday)

# noon = datetime.time(12, 0, 0)
# six = datetime.time(6, 0, 0)
# birthday = ci.get_date(prompt="What time do you want your wakeup call?", minimum=six, maximum=noon)
# print(birthday)
