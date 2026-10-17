# Heap / Priority Queue

**Reach for it when you see**
- "k largest", "k smallest", "k closest", "top k"
- "median of a stream", "merge k sorted"
- repeatedly needing the min or max as things keep arriving

**The move**
A heap gives you the smallest item in O(log n). To keep the k *largest*, keep a min-heap of size k and pop the smallest whenever it overflows. For max, push negatives.

**Template**
```python
import heapq
heap = []
for x in nums:
    heapq.heappush(heap, x)
    if len(heap) > k:
        heapq.heappop(heap)       # throw away the smallest
# heap[0] is now the kth largest
```

**Gotchas**
- Python only has a min-heap. Push `-x` for a max-heap and negate on the way out.
- Push tuples `(key, item)` to sort by a key. Make sure ties can't crash on comparing `item`.
- Median from a stream = a max-heap of the small half and a min-heap of the large half, kept balanced.
