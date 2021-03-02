# %%
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
    args: list


commands = []
m = mouse.Controller()
k = keyboard.Controller()


class StopRecording(Exception):
    pass


def kpress(key):
    if isinstance(key, str):
        k.press(key)
    elif isinstance(key, int):
        k.press(keyboard.KeyCode(key))


def krelease(key):
    if isinstance(key, str):
        k.release(key)
    elif isinstance(key, int):
        k.release(keyboard.KeyCode(key))


def on_press(key):
    try:
        ke = key.char
    except AttributeError:
        ke = key.value.vk
    if key == keyboard.Key.esc:
        raise StopRecording()
    commands.append(Command(perf_counter(), kpress, [ke]))


def on_release(key):
    try:
        ke = key.char
    except AttributeError:
        ke = key.value.vk
    commands.append(Command(perf_counter(), krelease, [ke]))


def move(x, y):
    m.position = (x, y)


def on_move(x, y):
    commands.append(Command(perf_counter(), move, [x, y]))


def cpress(button):
    m.press(mouse.Button(button))


def crelease(button):
    m.release(mouse.Button(button))


def on_click(x, y, button, pressed):
    on_move(x, y)

    if pressed:
        commands.append(Command(perf_counter(), cpress, [button.value]))
    if not pressed:
        commands.append(Command(perf_counter(), crelease, [button.value]))


def on_scroll(x, y, dx, dy):
    on_move(x, y)
    commands.append(Command(perf_counter(), m.scroll, [dx, dy]))


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
    stop = [False]

    def on_release(key):
        if key == keyboard.Key.esc:
            stop.append(True)
            return False

    sleep(1)
    print(f"Playing {x} times...")
    with keyboard.Listener(on_release=on_release):
        for i in range(x):
            previus_time = 0
            for c in commands:
                if any(stop):
                    break
                if previus_time:
                    sleep((c.time - previus_time) * (0.01 if ignore_time else 1))
                previus_time = c.time
                c.method(*c.args)
            if any(stop):
                break
        print("Finished Playing...")


def validate():
    import sys
    import json
    import pathlib
    import os

    f = pathlib.Path(__file__).parent.absolute() / "data.json"
    mt = {
        "kpress": kpress,
        "krelease": krelease,
        "move": move,
        "cpress": cpress,
        "crelease": crelease,
        "scroll": m.scroll,
    }

    x = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if len(sys.argv) > 2 and sys.argv[2] in ("True", "true", "t"):
        ig_t = True
    elif len(sys.argv) > 2 and sys.argv[2] in ("False", "false", "f"):
        ig_t = False
    else:
        raise Exception("Invalid arg. Must be: pig 10[int] True[bool] --load=...[str] || --save=...[str]")

    if len(sys.argv) > 3 and "--load=" in sys.argv[3]:
        with open(f, "r") as file:
            data = json.load(file)
        for i, preset in enumerate(data):
            if preset.get("name") == sys.argv[3].replace("--load=", ""):
                commands.clear()
                commands.extend([
                    Command(c["time"], mt[c["method_name"]], c["method_args"])
                    for c in preset["commands"]
                ])
                play(x, ig_t)
                return

    if not len(commands):
        record()

    if len(sys.argv) > 3 and "--save=" in sys.argv[3]:
        if not os.path.exists(f):
            with open(f, "w") as file:
                json.dump([{"name": "example", "commands": []}], file)

        with open(f, "r") as file:
            data = json.load(file)

        name = sys.argv[3].replace("--save=", "")
        nd = {
            "name": name,
            "commands": [
                {
                    "time": c.time,
                    "method_name": c.method.__name__,
                    "method_args": c.args,
                }
                for c in commands
            ],
        }
        for i, preset in enumerate(data):
            if preset.get("name") == name:
                data.pop(i)
                data.append(nd)
                break
        else:
            data.append(nd)

        with open(f, "w") as file:
            json.dump(data, file)

    play(x, ig_t)


if __name__ == "__main__":
    validate()
