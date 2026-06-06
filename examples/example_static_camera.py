from pygame_visor import Visor, VisorMode
from common import App


def main():
    app = App((1000, 600))

    view = Visor(
        VisorMode.RegionLetterbox,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    current_center = app.player_pos.center
    view.move_to(current_center)

    def create_new_neighbours(r):
        return [
            (side, r.copy().move(dx, dy))
            for side, (dx, dy) in [
                ("up", (0, -r.height)),
                ("right", (r.width, 0)),
                ("bottom", (0, r.height)),
                ("left", (-r.width, 0)),
            ]
        ]

    neighbours = create_new_neighbours(view.region)
    exclude = None
    exclude_map = {"left": "right", "right": "left", "up": "bottom", "bottom": "up"}

    for delta in app.loop(60):
        view.lerp_to(current_center, view.fps_corrected_weight(0.1, delta))

        for side, sr in neighbours:
            if app.player_pos.colliderect(sr):
                if side != exclude:
                    current_center = sr.center
                    if side in ("left", "right"):
                        view.move_to(sr.center)
                    neighbours = create_new_neighbours(sr)
                    exclude = exclude_map[side]
                break
        else:
            exclude = None

        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))

        # render the player
        view.render(app.screen, [(app.player_pos.topleft, app.player_surf)])


if __name__ == "__main__":
    main()
