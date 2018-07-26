from pathlib import Path
import json

config = Path('config/')


def settings():
    with open(config / 'customcolorsettings.json') as f:
        return json.load(f)


def save_settings(settings):
    with open(config / 'customcolorsettings.json', 'w') as f:
        f.write(json.dumps(settings, indent=4, sort_keys=True))


def change_wizard(loc):
    editmode = input('"rgb" for color change, "bri" for brightness change: ')
    if editmode in ['rgb', 'bri']:
        if editmode == 'rgb':
            rgb = input('Enter 3 rgb values(1-255 inclusive) separated by dashes(-): ').split('-')
            if len(rgb) != 3:
                print('Exactly 3 values separated by dashes expected.')
                return None
            try:
                rgb = [int(x) for x in rgb]
                for x in rgb:
                    if not 1 <= x <= 255:
                        raise ValueError
            except ValueError:
                print("All 3 values must be valid Integers 1 to 255 inclusive.")
                return None
            loc.update({'rgb': rgb})
        elif editmode == 'bri':
            bri = input('Enter a value 1 to 255 inclusive, 255 being the brightest: ')
            try:
                bri = int(bri)
                if not 1 <= bri <= 255:
                    raise ValueError
            except ValueError:
                print("Value must be a valid Integer 1 to 255 inclusive.")
                return None
            loc.update({'bri': bri})
    else:
        print('Invalid Command')
        return None
    return loc


def change_settings(loc):
    change = change_wizard(loc)
    if change:
        loc.update(change)


current = settings()

while True:
    option = input(
        '"change" to change settings,\n'
        '"save" to save changes,\n'
        '"revert" to revert changes,\n'
        '"quit" to quit app: ')
    if option == 'quit':
        break
    elif option == 'change':
        mode = input('"custom" to change a specific light. "default" to change default settings: ')
        if mode in ['custom', 'default']:
            if mode == 'custom':
                ip = input('Bridge IP: ')
                if ip not in current['custom'].keys():
                    current['custom'].update({ip: {}})
                light = input('Light Number: ')
                if light not in current['custom'][ip].keys():
                    current['custom'][ip].update({light: {}})
                change_settings(current['custom'][ip][light])
            elif mode == 'default':
                change_settings(current['default'])
        else:
            print('Invalid Command')
    elif option == 'save':
        save_settings(current)
        print('Changes Saved')
    elif option == 'revert':
        current = settings()
        print('Changes Reverted')
    else:
        print('Invalid Command')
