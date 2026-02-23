from django import template

register = template.Library()


@register.filter
def format_phone(value):
    if not value:
        return ""

    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) == 10:
        return f"+359 {digits[1:4]} {digits[4:7]} {digits[7:10]}"
    if len(digits) == 12 and digits.startswith("359"):
        return f"+{digits[0:3]} {digits[4:7]} {digits[7:11]}"
    return value

