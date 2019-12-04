from gensim.models import KeyedVectors
import requests
from num_to_words.index import num2words
from collections import OrderedDict
from joblib import Memory
import os
TAGGING_SERVER_URL = os.getenv("TAGGING_SERVER_URL")

memory = Memory('./cache', verbose=0)

print('Loading word2vec...')
word_vectors = KeyedVectors.load_word2vec_format('./polish.w2v.txt', binary=False)
print('Finished loading word2vec...')

command_map = {
    "on": ['włączyć', 'włączać', 'uruchomić', 'załączyć', 'cyknąć'],
    "off": ['wyłączyć', 'wyłączać', 'zgasić'],
    "toggle": ['zmienić', 'zmieniać'],
    "ch": ['kanał', 'stacja'],
    "vol": ['głośność', 'pogłośnić', 'ściszyć'],
    "color": ['kolor', 'barwa', 'odcień'],
    "time": ['czas', 'godzina', 'data', 'moment', 'ustawić'],
    "up": ['podnieść', 'zwiększyć', 'podwyższyć', 'odsłonić', 'góra', 'głośniej'],
    "down": ['opuścić', 'zmniejszyć','obniżyć', 'zasłonić', 'dół', 'ciszej'],
    "stop": ['zatrzymać', 'zatrzymywać', 'zastopować', 'stop'],
    "bright": ['jasność', 'jaskrawość'],
    "speed": ['szybkość', 'prędkość']
}

command_value_map = {
    "next": ['następny', 'kolejny'],
    "prev": ['poprzedni', 'wcześniejszy'],
    "up": ['głośniej', 'pogłośnić'],
    "down": ['ciszej', 'ściszyć'],
    "warm": ['ciepły', 'gorący'],
    "cold": ['zimny', 'chłodny'],
    "white": ['biały'],
    "black": ['czarny'],
    "green": ['zielony'],
    "blue": ['niebieski'],
    "red": ['czerwony'],
    "yellow": ['żółty'],
    "purple": ['fioletowy'],
    "orange": ['pomarańczowy'],
    "fast": ['szybko', 'szybki'],
    "slow": ['wolno', 'wolny']
}

pos_map = {
    "subst": "noun",
    "depr": "noun",
    "ger": "noun",
    "brev": "noun",

    "adj": "adj",
    "adja": "adj",
    "adjp": "adj",
    "adjc": "adj",

    "fin": "verb",
    "bedzie": "verb",
    "praet": "verb",
    "impt": "verb",
    "inf": "verb",
    "pcon": "verb",
    "pant": "verb",
    "imps": "verb",
    "winien": "verb",
    "pred": "adv",
    "pact": "verb",
    "ppas": "verb",

    "num": "num",
    "numcol": "num",

    "adv": "adv",

    "ppron12": "pron",
    "ppron3": "pron",
    "siebie": "pron",

    "prep": "prep",

    "conj": "conj",
    "comp": "conj",

    "interj": "interj",
    "burk": "burk",

    "qub": "qub",

    "xxx": "xxx",

    "interp": "ign",
    "aglt": "ign",
    "ign": "ign"
}
post_list = pos_map.keys()

device_map = {
    'oświetlenie': ['światło'],
    "górne": ['główne'],
    'budzik': ['budzenie']
}

def check_if_simple(command):
    return 'ranges' not in command and 'values' not in command


def lev_edits1(word):
    letters = 'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return deletes + transposes + replaces + inserts


def lev_edits2(word):
    return [e2 for e1 in lev_edits1(word) for e2 in lev_edits1(e1)]


def levenshtein(word):
    return [word] + lev_edits1(word) #+ lev_edits2(word)


def calculate_compliance(rn, matching_words):
    s = 0
    for mw in matching_words:
        if mw in rn:
            s += 1
        elif len(mw) > 3:
            if any([mwv in rn for mwv in lev_edits1(mw)]):
                s += (len(mw) - 1) / len(mw)
            elif any([mwv in rn for mwv in lev_edits2(mw)]):
                s += (len(mw) - 2) / len(mw)

    return s


def tag_sentence(sentence):
    r = requests.post(f'{TAGGING_SERVER_URL}:9200', data=sentence.lower().encode('utf-8'))
    lemmas = [(c.split('\t')[1], c.split('\t')[2].split(':')[0]) for c in
              [line for line in r.content.decode().split('\n') if len(line) > 0][1::2]]
    return lemmas


def lemmatize_sentence(sentence, lev=True, wv=word_vectors, add_pos=True):
    def find_word_in_word_vectors(word, pos):
        lev_words = []
        for w in (levenshtein(word) if lev and len(word) > 3 else [word]):
            if add_pos:
                for pos in set(pos_map.values()):
                    wv_word = f'{w}::{pos}'
                    if wv_word in wv:
                        lev_words.append(wv_word)
            else:
                if w in wv:
                    lev_words.append(w)

        return lev_words

    lemmas = [find_word_in_word_vectors(word, pos) for (word, pos) in tag_sentence(sentence)]
    return lemmas


def find_room_setup(_configuration):
    _co_rooms = _configuration["rooms"]
    _co_rooms_names = [r['name'] for r in _co_rooms]
    _co_rooms_names = [lemmatize_sentence(room_name, lev=False) for room_name in _co_rooms_names]
    _co_rooms_names = [[l[0].split('::')[0] for l in s] for s in _co_rooms_names]
    _co_rooms_names_dict = [w for room_name in _co_rooms_names for w in room_name]
    return _co_rooms, _co_rooms_names, _co_rooms_names_dict


def find_room(_in_sentence, _co_rooms, _co_rooms_names, _co_rooms_names_dict):
    _in_rooms = [l for l in _in_sentence if l in _co_rooms_names_dict]

    _out_rooms = [(r, calculate_compliance(_co_rooms_names[i], _in_rooms)) for i, r in enumerate(_co_rooms)]
    _out_rooms.sort(key=lambda x: x[1], reverse=True)

    _max_compliance = max([r[1] for r in _out_rooms])
    _out_rooms = [r[0] for r in _out_rooms if _max_compliance > 1e-5 > _max_compliance - r[1]]
    _out_rooms = _out_rooms if len(_out_rooms) > 0 else _co_rooms
    print(f'Possible rooms: {", ".join([r["name"] for r in _out_rooms])}')
    return _out_rooms


def find_device_setup(_configuration):
    _co_all_devices_in_room_map = {}
    _co_all_devices_dict = []

    for r in _configuration['rooms']:
        _co_room_devices = []
        for d in r['devices']:
            _co_room_devices.append(d)
            _co_d_name = d['name'].lower()
            co_d_spl = _co_d_name.split(' ')
            for dm in device_map:
                if dm in co_d_spl:
                    for dmv in device_map[dm]:
                        _co_room_devices.append(dict(d, name=_co_d_name.replace(dm, dmv)))
        _co_room_devices_names = [lemmatize_sentence(dn, lev=False) for dn in [d['name'] for d in _co_room_devices]]
        _co_room_devices_names = [[l[0].split('::')[0] for l in s] for s in _co_room_devices_names]
        _co_room_devices_names_dict = [w for dn in _co_room_devices_names for w in dn]
        _co_all_devices_dict += _co_room_devices_names_dict
        _co_all_devices_in_room_map[r['name']] = (_co_room_devices, _co_room_devices_names, _co_room_devices_names_dict)

    return _co_all_devices_in_room_map, _co_all_devices_dict


def find_device(_in_sentence, _co_all_devices_in_room_map, _out_rooms):
    _co_all_devices_in_room = [_co_all_devices_in_room_map[r['name']] for r in _out_rooms]
    _co_all_devices = [d for r in _co_all_devices_in_room for d in r[0]]
    _co_devices_names = [dn for r in _co_all_devices_in_room for dn in r[1]]
    _co_devices_names_dict = [dnd for r in _co_all_devices_in_room for dnd in r[2]]

    _in_devices = [l for l in _in_sentence if l in _co_devices_names_dict]
    print(_in_sentence)

    _out_devices = [(r, calculate_compliance(_co_devices_names[i], _in_devices)) for i, r in
                    enumerate(_co_all_devices)]
    _out_devices.sort(key=lambda d: d[1], reverse=True)

    _max_compliance = max([d[1] for d in _out_devices])
    _out_devices = [d[0] for d in _out_devices if _max_compliance > 1e-5 > _max_compliance - d[1]]

    if len(_out_devices) == 0:
        return None

    _min_device_name_len = min([len(d['name'].split(' ')) for d in _out_devices])
    _out_devices = [d for d in _out_devices if len(d['name'].split(' ')) <= _min_device_name_len]

    if len(_out_devices) == 0:
        return None

    _out_devices_ids = list(OrderedDict.fromkeys([fdd['id'] for fdd in _out_devices]))
    _out_devices = [[d for d in _co_all_devices if d['id'] == di][0] for di in _out_devices_ids]
    print(f'Possible devices: {", ".join([d["name"] for d in _out_devices])}')
    return _out_devices


def find_command_setup(_configuration):
    _co_all_commands_for_device_map = {}
    _co_all_commands_dict = []

    for r in _configuration['rooms']:
        for d in r['devices']:
            _co_device_commands = d['commands']
            _co_device_commands_ids = [c['id'] for c in _co_device_commands]
            _co_device_commands_names = [command_map[c_id] for c_id in _co_device_commands_ids]

            _co_all_commands_dict += [w for c in _co_device_commands_names for w in c]

            _co_all_commands_for_device_map[d['id']] = (
            _co_device_commands, _co_device_commands_ids, _co_device_commands_names)

    _co_all_commands_dict = list(set(_co_all_commands_dict))
    _co_all_commands_dict = [lemmatize_sentence(c, lev=False) for c in _co_all_commands_dict]
    _co_all_commands_dict = [l[0][0].split('::')[0] for l in _co_all_commands_dict]

    return _co_all_commands_for_device_map, _co_all_commands_dict


def find_command(_in_sentence, _co_all_commands_for_device_map, _out_devices):
    _co_all_commands_in_devices = [_co_all_commands_for_device_map[d['id']] for d in _out_devices]
    _co_all_commands = [c for d in _co_all_commands_in_devices for c in d[0]]
    _co_all_commands_ids = [c for d in _co_all_commands_in_devices for c in d[1]]
    _co_all_commands_names = [c for d in _co_all_commands_in_devices for c in d[2]]

    _co_flat_commands_names = [c for commands_names in _co_all_commands_names for c in commands_names]
    _co_flat_commands_names = [lemmatize_sentence(command_name, lev=False) for command_name in _co_flat_commands_names]
    _co_flat_commands_names = [[l[0].split('::')[0] for l in s] for s in _co_flat_commands_names]
    _co_commands_names_dict = [w for cn in _co_flat_commands_names for w in cn]

    _in_commands = [l for l in _in_sentence if l in _co_commands_names_dict]

    _out_commands = [(c,
                      max([calculate_compliance([fc_cmd_name_var], _in_commands) for fc_cmd_name_var in
                           _co_all_commands_names[i]])
                      ) for i, c in enumerate(_co_all_commands)]

    _out_commands.sort(key=lambda c: c[1], reverse=True)

    _max_compliance = max([c[1] for c in _out_commands])
    _out_commands = [c[0] for c in _out_commands if _max_compliance > 1e-5 > _max_compliance - c[1]]

    if len(_out_commands) == 0:
        _out_commands = _co_all_commands

    return _out_commands


def find_command_value_setup(_configuration):
    def get_cv_values_for_ranges(_ranges):
        if isinstance(_ranges, list):
            [v1s, v2s] = [get_cv_values_for_ranges(r) for r in _ranges]
            v2s = v2s[0::30]
            return [[str(v1), f'{int(v2):02d}'] for v1 in v1s for v2 in v2s]

        _result = [str(n) for n in range(int(_ranges['min']), int(_ranges['max'] + 1))]
        if 'iteration' in _ranges:
            _result += [_ranges['iteration']['incr'], _ranges['iteration']['decr']]
        return _result

    def find_command_values(cv_command):
        if 'values' in cv_command:
            cv_ids = cv_command['values']
            cv_values = [command_value_map[v] if v in command_value_map else [v] for v in cv_ids]
            cv_values = [[x[0].split('::')[0] for w in v for x in lemmatize_sentence(w, lev=False)] for v in cv_values]
            return cv_ids, cv_values
        elif 'ranges' in cv_command:
            _co_ranges = cv_command['ranges']
            cv_values = get_cv_values_for_ranges(_co_ranges)
            cv_ids = [cv_id for cv_id in cv_values]
            cv_values = [v if isinstance(v, list) else [v, num2words(v, lang='pl'),
                                                        num2words(v, lang='pl', to='ordinal')] if v.isdigit() else
            command_value_map[v] if v in command_value_map else [v] for v in cv_values]
            cv_values = [[x[0].split('::')[0] for w in v for x in lemmatize_sentence(w, lev=False) if len(x) > 0] for v
                         in cv_values]
            return cv_ids, cv_values
        else:
            return [], []

    _co_value_for_command_map = {}
    _co_command_values_dict = []
    for r in _configuration['rooms']:
        for d in r['devices']:
            for c in d['commands']:
                if check_if_simple(c):
                    continue

                c_id = c['id']
                cv_ids, cv_values = find_command_values(c)
                if c_id in _co_value_for_command_map:
                    _co_value_for_command_map[c_id] = (
                        _co_value_for_command_map[c_id][0] + [cv_id for cv_id in cv_ids if
                                                              cv_id not in _co_value_for_command_map[c_id][0]],
                        _co_value_for_command_map[c_id][1] + [cv_val for cv_val in cv_values if
                                                              cv_val not in _co_value_for_command_map[c_id][1]]
                    )
                else:
                    _co_value_for_command_map[c_id] = (cv_ids, cv_values)

                _co_command_values_dict += [w for v in cv_values for w in v]

    _co_command_values_dict = list(set(_co_command_values_dict))
    return _co_value_for_command_map, _co_command_values_dict


def find_command_value(_in_sentence, _co_value_for_command_map, cv_commands):
    def find_specific_command_value(cv_command):
        co_cv_ids, co_cv_values = _co_value_for_command_map[cv_command['id']]
        co_cv_values = [(co_cv_ids[i], calculate_compliance(v, _in_sentence)) for i, v in enumerate(co_cv_values)]
        co_cv_values.sort(key=lambda x: x[1], reverse=True)
        co_cv_values = [c[0] for c in co_cv_values if c[1] > 1e-5]
        if len(co_cv_values) == 0:
            return None

        return ':'.join(co_cv_values[0]) if isinstance(co_cv_values[0], list) else co_cv_values[0]

    results = [(i, '' if check_if_simple(c) else find_specific_command_value(c)) for i, c in enumerate(cv_commands)]
    results = [r for r in results if r[1] is not None]
    if len(results) == 1:
        return cv_commands[results[0][0]], results[0][1] if len(results[0][1]) > 0 else None
    elif len(results) > 1:
        more_specific_results = [r for r in results if len(r[1]) > 0]
        if len(more_specific_results) == 1:
            return cv_commands[more_specific_results[0][0]], more_specific_results[0][1]
        elif len(more_specific_results) == 0:
            default_commands = [cv_c for i, cv_c in enumerate(cv_commands) if cv_c["default"]]
            return default_commands[0] if len(default_commands) > 0 else \
                       cv_commands[results[0][0]], results[0][1] if len(results[0][1]) > 0 else None

    return None, None


def create_result(out_rooms, out_devices, out_command, out_command_value):
    if out_command is None:
        return 'error'

    out_devices = [crd for crd in out_devices if out_command in crd['commands']]
    if len(out_devices) >= 1:
        out_device = out_devices[0]
    else:
        return 'error'

    out_rooms = [crr for crr in out_rooms if out_device in crr['devices']]
    if len(out_rooms) == 1:
        [out_room] = out_rooms
    else:
        return 'error'

    print(f'Room: {out_room["name"]}')
    print(f'Device: {out_device["name"]}')
    if check_if_simple(out_command):
        print(f'Command: {out_command["id"]}')
        result = f'{out_command["id"]} {out_device["id"]}'
    else:
        print(f'Command: {out_command["id"]}')
        print(f'Command value: {out_command_value}')
        result = f'set {out_device["id"]} {out_command["id"]} {out_command_value}'

    return result


def resolve_command(rc_transcript, r_setup, d_setup, c_setup, cv_setup, all_dict):
    rc_transcript = ' '.join([num2words(w, lang='pl') if w.isdigit() else w for w in rc_transcript.split(' ')])
    _in_sentence = lemmatize_sentence(rc_transcript, wv=all_dict, add_pos=False)
    _in_sentence = [w[0] for w in _in_sentence if len(w) > 0]

    _co_rooms, _co_rooms_names, _co_rooms_names_dict = r_setup
    _out_rooms = find_room(_in_sentence, _co_rooms, _co_rooms_names, _co_rooms_names_dict)

    _co_all_devices_in_room_map, _ = d_setup
    _out_devices = find_device(_in_sentence, _co_all_devices_in_room_map, _out_rooms)

    if _out_devices is None:
        return 'error'

    _co_all_commands_for_device_map, _ = c_setup
    _out_commands = find_command(_in_sentence, _co_all_commands_for_device_map, _out_devices)

    print(f'Possible commands: {", ".join([c["id"] if "id" in c else c for c in _out_commands])}')

    if len(_out_commands) == 1:
        [_out_command] = _out_commands
        if check_if_simple(_out_command):
            return create_result(_out_rooms, _out_devices, _out_command, None)

    _co_value_for_command_map, _ = cv_setup
    _out_command, _out_command_value = find_command_value(_in_sentence, _co_value_for_command_map, _out_commands)
    if _out_command is None:
        return 'error'

    return create_result(_out_rooms, _out_devices, _out_command, _out_command_value)

resolve_command = memory.cache(resolve_command)
