def validate_phone(phone_number):
    if len(phone_number) == 11 and phone_number[0] == "0":
        return phone_number
    elif len(phone_number) == 10 and phone_number[0] == "9":
        return '0' + phone_number
    else:
        return phone_number