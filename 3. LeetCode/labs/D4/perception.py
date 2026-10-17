"""D4 · Perception basics: find an orange leopard gecko on green substrate, then follow it.

    python3 perception.py             a 12-frame synthetic sequence: found centroid vs truth per frame, then speed
    python3 perception.py --frame     one frame: the mask drawn in ASCII, the blob, and what annotate changed

Everything is synthetic. make_frame draws the scene (green background, orange ellipse, a few
camera speckles, sensor noise) so you always know where the gecko really is. No camera, no
files, no window. Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import math
import sys
from typing import NamedTuple

import cv2
import numpy as np

# ------------------------------------------------------------------ scaffolding: the scene

WIDTH, HEIGHT = 160, 120
GREEN_BGR = (60, 150, 70)        # the substrate. OpenCV images are B, G, R.
ORANGE_BGR = (30, 140, 255)      # the gecko

# HSV in OpenCV: H is 0..179 (degrees / 2), S and V are 0..255. Orange sits around H 10..20.
# The README says how to find numbers like these for a real camera.
ORANGE_LOWER = (5, 100, 100)
ORANGE_UPPER = (25, 255, 255)

PATH_START = (30, 60)            # where the gecko is in frame 0
PATH_STEP = (6, 2)               # how far it moves per frame, in pixels
GECKO_SIZE = (40, 20)            # full width and height of the ellipse
FPS = 10


def make_frame(width: int = WIDTH, height: int = HEIGHT,
               gecko_center: tuple[int, int] | None = (80, 60),
               gecko_size: tuple[int, int] = GECKO_SIZE,
               seed: int = 0, speckles: int = 25) -> np.ndarray:
    """A BGR uint8 image: green background, an orange filled ellipse at gecko_center with the
    given full width and height, a few lone orange pixels (camera speckles), then gaussian
    sensor noise. gecko_center=None draws no gecko. The seed makes it reproducible."""
    rng = np.random.default_rng(seed)
    frame = np.empty((height, width, 3), np.uint8)
    frame[:] = GREEN_BGR
    if speckles:
        ys = rng.integers(0, height, speckles)
        xs = rng.integers(0, width, speckles)
        frame[ys, xs] = ORANGE_BGR
    if gecko_center is not None:
        w, h = gecko_size
        cx, cy = int(gecko_center[0]), int(gecko_center[1])
        cv2.ellipse(frame, (cx, cy), (w // 2, h // 2), 0, 0, 360, ORANGE_BGR, -1)
    noise = rng.normal(0, 6, frame.shape)
    return np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def gecko_path(n: int, start: tuple[int, int] = PATH_START,
               step: tuple[int, int] = PATH_STEP) -> list[tuple[int, int]]:
    """The true gecko center for each of n frames: start, then one step per frame."""
    return [(start[0] + i * step[0], start[1] + i * step[1]) for i in range(n)]


def make_sequence(n: int, width: int = WIDTH, height: int = HEIGHT,
                  gecko_size: tuple[int, int] = GECKO_SIZE, seed: int = 0) -> list[np.ndarray]:
    """n frames with the gecko walking along gecko_path(n). Up to 18 frames stay fully inside
    the default 160x120 frame. Each frame gets its own noise (seed + frame index)."""
    return [make_frame(width, height, center, gecko_size, seed=seed + i)
            for i, center in enumerate(gecko_path(n))]


class Blob(NamedTuple):
    """What largest_blob found: a bounding box, a centroid and an area (in pixels)."""
    bbox: tuple[int, int, int, int]      # x, y, w, h from cv2.boundingRect
    centroid: tuple[float, float]        # cx, cy from the moments
    area: float                          # cv2.contourArea


def render_mask(mask: np.ndarray, step: int = 4) -> str:
    """The mask as text, one character per step x step block: '#' where it is on, '.' where off."""
    rows = []
    for y in range(0, mask.shape[0], step):
        rows.append("".join("#" if mask[y, x] else "." for x in range(0, mask.shape[1], step)))
    return "\n".join(rows)


# ------------------------------------------------------------------ step 1

def color_mask(frame_bgr: np.ndarray, lower_hsv, upper_hsv) -> np.ndarray:
    """TODO(you): a uint8 mask (0 or 255) of the pixels whose HSV color is inside [lower_hsv, upper_hsv].

    cv2.cvtColor the frame to HSV (cv2.COLOR_BGR2HSV), cv2.inRange it between the two bounds
    (np.array them first), then clean it with a morphological open, cv2.morphologyEx with
    cv2.MORPH_OPEN and a 5x5 kernel of ones. The open erases blobs smaller than the kernel
    (the camera speckles) and leaves the gecko alone.
    """
    raise NotImplementedError


def largest_blob(mask: np.ndarray) -> Blob | None:
    """TODO(you): the biggest connected white region in the mask as a Blob, or None when there is none.

    cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) gives (contours, _).
    No contours: return None. Pick the contour with the largest cv2.contourArea; if even that
    area is 0 there is no real blob, return None. bbox is cv2.boundingRect(contour) as plain
    ints. The centroid comes from m = cv2.moments(contour): (m["m10"] / m["m00"],
    m["m01"] / m["m00"]). Return Blob(bbox, centroid, area).
    """
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

def track(frames: list[np.ndarray], lower_hsv=ORANGE_LOWER,
          upper_hsv=ORANGE_UPPER) -> list[tuple[float, float] | None]:
    """TODO(you): one centroid per frame, in order: color_mask then largest_blob; None where nothing was found."""
    raise NotImplementedError


def annotate(frame: np.ndarray, bbox: tuple[int, int, int, int] | None,
             centroid: tuple[float, float] | None,
             color: tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    """TODO(you): a copy of frame with the bbox drawn as a 1-pixel rectangle and the centroid as a filled dot.

    Never draw on the frame you were given: frame.copy() first. When bbox is None (nothing
    found) return the plain copy. Otherwise cv2.rectangle(out, (x, y), (x + w, y + h), color, 1)
    and cv2.circle(out, (round(cx), round(cy)), 3, color, -1). OpenCV wants int pixel
    coordinates, so the centroid has to be rounded.
    """
    raise NotImplementedError


def speed(centroids: list[tuple[float, float] | None], fps: float) -> float:
    """TODO(you): the gecko's mean speed in pixels per second, skipping gaps where it was not found.

    Walk consecutive pairs of centroids. A pair with a None in it is skipped. For each other
    pair the distance moved is math.hypot(x2 - x1, y2 - y1) pixels in 1 / fps seconds, so its
    speed is distance * fps. Return the mean of those speeds, or 0.0 when no pair was usable.
    """
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

def _show_one_frame() -> None:
    center = (80, 60)
    frame = make_frame(gecko_center=center)
    mask = color_mask(frame, ORANGE_LOWER, ORANGE_UPPER)
    print(f"frame {frame.shape[1]}x{frame.shape[0]}, gecko drawn at {center}, size {GECKO_SIZE[0]}x{GECKO_SIZE[1]}")
    print(f"mask: {int(np.count_nonzero(mask))} px on (one '#' below is a 4x4 block)")
    print(render_mask(mask))
    blob = largest_blob(mask)
    if blob is None:
        print("blob: none found")
        return
    cx, cy = blob.centroid
    print(f"blob: bbox={blob.bbox} centroid=({cx:.1f}, {cy:.1f}) area={blob.area:.0f}")
    out = annotate(frame, blob.bbox, blob.centroid)
    changed = int(np.count_nonzero(np.any(out != frame, axis=2)))
    print(f"annotate changed {changed} px; the original frame is untouched: {np.array_equal(frame, make_frame(gecko_center=center))}")


def _show_sequence(n: int = 12) -> None:
    frames = make_sequence(n)
    truth = gecko_path(n)
    found = track(frames)
    print(f"{'frame':>5}  {'true center':>12}  {'found centroid':>16}  {'error':>5}")
    for i, (t, f) in enumerate(zip(truth, found)):
        if f is None:
            print(f"{i:>5}  {str(t):>12}  {'not found':>16}")
            continue
        err = math.hypot(f[0] - t[0], f[1] - t[1])
        print(f"{i:>5}  {str(t):>12}  {f'({f[0]:.1f}, {f[1]:.1f})':>16}  {err:>5.2f}")
    true_speed = math.hypot(*PATH_STEP) * FPS
    print(f"speed: {speed(found, FPS):.1f} px/s at {FPS} fps (true {true_speed:.1f})")


def main(argv: list[str]) -> None:
    if "--frame" in argv:
        _show_one_frame()
    else:
        _show_sequence()


if __name__ == "__main__":
    main(sys.argv[1:])
