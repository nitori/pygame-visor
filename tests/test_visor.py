import math

import pytest
from pygame.typing import RectLike

from pygame_visor import Visor, VisorMode
from pygame_visor.types import ScreenPos, WorldPos, Limits, ScreenSize


@pytest.mark.parametrize(
    "region,move_to,expected_region,expected_end",
    [
        [(0, 0, 100, 100), (50, 50), (0, 0, 100, 100), (100, 100)],
        [(0, 0, 100, 100), (10, 10), (-40, -40, 100, 100), (60, 60)],
        [(-50, -50, 100, 100), (0, 0), (-50, -50, 100, 100), (50, 50)],
        [(0.5, 0.5, 1.0, 1.0), (1.25, 1.25), (0.75, 0.75, 1.0, 1.0), (1.75, 1.75)],
    ],
)
def test_move_to(
    region: RectLike,
    move_to: WorldPos,
    expected_region: RectLike,
    expected_end: WorldPos,
):
    """
    Region view modes have the same results.
    This mostly just test if the pygame rect move is applied correctly.
    No need to test the Rect itself.
    """
    for mode in (VisorMode.RegionLetterbox, VisorMode.RegionExpand):
        view = Visor(mode, (800, 600), region=region)
        view.move_to(move_to)
        assert tuple(view.region) == expected_region, f"Failed for {mode}"
        assert tuple(view.region.bottomright) == expected_end, f"Failed for {mode}"


@pytest.mark.parametrize(
    "mode,region,screen_size,expected_bounding_box",
    [
        # the region stays exactly the same.
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (0, 0, 400, 300)],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (0, 0, 400, 300)],
        [VisorMode.RegionLetterbox, (0, 0, 100, 100), (1920, 1080), (0, 0, 100, 100)],
        # we get some extra view in the area outside the internal region
        [VisorMode.RegionExpand, (0, 0, 400, 300), (400, 300), (0, 0, 400, 300)],
        [VisorMode.RegionExpand, (0, 0, 100, 100), (1920, 1080), (-39, 0, 178, 100)],
        [VisorMode.RegionExpand, (0, 0, 100, 100), (1080, 1920), (0, -39, 100, 178)],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (-67, 0, 534, 300)],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, -206, 400, 712)],
        [
            VisorMode.RegionExpand,
            (-549, 317, 400, 300),
            (1920, 1080),
            (-616, 317, 534, 300),
        ],
        [
            VisorMode.RegionExpand,
            (-549, 317, 400, 300),
            (1080, 1920),
            (-549, 111, 400, 712),
        ],
    ],
)
def test_bounding_box(
    mode: VisorMode,
    region: RectLike,
    screen_size: ScreenSize,
    expected_bounding_box: RectLike,
):
    view = Visor(mode, screen_size, region=region)
    bounding_box = view.get_bounding_box()
    for a, b in zip(tuple(bounding_box), expected_bounding_box):
        assert math.isclose(a, b), (
            f"Failed for {mode} with: {tuple(bounding_box)} == {expected_bounding_box}"
        )


@pytest.mark.parametrize(
    "region,screen_size,expected_factor",
    [
        [(0, 0, 400, 300), (400, 300), 1.0],
        [(0, 0, 400, 300), (1920, 1080), 3.6],
        [(0, 0, 800, 600), (400, 300), 0.5],
    ],
)
def test_scaling_factor(
    region: RectLike, screen_size: ScreenSize, expected_factor: float
):
    view = Visor(VisorMode.RegionLetterbox, screen_size, region=region)
    factor = view.get_scaling_factor()
    assert factor == expected_factor


@pytest.mark.parametrize(
    "region,screen_size,expected_active_screen_area",
    [
        [(0, 0, 400, 300), (400, 300), (0, 0, 400, 300)],
        [(0, 0, 400, 300), (1920, 1080), (240, 0, 1440, 1080)],
        [(0, 0, 800, 600), (400, 300), (0, 0, 400, 300)],
        [(0, 0, 400, 300), (1080, 1920), (0, 555, 1080, 810)],
    ],
)
def test_active_screen_area(
    region: RectLike, screen_size: ScreenSize, expected_active_screen_area: RectLike
):
    view = Visor(VisorMode.RegionLetterbox, screen_size, region=region)
    active_screen_area = view.get_active_screen_area()
    for a, b in zip(active_screen_area, expected_active_screen_area):
        assert math.isclose(a, b), (
            f"Failed for: {tuple(active_screen_area)} == {expected_active_screen_area}"
        )


@pytest.mark.parametrize(
    "mode,region,screen_size,screen_pos,expected_world_pos",
    [
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (400, 300),
            (200, 150),
            (200, 150),
        ],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (960, 540),
            (200, 150),
        ],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (384, 108),
            (40, 30),
        ],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (240, 0), (0, 0)],
        [
            VisorMode.RegionLetterbox,
            (100, 100, 400, 300),
            (400, 300),
            (200, 150),
            (300, 250),
        ],
        # check left/right edges in Letterbox, with non-zero offsets. Caught a bug earlier in another test.
        [VisorMode.RegionLetterbox, (25, 25, 50, 50), (100, 100), (0, 0), (25, 25)],
        [VisorMode.RegionLetterbox, (25, 25, 50, 50), (100, 100), (98, 98), (74, 74)],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (1679, 1079),
            (400 / 1440 * 1439, 300 / 1080 * 1079),
        ],
        # the ends are *exclusive* for screen_pos_in_active_area, but the
        # coordinate math is well-defined regardless
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (1680, 1080),
            (400, 300),
        ],
        [
            VisorMode.RegionExpand,
            (0, 0, 400, 300),
            (1920, 1080),
            (1680, 1080),
            (400, 300),
        ],
        # offset: (240, 0) -- screen pos sits in the left letterbox bar
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (60, 0), (-50, 0)],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (60, 0), (-50, 0)],
        # offset: (0, 555) -- screen pos sits in the top letterbox bar
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1080, 1920), (0, 420), (0, -50)],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, 420), (0, -50)],
    ],
)
def test_screen_to_world(
    mode: VisorMode,
    region: RectLike,
    screen_size: ScreenSize,
    screen_pos: ScreenPos,
    expected_world_pos: WorldPos,
):
    view = Visor(mode, screen_size, region=region)
    world_pos = view.screen_to_world(screen_pos)
    for a, b in zip(world_pos, expected_world_pos):
        assert math.isclose(a, b), (
            f"Failed for {mode} width: {tuple(world_pos)} == {expected_world_pos}"
        )


@pytest.mark.parametrize(
    "mode,region,screen_size,screen_pos,expected",
    [
        # screen ratio matches region ratio: no bars, active area == screen
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (0, 0), True],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (200, 150), True],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (400, 300), (399, 299), True],
        # 1920x1080 + (0,0,400,300) -> active area (240, 0, 1440, 1080)
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (240, 0), True],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (1679, 1079), True],
        # right/bottom edges are exclusive
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (1680, 1080), False],
        # inside left letterbox bar
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (60, 0), False],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (239, 540), False],
        # 1080x1920 + (0,0,400,300) -> active area (0, 555, 1080, 810)
        # inside top letterbox bar
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1080, 1920), (0, 420), False],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1080, 1920), (540, 554), False],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1080, 1920), (540, 555), True],
        # RegionExpand: active area is the same rect as in Letterbox -- positions
        # in the extended/overflow area are NOT in the active area.
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (60, 0), False],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (1919, 1079), False],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, 420), False],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (960, 540), True],
    ],
)
def test_screen_pos_in_active_area(
    mode: VisorMode,
    region: RectLike,
    screen_size: ScreenSize,
    screen_pos: ScreenPos,
    expected: bool,
):
    view = Visor(mode, screen_size, region=region)
    assert view.screen_pos_in_active_area(screen_pos) is expected


@pytest.mark.parametrize(
    "mode,region,screen_size,world_pos,expected_screen_pos",
    [
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (400, 300),
            (200, 150),
            (200, 150),
        ],
        [
            VisorMode.RegionLetterbox,
            (100, 100, 400, 300),
            (400, 300),
            (300, 250),
            (200, 150),
        ],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (200, 150),
            (960, 540),
        ],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (40, 30),
            (384, 108),
        ],
        [VisorMode.RegionLetterbox, (0, 0, 400, 300), (1920, 1080), (0, 0), (240, 0)],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 400, 300),
            (1920, 1080),
            (400 / 1440 * 1439, 300 / 1080 * 1079),
            (1679, 1079),
        ],
        # same as screen_to_world, though it shouldn't be an issue here anyway.
        [VisorMode.RegionLetterbox, (25, 25, 50, 50), (100, 100), (25, 25), (0, 0)],
        [VisorMode.RegionLetterbox, (25, 25, 50, 50), (100, 100), (74, 74), (98, 98)],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (0, 0), (240, 0)],
        [
            VisorMode.RegionExpand,
            (0, 0, 400, 300),
            (1920, 1080),
            (400, 300),
            (1680, 1080),
        ],
        [
            VisorMode.RegionExpand,
            (0, 0, 400, 300),
            (1920, 1080),
            (400, 300),
            (1680, 1080),
        ],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1920, 1080), (-50, 0), (60, 0)],
        [VisorMode.RegionExpand, (0, 0, 400, 300), (1080, 1920), (0, -50), (0, 420)],
    ],
)
def test_world_to_screen(
    mode: VisorMode,
    region: RectLike,
    screen_size: ScreenSize,
    world_pos: WorldPos,
    expected_screen_pos: ScreenPos,
):
    view = Visor(mode, screen_size, region=region)
    screen_pos = view.world_to_screen(world_pos)

    for a, b in zip(screen_pos, expected_screen_pos):
        assert math.isclose(a, b), (
            f"Failed for {mode} width: {tuple(screen_pos)} == {expected_screen_pos}"
        )


@pytest.mark.parametrize(
    "mode,region,screen_size,limits,move_to,expected_bounding_box",
    [
        [
            VisorMode.RegionLetterbox,
            (0, 0, 100, 100),
            (100, 100),
            (0, 0, 100, 100),
            (10, 10),
            (0, 0, 100, 100),
        ],
        [
            VisorMode.RegionExpand,
            (0, 0, 100, 100),
            (100, 100),
            (0, 0, 100, 100),
            (10, 10),
            (0, 0, 100, 100),
        ],
        # <note>
        # The folowing expected_bounding_box values where taken from the actual output
        # from a (seemingly) working version. In case you encounter strange behaviour, but the tests succeed,
        # don't hesitate to adjust the test.
        [
            VisorMode.RegionLetterbox,
            (0, 0, 960, 540),
            (1280, 720),
            (-320, -320, 352, 352),
            (10, 10),
            (-464, -260, 960, 540),
        ],
        [
            VisorMode.RegionLetterbox,
            (0, 0, 960, 540),
            (1280, 720),
            (-320, -320, 352, 352),
            (950, 530),
            (-464, -188, 960, 540),
        ],
        [
            VisorMode.RegionExpand,
            (0, 0, 960, 540),
            (1280, 720),
            (-320, -320, 352, 352),
            (10, 10),
            (-464, -260, 960, 540),
        ],
        [
            VisorMode.RegionExpand,
            (0, 0, 960, 540),
            (1280, 720),
            (-320, -320, 352, 352),
            (950, 530),
            (-464, -188, 960, 540),
        ],
        # </note>
    ],
)
def test_limits_bounding_box(
    mode: VisorMode,
    region: RectLike,
    screen_size: ScreenSize,
    limits: Limits,
    move_to: WorldPos,
    expected_bounding_box: RectLike,
):
    view = Visor(mode, screen_size, region=region, limits=limits)
    view.move_to(move_to)
    assert tuple(view.get_bounding_box()) == expected_bounding_box


@pytest.mark.parametrize("mode", [VisorMode.RegionExpand, VisorMode.RegionLetterbox])
@pytest.mark.parametrize(
    "region,screen_size,factor,world_pos,expected_region,expected_center",
    [
        [(0, 0, 100, 100), (100, 100), 2.0, (0, 0), (0, 0, 200, 200), (100, 100)],
        [(0, 0, 100, 100), (100, 100), 2.0, (50, 50), (-50, -50, 200, 200), (50, 50)],
        [(0, 0, 100, 100), (100, 100), 2.0, None, (-50, -50, 200, 200), (50, 50)],
        [(0, 0, 100, 100), (100, 100), 2.0, (98, 98), (-98, -98, 200, 200), (2, 2)],
        [(0, 0, 100, 100), (100, 100), 0.5, (0, 0), (0, 0, 50, 50), (25, 25)],
        [(0, 0, 100, 100), (100, 100), 0.5, (50, 50), (25, 25, 50, 50), (50, 50)],
        [(0, 0, 100, 100), (100, 100), 0.5, None, (25, 25, 50, 50), (50, 50)],
    ],
)
def test_scale_by_at(
    mode: VisorMode,
    region: RectLike,
    screen_size: ScreenSize,
    factor: float,
    world_pos: WorldPos,
    expected_region: RectLike,
    expected_center: WorldPos,
):
    view = Visor(mode, screen_size, region=region)
    view.scale_by_at(factor, world_pos)
    assert tuple(view.region) == expected_region
    assert tuple(view.region.center) == expected_center
