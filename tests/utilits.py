import json
from os import listdir
from os.path import isfile, join

from config import BASE_DIR


fixtures_dir = join(BASE_DIR, 'tests/fixtures')


def loads_fixtures() -> dict:
    fixtures_data = {}
    name_files = [f for f in listdir(fixtures_dir) if isfile(join(fixtures_dir, f))]
    for name_file in name_files:
        try:

            with open(join(fixtures_dir, name_file), 'r') as file:
                raw_file = file.read()
                key = name_file.split('.')[0]
                fixtures_data[key] = json.loads(raw_file)

        except json.decoder.JSONDecodeError:
            pass

    return fixtures_data


if __name__ == "__main__":
    print(loads_fixtures())
