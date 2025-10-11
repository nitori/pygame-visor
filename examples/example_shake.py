import pygame
import math
import random

from pygame_visor import Visor, VisorMode
from common import App


def ease_out_elastic(x: float) -> float:
    """
    https://easings.net/#easeOutElastic
    function easeOutElastic(x: number): number {
        const c4 = (2 * Math.PI) / 3;
        return x === 0
          ? 0
          : x === 1
          ? 1
          : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * c4) + 1;
    }
    """
    c4 = (2 * math.pi) / 3
    if x == 0:
        return 0
    elif x == 1:
        return 1
    return pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1


def main():
    app = App((1000, 600))

    view = Visor(
        VisorMode.RegionExpand,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    view.move_to(app.player_pos.center)

    button = pygame.Surface((100, 50))
    button.fill("black")

    font = pygame.Font(pygame.font.get_default_font())
    button_text = font.render("SHAKE", True, "white")

    shake_start = None
    shake_time = 0.5
    x, y = random.sample((1.0, 0.0), k=2)

    default_cursor = pygame.mouse.get_cursor()

    def try_set_cursor(cursor):
        try:
            pygame.mouse.set_cursor(cursor)
        except Exception as e:
            print(f"could not set cursor {cursor}. ignoring.", e)

    for delta in app.loop(60):
        view.move_to(app.player_pos.center)

        if shake_start is not None:
            shake_delta = pygame.time.get_ticks() / 1000 - shake_start
            if shake_delta > shake_time:
                shake_start = None
            progress = pygame.math.clamp(shake_delta / shake_time, 0.0, 1.0)
            eased = 1.0 - ease_out_elastic(progress)
            # region was already moved to player center
            # so we offset the region slightly (works, best as view.region is an FRect)
            f = 50 * eased
            view.region.move_ip(x * f, y * f)

        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))

        # render the player
        view.render(app.screen, [(app.player_pos.topleft, app.player_surf)])

        active_area = view.get_active_screen_area()

        # show a button
        r = button.get_rect()
        r.midbottom = (active_area.centerx, active_area.bottom - 10)
        app.screen.blit(button, r)
        tr = button_text.get_rect(center=r.center)
        app.screen.blit(button_text, tr)

        mx, my = pygame.mouse.get_pos()
        if r.collidepoint(mx, my):
            try_set_cursor(pygame.cursors.tri_left)
            if pygame.mouse.get_just_pressed()[0]:
                shake_start = pygame.time.get_ticks() / 1000
                x, y = random.sample((1.0, 0.0), k=2)
        else:
            try_set_cursor(default_cursor)


if __name__ == "__main__":
    main()
