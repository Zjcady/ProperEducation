# A01 · Values, types, variables, f-strings

**Why it exists.** Every program is values moving through names. Get these four things straight and the next eleven chapters are just combinations of them.

## The idea

A **value** is a piece of data. Every value has a **type**, which decides what you can do with it.

```python
42          # int    whole number
3.5         # float  decimal number
"hi"        # str    text, in quotes
True        # bool   True or False, capital letter
```

A **variable** is a name stuck to a value. `=` means "stick this name on this value", not "equals".

```python
price = 3.5
price = price * 2     # the name now points at 7.0
```

Ask a value its type with `type(x)`. Convert with `int("42")`, `float("3.5")`, `str(42)`.

An **f-string** builds text from values. Put `f` before the quote and `{}` around anything you want inserted. A colon inside the braces formats it.

```python
name, total = "Zach", 7.5
print(f"{name} owes ${total:.2f}")      # Zach owes $7.50
print(f"{3:02d}:{7:02d}")                # 03:07
```

`:.2f` means "float, 2 decimals". `:02d` means "integer, pad to width 2 with zeros".

Integer tricks you'll use constantly: `7 // 2` is `3` (floor division, drops the remainder). `7 % 2` is `1` (the remainder). `2 ** 10` is `1024`.

## The two things people get wrong

1. `"5" + 3` crashes. A str and an int don't add. Convert first: `int("5") + 3`.
2. `=` assigns, `==` compares. `if x = 5` is a syntax error. `if x == 5` is a question.

Run the examples. Change a number. Break something on purpose and read the error.
