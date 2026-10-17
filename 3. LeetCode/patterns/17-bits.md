# Bit Manipulation

**Reach for it when you see**
- "without using + or -", "number of 1 bits", "reverse bits", "XOR"
- a problem about a *missing* or *single* number

**The move**
Treat the integer as 32 switches. Learn five tricks and you're done.

**Cheat sheet**
```python
n & 1            # last bit
n >> 1           # drop last bit
n & (n - 1)      # clear the lowest set bit   (count 1s in O(bits set))
a ^ a == 0       # XOR cancels pairs          (missing number, single number)
n & 0xFFFFFFFF   # force 32-bit unsigned view (Python ints are infinite)
```

**Gotchas**
- Python has no 32-bit overflow. For "add without +", mask with `0xFFFFFFFF` every step and convert back if the top bit is set.
- Counting Bits: `dp[i] = dp[i >> 1] + (i & 1)`. It's a DP problem in disguise.
- Missing Number: XOR all indices and all values. Pairs cancel, the leftover is the answer.
