# Math & Geometry

**Reach for it when you see**
- "rotate", "spiral", "in place" on a matrix
- index arithmetic, modular tricks

**The move**
There is no trick. There is careful bookkeeping. Write the four boundary variables (`top, bottom, left, right`) and move exactly one per side.

**Templates**
```python
# rotate 90° clockwise, in place = transpose then reverse each row
for i in range(n):
    for j in range(i + 1, n):
        m[i][j], m[j][i] = m[j][i], m[i][j]
for row in m:
    row.reverse()

# spiral: shrink the box after each side
top, bottom, left, right = 0, R - 1, 0, C - 1
while top <= bottom and left <= right:
    ...right along top, down the right, left along bottom, up the left
    top += 1; right -= 1; bottom -= 1; left += 1
```

**Gotchas**
- Spiral: after walking the top and right, check `top <= bottom` and `left <= right` again before the bottom and left, or single rows get walked twice.
- Set Matrix Zeroes in O(1) space: use the first row and column as the markers.
