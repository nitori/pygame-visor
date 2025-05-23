# Pygame Visor

Camera/Viewport library.

Currently only works with `pygame-ce`, as it's using `pygame.FRect` in some parts.

## License

MIT © 2025 [Sani (https://github.com/nitori)](https://github.com/nitori)

## Install

Currently `pygame-ce` is required instead of `pygame`. If you have `pygame` installed, uninstall it first.

```
pip install pygame-visor pygame-ce
```
or using `uv`
```
uv add pygame-visor pygame-ce
```

## Camera/Viewport System – Feature Overview

- [x] Translate between world and screen coordinates (`world_to_screen`, `screen_to_world`)
    - Needed for input mapping (e.g. `screen_to_world(surface_rect, mouse_pos)`)
- [x] Support multiple view modes:
    - [x] Fixed world area (scales with screen), with or without padding
    - [ ] ~~Fixed zoom level (screen res affects visible area)~~
- [x] Camera movement via external control (`move_to(pos)`)
- [x] Optional clamping to world bounds / limits (camera can't move past edges)
- [x] Multiple views supported via independent instances (multi-camera/minimap/splitscreen)
- [x] Support lerping/smooth movement to a target position (or perhaps have the user do it themselves?)
    - [ ] Can probably get some more love, but a basic lerp already works.
- [x] Expose `get_bounding_box(surface_rect)` for rendering logic
    - Camera "requests" world region using the bounding box method above; game provides matching surfaces
    - [x] Accept surface size/rect for bounding box calculations (for the different view modes above)
- [ ] Handle zooming, including fractional zoom
    - [ ] UX: Optional **zoom-to-cursor** behavior (maintains world point under cursor)

### Optional stuff for now

- [ ] debug helpers (draw bounding box, show mouse world pos, etc.)
- [ ] Overscan/margin support for effects, camera shake, etc.

## View/Visor Modes

#### 1. Fixed Region (letterbox)

- A specific world size (e.g. 400x300 units) is always shown.
- If the screen's aspect ratio differs, black bars (letterboxing) fill the space.
- Scaling happens to fit the screen, preserving aspect ratio.

#### 2. Fixed Region (extended view)

- A specific world size (e.g. 400x300) is the *minimum* shown.
- If the screen is larger/wider, *more* of the world is revealed (i.e. expands the visible region).
- No letterboxing; fills the screen with as much world as possible.

## Basic Usage

```python
# get a surface the view can draw on. Could also be screen directly.
surf = pygame.Surface(400, 300)

# Create a Visor instance
visor = Visor(
    VisorMode.RegionLetterbox,  # One of two modes (see above)
    screen.get_rect(),  # pass in the rect of the surface you wish to draw on.
    region=(0, 0, 400, 300),  # world region to "view"
    limits=[-2000, -2000, 2000, 2000],  # Optional min/max x,y coords to constrain the visor to.
)

while True:
    # ...

    # Get the world bounding box (it returns a pygame.FRect, indicating the area of
    # the world that is currently visible)
    # Uses the stored screen rect passed in the constructor.
    # Use update_screen(new_rect) if your screen/surface got resized.
    bbox = visor.get_bounding_box()

    # Get iterable of surfaces, that cover the bounding box
    # This you need to implement yourself!
    # Return an iterable of tuples: ((world_x, world_y), tile_surface)
    # Where tile_surface (at the moment) must have world coords width/height. Surfaces are expected to be
    # pre-rendered at world-scale (1 unit = 1 pixel in world space). The Visor system will scale them
    # appropriately based on screen resolution and visor mode.
    tiles = world.get_tiles_iterable(bbox)

    # render tiles to surface, the visor will autoscale them to the correct size.
    visor.render(surf, tiles)

    # optional (if you don't use the screen directly), blit to screen:
    screen.blit(surf, (0, 0))

    # ...
```

If you have a player, that needs to be rendered on top of the map. Assuming `player.surf` holds
your players surface, and `player.rect` holds the players position:

```python
while True:
    # ...

    # update visor based on player position *before* getting the bbox
    visor.move_to(player.rect.center)  # visor.lerp_to(...) is also possible
    bbox = visor.get_bounding_box()

    # ... get tiles etc.

    # render map
    visor.render(surf, tiles)

    # render the player using visor.render, so it will be scaled correctly
    visor.render(surf, [
        (player.rect.topleft, player.surf)
    ])

    # ...
```

## Examples

See [`example_map.py`](examples/example_map.py) for a full working example of a main visor and a minimap using two independent cameras.

![example_map.png](examples/screenshots/example_map.png)

---

See [`example_modes.py`](examples/example_modes.py) to demonstrate the difference between `VisorMode.RegionLetterbox` and `VisorMode.RegionExpand`.

![example_modes.png](examples/screenshots/example_modes.png)

---

See [`example_zoom.py`](examples/example_zoom.py) to demonstrate a simple way to zoom your visor in and out.

![example_zoom.png](examples/screenshots/example_zoom.png)

---

See [`example_mouse.py`](examples/example_mouse.py) for a demonstration of tracking mouse screen pos to world tile position.

![example_mouse.png](examples/screenshots/example_mouse.png)

---

See [`example_ui.py`](examples/example_ui.py) for a simple UI example, of how to position them in the "active" area, in any VisorMode.

![example_ui.png](examples/screenshots/example_ui.png)**

---

See [`example_split_screen.py`](examples/example_split_screen.py) for a simple split screen example with two player. Using WASD and Arrow keys for independent movement.

![example_split_screen.png](examples/screenshots/example_split_screen.png)**

---

See [`example_shake.py`](examples/example_shake.py) for a simple shaking camera example.

See [`example_static_camera.py`](examples/example_static_camera.py) for a static camera fixed to regions. The camera 
does not follow the player all the time, only when the player moves to a new region.
