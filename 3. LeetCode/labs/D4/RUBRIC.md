# D4 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Learner can say why the threshold is done in HSV and not BGR, and what H, S and V each say about a gecko pixel. |
| 3 | Learner can explain what the morphological open does to a lone speckle and to the gecko, and what would change with a 15x15 kernel. |
| 4 | `largest_blob` returns `None` on an empty mask instead of crashing; learner can say why a tracker has to handle "not found" and what `track` records for that frame. |
| 5 | Learner can say where the centroid comes from (`m10/m00`, `m01/m00`) and why it beats the center of the bounding box for a lopsided blob. |
| 6 | From the `python3 perception.py` output, learner can say how far the centroids are from the truth and why a real camera would make that number bigger. |
| 7 | `speed` skips `None` gaps; learner can say why the mean is over pairs rather than frames, and what a missed frame does to a version that doesn't skip. |
| 8 | Learner can name two things that would break this tracker on a real camera (lighting, a second orange thing, motion blur) and which function each one hits first. |
