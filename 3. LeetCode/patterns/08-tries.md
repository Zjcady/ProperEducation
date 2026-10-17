# Tries

**Reach for it when you see**
- "prefix", "starts with", "autocomplete"
- many words to look up against many patterns (Word Search II)

**The move**
A tree where each edge is a letter. Walk down one letter at a time. A flag on a node means "a word ends here".

**Template**
```python
class Node:
    def __init__(self):
        self.kids = {}          # char -> Node
        self.end = False

def insert(root, word):
    node = root
    for ch in word:
        node = node.kids.setdefault(ch, Node())
    node.end = True
```

**Gotchas**
- `search` and `startsWith` are the same walk. Only the final check differs.
- Wildcard `.` means "try every child" at that step. That's recursion, not a loop.
- Word Search II: build a trie of the words, then DFS the grid while walking the trie. Prune when a prefix doesn't exist.
