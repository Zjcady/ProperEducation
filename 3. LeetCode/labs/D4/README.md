# D4 · Perception basics with OpenCV

**Maps to:** the responsibilities paragraph: "perception, motion/mission planning, controls". This lab is the perception line at its smallest: find one thing in an image, then follow it from frame to frame.
**You'll have at the end:** a color-segmentation pipeline that finds an orange leopard gecko on green substrate, a tracker that follows it through a sequence of frames and reports its speed, and the annotated frame (box plus dot) every robotics demo shows. Everything is synthetic: no camera, no files, no window. The scene is drawn by code, so you always know where the gecko really is and the tests can check you against the truth.

Setup: `pip install -r requirements.txt` (numpy and opencv-python-headless). Tests are offline. `python3 perception.py --frame` and `python3 perception.py` print what your functions found once they work.

**What perception is, in one sentence.** Turning pixels into a few numbers the rest of the robot can use: here, "the gecko is at (cx, cy), inside this box, moving this fast".

Read `perception.py` first. `make_frame` draws one 160x120 BGR image: green background, an orange filled ellipse, a few lone orange pixels (the speckles a cheap camera gives you), then sensor noise, all from a fixed seed. `make_sequence(n)` gives `n` frames with the gecko walking along `gecko_path(n)`, which is the truth the tests compare you against. `Blob` is the three things you report per gecko, `render_mask` prints a mask as text, and the HSV bounds `ORANGE_LOWER` / `ORANGE_UPPER` are given. OpenCV images are `numpy` arrays indexed `[y, x]` with channels in B, G, R order; a mask is a 2-D `uint8` array that is 255 where "yes" and 0 where "no".

## Step 1 · Find the gecko in one frame  (15 min)

You write `color_mask` and `largest_blob`:

- `color_mask(frame_bgr, lower_hsv, upper_hsv)`: `cv2.cvtColor` to HSV, `cv2.inRange` between the two bounds, then a morphological **open** (`cv2.morphologyEx` with `cv2.MORPH_OPEN` and a 5x5 kernel of ones). The open is an erode followed by a dilate: anything thinner than the kernel disappears, anything bigger comes back the same size. That is what deletes the speckles and keeps the gecko.
- `largest_blob(mask)`: `cv2.findContours` with `RETR_EXTERNAL`, pick the contour with the largest `cv2.contourArea`, and return a `Blob` of its `cv2.boundingRect` (x, y, w, h), its centroid from `cv2.moments` (`m10/m00`, `m01/m00`) and its area. No contours, or a largest contour with zero area: return `None`. The tracker in step 2 depends on that `None`.

**Where do the HSV numbers come from?** OpenCV's hue runs 0..179 (degrees divided by two), saturation and value 0..255. Thresholding in HSV instead of BGR works because lighting mostly moves V while the hue of an orange gecko stays near 15 whether the lamp is on or off. To find bounds for a real camera: convert one frame with `cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)`, print `hsv[y, x]` for a pixel you know is gecko and one you know is substrate, take about ±10 on H around the gecko's hue, and loosen S and V downward until the shadowed parts of the animal are in and the substrate is still out. Try it here: `hsv[60, 80]` on `make_frame()` is the gecko, `hsv[10, 10]` is the substrate. Say what each of the three numbers tells you before you move on.

Try it: `python3 perception.py --frame` prints the mask as text, the blob, and how many pixels `annotate` touched (step 2; until then it prints `annotate: not implemented yet (step 2)`, which is fine). The mask should be one oval and nothing else; if you see stray `#`, the open is missing.

## Step 2 · Track it across frames and annotate  (15 min)

You write `track`, `annotate` and `speed`:

- `track(frames)`: for each frame, `color_mask` then `largest_blob`; collect the centroid, or `None` when nothing was found. One entry per frame, same order.
- `annotate(frame, bbox, centroid)`: `frame.copy()` first, never draw on the input. `cv2.rectangle` for the box with thickness 1 and `cv2.circle` with radius 3 and thickness -1 for the dot. OpenCV wants integer pixel coordinates, so round the centroid. `bbox` of `None` means nothing was found: return the plain copy.
- `speed(centroids, fps)`: walk consecutive pairs; skip any pair with a `None` in it; each usable pair moved `math.hypot(dx, dy)` pixels in `1 / fps` seconds. Return the mean of the pair speeds, or `0.0` when no pair was usable. Skipping gaps is the whole point: a missed frame must not read as "the gecko stopped".

Run `python3 perception.py`. The gecko moves `PATH_STEP = (6, 2)` pixels per frame at 10 fps, so the true speed is `hypot(6, 2) * 10 = 63.2` px/s; your centroids should sit within a pixel of the truth and your speed within a few px/s. Be ready to say why they are not exact. Then rubric review and `python3 coach.py done D4`.
