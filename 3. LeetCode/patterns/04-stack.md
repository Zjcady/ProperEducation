# Stack

**Reach for it when you see**
- brackets / nesting / "most recent unmatched thing"
- "next greater element", "previous smaller element"
- undo, backtrack one level, evaluate an expression

**The move**
Push things you haven't resolved yet. When the current item resolves the top of the stack, pop. The stack always holds exactly the "still waiting" items, in order.

**Template (monotonic stack, next greater element)**
```python
stack = []                      # indices, values decreasing
ans = [0] * len(nums)
for i, x in enumerate(nums):
    while stack and nums[stack[-1]] < x:
        j = stack.pop()
        ans[j] = i - j          # x is the answer for j
    stack.append(i)
```

**Gotchas**
- Always guard `stack[-1]` with `stack and`.
- Store **indices** when you'll need distances.
- Valid Parentheses: a dict mapping closers to openers makes it 8 lines.
