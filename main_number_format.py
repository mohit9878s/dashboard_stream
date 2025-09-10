def format_comma_number(n):
    s = str(int(n))
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last_three

def format_decimal_number(n):
    n = int(n)
    if n >= 1e7:
        return f"{n / 1e7:.2f} Cr"
    elif n >= 1e5:
        return f"{n / 1e5:.2f} L"
    elif n >= 1e3:
        return f"{n / 1e3:.2f} K"
    return str(n)

if __name__ == "__main__":
    print(format_comma_number(123456789))   # 12,34,56,789
    print(format_decimal_number(12345678))  # 1.23 Cr





def format_indian_number(n):
    s = str(int(n))
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last_three

def format_compact_decimal(n):
    n = int(n)
    if n >= 1e7:
        return f"{n / 1e7:.2f} Cr"
    elif n >= 1e5:
        return f"{n / 1e5:.2f} L"
    elif n >= 1e3:
        return f"{n / 1e3:.2f} K"
    return str(n)

if __name__ == "__main__":
    print(format_indian_number(123456789))   # 12,34,56,789
    print(format_compact_decimal(12345678))  # 1.23 Cr


# def format_compact_number(x):
#     if x >= 1e7:
#         return f"{x / 1e7:.2f} Cr"
#     elif x >= 1e5:
#         return f"{x / 1e5:.2f} L"
#     elif x >= 1e3:
#         return f"{x / 1e3:.2f} K"
#     elif x == 0:
#         return "0"
#     else:
#         return f"{x:.0f}"
# if __name__ == "__main__":
    # print(format_compact_number(543210))     # 5.43 L