import os
import pygame
import pygame_gui
import src.chess as chess

pygame.init()

screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT))

clock = pygame.time.Clock()


def load_all_mods():
    mod_dir = os.path.join("src", "mod", "mods")
    return sorted([
        f.replace(".py", "")
        for f in os.listdir(mod_dir)
        if f.endswith(".py") and not f.startswith("__")
    ])


def main():
    mods.load_mod_config()

    all_mods = load_all_mods()

    bg = chess.build_bg()
    try:
        blurred = pygame.transform.box_blur(bg, radius=7)
    except:
        blurred = bg

 

    title = chess.text_outline("Mod Menu", font_size=90)
    title_rect = title.get_rect(center=(chess.WIDTH // 2, 80))


    all_list = pygame_gui.elements.UISelectionList(
        pygame.Rect(80, 150, 250, 350),
        item_list=all_mods,
        manager=manager,
    )

 
    active_list = pygame_gui.elements.UISelectionList(
        pygame.Rect(500, 150, 250, 350),
        item_list=mods.active_mods,
        manager=manager,
    )

    add_button = pygame_gui.elements.UIButton(
        pygame.Rect(350, 220, 120, 40),
        "Enable →",
        manager,
    )

    remove_button = pygame_gui.elements.UIButton(
        pygame.Rect(350, 280, 120, 40),
        "← Disable",
        manager,
    )

    up_button = pygame_gui.elements.UIButton(
        pygame.Rect(770, 200, 50, 40),
        "↑",
        manager,
    )

    down_button = pygame_gui.elements.UIButton(
        pygame.Rect(770, 260, 50, 40),
        "↓",
        manager,
    )

    back_button = pygame_gui.elements.UIButton(
        pygame.Rect(20, chess.HEIGHT - 70, 120, 50),
        "Back",
        manager,
    )

    selected_all = None
    selected_active = None

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == all_list:
                    selected_all = event.text
                elif event.ui_element == active_list:
                    selected_active = event.text

            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == add_button and selected_all:
                    if selected_all not in mods.active_mods:
                        mods.active_mods.append(selected_all)
                        active_list.set_item_list(mods.active_mods)

                elif event.ui_element == remove_button and selected_active:
                    if selected_active in mods.active_mods:
                        mods.active_mods.remove(selected_active)
                        active_list.set_item_list(mods.active_mods)

                elif event.ui_element == up_button and selected_active:
                    i = mods.active_mods.index(selected_active)
                    if i > 0:
                        mods.active_mods[i], mods.active_mods[i - 1] = (
                            mods.active_mods[i - 1],
                            mods.active_mods[i],
                        )
                        active_list.set_item_list(mods.active_mods)

                elif event.ui_element == down_button and selected_active:
                    i = mods.active_mods.index(selected_active)
                    if i < len(mods.active_mods) - 1:
                        mods.active_mods[i], mods.active_mods[i + 1] = (
                            mods.active_mods[i + 1],
                            mods.active_mods[i],
                        )
                        active_list.set_item_list(mods.active_mods)

                elif event.ui_element == back_button:
                    mods.save_mod_config()
                    mods.reload_modules()
                    return

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(blurred)
        screen.blit(title, title_rect)

        manager.draw_ui(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()