import pygame
from pygame._sdl2.video import Texture
from pygame_visor.video import Visor, VisorMode
from common import App


def main():
    # switch our dummy app to use sdl2 texture features.
    # Use Texture hint so all the other app methods are hinted with the correct types
    app = App[Texture](use_sdl2=True)

    # this Visor class is imported from pygame_visor.video instead.
    # It's a subclass of the regular Visor, but overwrites the render method.
    view = Visor(
        VisorMode.RegionLetterbox,
        app.window.size,
        region=(0, 0, 300, 300),
        limits=app.extended_limits(10),
    )

    surf = pygame.Surface((50, 50))
    surf.fill("blue")
    tex = Texture.from_surface(app.renderer, surf)

    for delta in app.loop(60):
        view.move_to(app.player_pos.center)
        bbox = view.get_bounding_box()

        # instead of passing in the surface/screen + iterable of suraces
        # we pass in the renderer and an iterable of Textures

        # app.get_tiles_for_bbox returns iterable textures, if use_sdl2=True
        view.render(app.renderer, app.get_tiles_for_bbox(app.tiles, bbox))

        # sample texture
        view.render(
            app.renderer,
            [
                ((10, 10), tex),
            ],
        )

        # player
        view.render(
            app.renderer,
            [
                (
                    app.player_pos.topleft,
                    app.player_surf,
                )  # player_surf is actually a Texture (see App.__init__)
            ],
        )


if __name__ == "__main__":
    main()
