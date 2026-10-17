# Trees

**Reach for it when you see**
- `TreeNode` in the signature
- "depth", "height", "subtree", "path", "level"
- BST: "kth smallest", "validate", "lowest common ancestor"

**The move**
Recursion. Trust the function to handle the children. Write the base case (`if not node: return ...`), then one line that combines the left answer and the right answer. For "by level", use a queue instead.

**Templates**
```python
# recursive (DFS)
def depth(node):
    if not node: return 0
    return 1 + max(depth(node.left), depth(node.right))

# level order (BFS)
from collections import deque
q = deque([root])
while q:
    for _ in range(len(q)):        # one level at a time
        node = q.popleft()
        if node.left:  q.append(node.left)
        if node.right: q.append(node.right)
```

**Gotchas**
- BST ordering: everything left is smaller, everything right is bigger. In-order traversal of a BST gives sorted order.
- "Validate BST" needs a (low, high) range passed down, not just a parent comparison.
- Max path sum: the value you *return* up (one branch) is different from the value you *record* (both branches).
