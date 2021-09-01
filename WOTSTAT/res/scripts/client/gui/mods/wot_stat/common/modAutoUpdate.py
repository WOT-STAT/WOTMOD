import os
import shutil
import json
import BigWorld

from helpers import getShortClientVersion
from asyncResponse import get_async


def num_game_version():
    return getShortClientVersion().split('v.')[1].strip()

def update_game_version(full_mod_name):
    gameVersion = num_game_version()
    currentMod = os.path.join(os.path.abspath('./mods/'), gameVersion, full_mod_name)

    def b(x, y):
        return '.'.join(
            [str(int(c) + 1 if i == y else 0) if i >= y else c for i, c in enumerate(x.split('.'))])

    v = [b(gameVersion, i) for i in range(len(gameVersion.split('.')))]

    absPath = os.path.abspath('./mods/')
    for i in range(len(v)):
        p = os.path.join(absPath, v[i])
        if not os.path.exists(p):
            os.mkdir(p)
        filePath = os.path.join(p, full_mod_name)
        if not os.path.exists(filePath):
            shutil.copyfile(currentMod, filePath)

# {
#     "version": "0.0.0",
#     "url": "https://example.com"
# }
def update_mod_version(url, mod_name, current_version, on_start_update=None, on_updated=None):
    def end_load_mod(res):
        global new_version

        gameVersion = num_game_version()
        newMod = os.path.join(os.path.abspath(
            './mods/'), gameVersion, mod_name + '_' + new_version + '.wotmod')
        if not os.path.exists(newMod):
            with open(newMod, "wb") as f:
                f.write(res)

        if on_updated:
            on_updated(new_version)

    def end_load_info(res):
        global new_version

        data = json.loads(res)
        new_version = data['version']
        if current_version != new_version:
            if on_start_update:
                on_start_update(new_version)
            get_async(data['url'], None, end_load_mod)

    get_async(url, None, end_load_info)
