# Linked List

**Reach for it when you see**
- `ListNode` in the signature
- "in place", O(1) space
- "cycle", "middle", "nth from end"

**The move**
Draw it. Three boxes and arrows on paper before any code. Then: keep `prev`, `cur`, `nxt` pointers and rewire one arrow at a time. For position problems, use two pointers moving at different speeds.

**Templates**
```python
# reverse
prev, cur = None, head
while cur:
    nxt = cur.next
    cur.next = prev
    prev, cur = cur, nxt
return prev

# fast / slow (middle, cycle detection)
slow = fast = head
while fast and fast.next:
    slow, fast = slow.next, fast.next.next
```

**Gotchas**
- Save `cur.next` *before* overwriting it. Every linked list bug is this.
- A dummy head (`dummy = ListNode(0, head)`) removes every "what if it's the first node" special case.
- Test with 0, 1 and 2 nodes. The harness has `to_linked` and `to_list` for that.
