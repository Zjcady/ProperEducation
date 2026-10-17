# A01 challenge · Values, types, variables, f-strings

Three levels in `challenge.py`. Each adds one constraint. Pass level 1 before reading level 2.

## Level 1 · `kind(value)`
Return the type name of a value as a string: `"int"`, `"float"`, `"str"`, or `"bool"`.
`kind(3)` is `"int"`. `kind(True)` is `"bool"`.

## Level 2 · `receipt_line(item, price, qty)`
Return one line of a receipt, exactly like `"3 x Apple @ $0.50 = $1.50"`. Price and total always show two decimals.

## Level 3 · `clock(seconds)`
Turn a number of seconds into `"h:mm:ss"`. `clock(3669)` is `"1:01:09"`. Minutes and seconds are always two digits, hours are not padded. Use `//` and `%`, no loops, no `if`.

## Hints (one at a time, after 5 real minutes)

<details>
<summary>Hint 1 · a nudge</summary>

Level 1: `type(x)` gives you a type object. Type objects have a `.__name__`. Level 2: everything you need is in the f-string section of read.md. Level 3: how many seconds in an hour? In a minute? `//` tells you how many fit, `%` tells you what's left over.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Level 3: `hours = seconds // 3600`. What's left after removing the hours is `seconds % 3600`. Do the same split again for minutes. Format with `:02d`.

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
h = seconds // 3600
rest = seconds % 3600
m = rest // ____
s = rest % ____
return f"{h}:{m:02d}:{s:02d}"
```

</details>
