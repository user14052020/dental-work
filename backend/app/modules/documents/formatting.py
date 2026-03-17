from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from html import escape


UNITS = {
    "male": (
        ("", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"),
        ("десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"),
        ("", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто"),
        ("", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот"),
    ),
    "female": (
        ("", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"),
        ("десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"),
        ("", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто"),
        ("", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот"),
    ),
}

ORDERS = (
    (("", "", ""), "male"),
    (("тысяча", "тысячи", "тысяч"), "female"),
    (("миллион", "миллиона", "миллионов"), "male"),
    (("миллиард", "миллиарда", "миллиардов"), "male"),
)


def format_money(value: Decimal) -> str:
    normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{normalized:,.2f}".replace(",", " ").replace(".", ",")


def format_date_ru(value: date | datetime | None) -> str:
    if value is None:
        return "—"
    current = value.date() if isinstance(value, datetime) else value
    return current.strftime("%d.%m.%Y")


def amount_to_words_ru(value: Decimal) -> str:
    normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rubles = int(normalized)
    kopecks = int((normalized - rubles) * 100)
    return f"{_number_to_words(rubles)} {_pluralize(rubles, ('рубль', 'рубля', 'рублей'))} {kopecks:02d} копеек"


def html_text(value: object | None) -> str:
    if value is None:
        return "—"
    text = str(value).strip()
    return escape(text) if text else "—"


def html_multiline(value: object | None) -> str:
    if value is None:
        return "—"
    text = escape(str(value).strip())
    return text.replace("\n", "<br />") if text else "—"


def checkbox(value: bool) -> str:
    return "☑" if value else "☐"


def _number_to_words(value: int) -> str:
    if value == 0:
        return "ноль"

    parts: list[str] = []
    order = 0

    while value > 0:
        chunk = value % 1000
        if chunk:
            names, gender = ORDERS[order]
            parts.insert(0, _chunk_to_words(chunk, gender, names))
        value //= 1000
        order += 1

    return " ".join(part for part in parts if part).strip()


def _chunk_to_words(value: int, gender: str, order_names: tuple[str, str, str]) -> str:
    ones, teens, tens, hundreds = UNITS[gender]
    words: list[str] = []
    h = value // 100
    t = value % 100
    d = t // 10
    u = t % 10

    if h:
        words.append(hundreds[h])
    if 10 <= t <= 19:
        words.append(teens[t - 10])
    else:
        if d:
            words.append(tens[d])
        if u:
            words.append(ones[u])

    if order_names != ("", "", ""):
        words.append(_pluralize(value, order_names))

    return " ".join(word for word in words if word)


def _pluralize(value: int, forms: tuple[str, str, str]) -> str:
    n = abs(value) % 100
    n1 = n % 10
    if 10 < n < 20:
        return forms[2]
    if 1 < n1 < 5:
        return forms[1]
    if n1 == 1:
        return forms[0]
    return forms[2]
