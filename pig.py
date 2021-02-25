from pynput import mouse, keyboard
from time import perf_counter, sleep
from dataclasses import dataclass


def print(x):
    import subprocess as s
    s.call(["notify-send", "--expire-time=1", x])


@dataclass
class Command:
    time: float
    method: callable


commands = []
m = mouse.Controller()
k = keyboard.Controller()


class StopRecording(Exception):
    pass


def on_press(key):
    if key == keyboard.Key.esc:
        raise StopRecording()
    commands.append(Command(perf_counter(), lambda: k.press(key)))


def on_release(key):
    commands.append(Command(perf_counter(), lambda: k.release(key)))


def on_move(x, y):
    def move():
        m.position = (x, y)

    commands.append(Command(perf_counter(), move))


def on_click(x, y, button, pressed):
    on_move(x, y)

    if pressed:
        commands.append(Command(perf_counter(), lambda: m.press(button)))
    if not pressed:
        commands.append(Command(perf_counter(), lambda: m.release(button)))


def on_scroll(x, y, dx, dy):
    on_move(x, y)
    commands.append(Command(perf_counter(), lambda: m.scroll(dx, dy)))


def wait_ready():
    """ Wait Esc to continue."""
    print("Waiting Esc input to start...")
    with keyboard.Listener(
        on_release=lambda key: False if key == keyboard.Key.esc else None
    ) as k_listener:
        k_listener.join()
    sleep(0.1)


def record():
    """ Start recording and stop with Esc."""
    wait_ready()

    print("Recording...")
    commands.clear()
    with keyboard.Listener(
        on_press=on_press, on_release=on_release
    ) as k_listener, mouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll
    ) as m_listener:
        try:
            k_listener.join()
            m_listener.join()
        except StopRecording:
            pass
    print("Finished recording...")


def play(x: int = 1, ignore_time=False):
    """ Reproduce the commands x times."""
    wait_ready()

    print(f"Playing {x} times...")
    for i in range(x):
        previus_time = 0
        for c in commands:
            if previus_time:
                sleep((c.time - previus_time) * (0.01 if ignore_time else 1))
            previus_time = c.time
            c.method()
    print("Finished Playing...")


if __name__ == "__main__":
    import sys
    record()
    x = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ig_t = True if len(sys.argv) > 2 else False
    play(x, ig_t)
