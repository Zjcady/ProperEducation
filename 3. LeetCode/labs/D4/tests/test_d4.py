import math

import cv2
import numpy as np

import perception
from perception import ORANGE_LOWER, ORANGE_UPPER

CENTER, SIZE = (80, 60), (40, 20)      # one gecko, drawn where we say
GREEN_LOWER, GREEN_UPPER = (40, 60, 60), (80, 255, 255)


def gecko_frame(center=CENTER, size=SIZE, seed=0):
    return perception.make_frame(gecko_center=center, gecko_size=size, seed=seed)


def ideal_mask(center=CENTER, size=SIZE):
    """The ellipse exactly as make_frame drew it: the truth a mask is compared against."""
    truth = np.zeros((perception.HEIGHT, perception.WIDTH), np.uint8)
    cv2.ellipse(truth, center, (size[0] // 2, size[1] // 2), 0, 0, 360, 255, -1)
    return truth > 0


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------------------------------------------------------- step 1

def test_step1_color_mask_is_a_binary_uint8_image_the_size_of_the_frame():
    frame = gecko_frame()
    mask = perception.color_mask(frame, ORANGE_LOWER, ORANGE_UPPER)
    assert mask.shape == frame.shape[:2]
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)) <= {0, 255}
    assert np.count_nonzero(mask) > 0


def test_step1_color_mask_covers_the_gecko_and_nothing_else():
    mask = perception.color_mask(gecko_frame(), ORANGE_LOWER, ORANGE_UPPER) > 0
    inside = ideal_mask()
    assert mask[inside].mean() >= 0.9, "most of the drawn ellipse must be in the mask"
    near = cv2.dilate(inside.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    assert not (mask & ~near).any(), "mask pixels far from the gecko: speckles survived, did you open?"
    assert abs(mask.sum() - inside.sum()) <= 0.15 * inside.sum()


def test_step1_color_mask_opening_removes_the_speckles():
    # the frame has lone orange pixels; a 5x5 open erases them, so only background + gecko remain
    mask = perception.color_mask(gecko_frame(seed=1), ORANGE_LOWER, ORANGE_UPPER)
    n_labels, _ = cv2.connectedComponents(mask)
    assert n_labels == 2, f"expected background + one gecko, got {n_labels - 1} blobs"
    empty = perception.make_frame(gecko_center=None, seed=3)
    assert np.count_nonzero(perception.color_mask(empty, ORANGE_LOWER, ORANGE_UPPER)) == 0


def test_step1_color_mask_uses_the_range_it_is_given():
    frame = gecko_frame()
    inside = ideal_mask()
    green = perception.color_mask(frame, GREEN_LOWER, GREEN_UPPER) > 0
    assert green[~inside].mean() >= 0.95, "a green range must light up the substrate"
    assert not green[inside].any(), "and leave the gecko dark"


def test_step1_largest_blob_matches_the_drawn_gecko():
    blob = perception.largest_blob(perception.color_mask(gecko_frame(), ORANGE_LOWER, ORANGE_UPPER))
    assert blob is not None
    bbox, centroid, area = blob                 # it unpacks like a tuple too
    assert dist(centroid, CENTER) <= 1.5
    w, h = SIZE
    expected_bbox = (CENTER[0] - w // 2, CENTER[1] - h // 2, w + 1, h + 1)
    assert all(abs(got - want) <= 2 for got, want in zip(bbox, expected_bbox)), (bbox, expected_bbox)
    assert all(isinstance(v, int) for v in bbox)
    ellipse_area = math.pi * (w / 2) * (h / 2)
    assert abs(area - ellipse_area) <= 0.15 * ellipse_area


def test_step1_largest_blob_picks_the_biggest_of_two():
    # findContours lists the small bottom-right box first, so contours[0] is the wrong answer here
    mask = np.zeros((60, 80), np.uint8)
    mask[10:40, 10:20] = 255                    # an L-shaped gecko: the upright ...
    mask[30:40, 10:40] = 255                    # ... and its foot. 500 px inside a 30 x 30 box
    mask[45:55, 50:70] = 255                    # a 20 x 10 speck, the loser
    blob = perception.largest_blob(mask)
    assert blob.bbox == (10, 10, 30, 30)
    assert 400 <= blob.area <= 520
    # the L is heavy on its left and bottom, so its centroid is not the box center (25, 25)
    assert dist(blob.centroid, (20.5, 28.5)) <= 1.0, "the centroid comes from the moments, not the box center"


def test_step1_largest_blob_returns_none_on_an_empty_mask():
    assert perception.largest_blob(np.zeros((120, 160), np.uint8)) is None
    empty = perception.make_frame(gecko_center=None, seed=7)
    assert perception.largest_blob(perception.color_mask(empty, ORANGE_LOWER, ORANGE_UPPER)) is None


# ---------------------------------------------------------------- step 2

def test_step2_track_follows_the_known_path():
    n = 12
    frames = perception.make_sequence(n)
    truth = perception.gecko_path(n)
    found = perception.track(frames)
    assert len(found) == n
    assert all(c is not None for c in found)
    for got, want in zip(found, truth):
        assert dist(got, want) <= 1.5, (got, want)


def test_step2_track_reports_none_where_the_gecko_is_hidden():
    frames = perception.make_sequence(6)
    frames[3] = perception.make_frame(gecko_center=None, seed=42)
    found = perception.track(frames)
    assert found[3] is None
    assert [c is None for c in found] == [False, False, False, True, False, False]


def test_step2_annotate_returns_a_copy_and_draws_only_near_the_bbox():
    frame = gecko_frame()
    before = frame.copy()
    blob = perception.largest_blob(perception.color_mask(frame, ORANGE_LOWER, ORANGE_UPPER))
    out = perception.annotate(frame, blob.bbox, blob.centroid)
    assert out is not frame and out.shape == frame.shape and out.dtype == frame.dtype
    assert np.array_equal(frame, before), "annotate must not draw on the frame it was given"
    changed = np.any(out != frame, axis=2)
    assert changed.any()
    ys, xs = np.nonzero(changed)
    x, y, w, h = blob.bbox
    assert xs.min() >= x - 2 and xs.max() <= x + w + 2
    assert ys.min() >= y - 2 and ys.max() <= y + h + 2


def test_step2_annotate_draws_a_border_and_a_dot_not_a_filled_box():
    frame = gecko_frame()
    blob = perception.largest_blob(perception.color_mask(frame, ORANGE_LOWER, ORANGE_UPPER))
    out = perception.annotate(frame, blob.bbox, blob.centroid)
    changed = np.any(out != frame, axis=2)
    x, y, w, h = blob.bbox
    cx, cy = (round(v) for v in blob.centroid)
    assert changed[y, x], "the top-left corner of the rectangle"
    assert changed[cy, cx], "the dot at the centroid"
    assert not changed[cy, x + 4], "inside the box, away from the dot, nothing is drawn"
    assert changed.sum() < 0.5 * w * h, "a filled box would change far more pixels"


def test_step2_annotate_with_nothing_found_is_an_untouched_copy():
    frame = perception.make_frame(gecko_center=None, seed=5)
    out = perception.annotate(frame, None, None)
    assert out is not frame
    assert np.array_equal(out, frame)


def test_step2_speed_on_hand_made_centroids_skips_none_gaps():
    assert perception.speed([(0, 0), (3, 4), None, (10, 10), (13, 14)], fps=2) == 10.0
    assert perception.speed([(0, 0), (0, 0), (0, 0)], fps=30) == 0.0
    assert perception.speed([None, None, None], fps=30) == 0.0
    assert perception.speed([(5, 5)], fps=30) == 0.0
    assert perception.speed([], fps=30) == 0.0


def test_step2_speed_matches_the_synthetic_motion():
    frames = perception.make_sequence(12)
    true_speed = math.hypot(*perception.PATH_STEP) * perception.FPS
    assert abs(perception.speed(perception.track(frames), perception.FPS) - true_speed) <= 5.0
    frames[5] = perception.make_frame(gecko_center=None, seed=99)
    with_gap = perception.speed(perception.track(frames), perception.FPS)
    assert abs(with_gap - true_speed) <= 5.0, "a missed frame must not drag the mean down"
