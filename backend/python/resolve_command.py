from gensim.models import KeyedVectors
import requests
from num_to_words.index import num2words
import operator
from collections import OrderedDict
from joblib import Memory

print('Starting resolution module...')
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
    'budzik': ['budzenie']
}

print('Loading word2vec...')
word_vectors = KeyedVectors.load_word2vec_format('./polish.w2v.txt', binary=False)
print('Finished loading word2vec...')

print('Initializing cache...')
lev_edits1_cache = {}
lev_edits2_cache = {}
levenshtein_cache = {}
resolve_command_cache = {}
print('Finished initializing cache...')

print('Resolution module ready...')


def lev_edits1(word):
    letters = 'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return deletes + transposes + replaces + inserts


lev_edits1 = Memory('./cache/lev_edits1', verbose=0).cache(lev_edits1)


def lev_edits2(word):
    return [e2 for e1 in lev_edits1(word) for e2 in lev_edits1(e1)]


lev_edits2 = Memory('./cache/lev_edits2', verbose=0).cache(lev_edits2)


def levenshtein(word):
    return [word] + lev_edits1(word) + lev_edits2(word)


levenshtein = Memory('./cache/levenshtein', verbose=0).cache(levenshtein)


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


def lemmatize_sentence(sentence, lev=True, wv=word_vectors):
    def find_word_in_word_vectors(word, pos):
        lev_words = []
        for w in (levenshtein(word) if lev and len(word) > 3 else [word]):
            wv_word = f'{w}::{pos}'
            if wv_word in wv:
                lev_words.append(wv_word)
            wv_word = f'{w}::{pos_map[pos]}'
            if wv_word in wv:
                lev_words.append(wv_word)
            for pos in set(pos_map.values()):
                wv_word = f'{w}::{pos}'
                if wv_word in wv:
                    lev_words.append(wv_word)

        return lev_words

    r = requests.post('http://192.168.99.100:9200', data=sentence.lower().encode('utf-8'))

    lemmas = [(c.split('\t')[1], c.split('\t')[2].split(':')[0]) for c in
              [line for line in r.content.decode().split('\n') if len(line) > 0][1::2]]
    lemmas = [find_word_in_word_vectors(word, pos) for (word, pos) in lemmas]
    return lemmas


def find_room_setup(_configuration):
    _rooms = _configuration["rooms"]
    _rooms_names = [list(map(operator.itemgetter(0), lemmatize_sentence(room_name, lev=False))) for room_name in [r['name'] for r in _rooms]]
    _rooms_names_dict = [w for room_name in _rooms_names for w in room_name]
    _max_room_name_len = max([len(r) for r in _rooms_names])
    return _rooms, _rooms_names, _rooms_names_dict, _max_room_name_len


def find_room(_sentence, _rooms, _rooms_names, _rooms_names_dict, _max_room_name_len):
    room_name = list(map(operator.itemgetter(0), [p for p in lemmatize_sentence(_sentence, lev=False, wv=_rooms_names_dict) if len(p) > 0]))
    fr_rooms = [(r, calculate_compliance(_rooms_names[i], room_name) / _max_room_name_len) for i, r in enumerate(_rooms)]
    fr_rooms.sort(key=lambda x: x[1], reverse=True)

    max_compliance = max([r[1] for r in fr_rooms])
    filtered_fr_rooms = [r[0] for r in fr_rooms if max_compliance > 1e-5 > max_compliance - r[1]]
    result = filtered_fr_rooms if len(filtered_fr_rooms) > 0 else _rooms
    print(f'Possible rooms: {", ".join([r["name"] for r in result])}')
    return result


def find_device_setup(_configuration):
    _all_devices_in_room_map = {}
    for r in _configuration['rooms']:
        _room_devices = []
        for d in r['devices']:
            _room_devices.append(d)
            d_name = d['name'].lower()
            d_spl = d_name.split(' ')
            for dm in device_map:
                if dm in d_spl:
                    for dmv in device_map[dm]:
                        _room_devices.append(dict(d, name=d_name.replace(dm, dmv)))
        _room_devices_names = [list(map(operator.itemgetter(0), lemmatize_sentence(dn, lev=False))) for dn in
                               [d['name'] for d in _room_devices]]
        _room_devices_names_dict = [w for dn in _room_devices_names for w in dn]
        _all_devices_in_room_map[r['name']] = (_room_devices, _room_devices_names, _room_devices_names_dict)

    return _all_devices_in_room_map


def find_device(_sentence, _all_devices_in_room_map, _rooms):
    _all_devices_in_room = [_all_devices_in_room_map[r['name']] for r in _rooms]
    _all_devices = [d for r in _all_devices_in_room for d in r[0]]
    _devices_names = [dn for r in _all_devices_in_room for dn in r[1]]
    _devices_names_dict = [dnd for r in _all_devices_in_room for dnd in r[2]]

    _device_name_in_sentence = list(
        map(operator.itemgetter(0), [p for p in lemmatize_sentence(_sentence, wv=_devices_names_dict) if len(p) > 0]))
    _devices_with_compl = [(d, calculate_compliance(_devices_names[i], _device_name_in_sentence)) for i, d in
                           enumerate(_all_devices)]
    _devices_with_compl.sort(key=lambda d: d[1], reverse=True)
    _max_compliance = max([d[1] for d in _devices_with_compl])
    _devices = [d[0] for d in _devices_with_compl if _max_compliance > 1e-5 > _max_compliance - d[1]]

    if len(_devices) == 0:
        return None

    _min_device_name_len = min([len(d['name'].split(' ')) for d in _devices])
    _devices = [d for d in _devices if len(d['name'].split(' ')) <= _min_device_name_len]

    if len(_devices) == 0:
        return None

    _devices_ids = list(OrderedDict.fromkeys([fdd['id'] for fdd in _devices]))
    _devices = [[d for d in _all_devices if d['id'] == di][0] for di in _devices_ids]
    print(f'Possible devices: {", ".join([d["name"] for d in _devices])}')
    return _devices


def find_command(fc_configuration, fc_sentence, fc_devices):
    def find_command_id(command):
        if type(command) is str:
            return command
        if type(command) is dict:
            return command['id']

        return None

    commands = [c for fc_device in fc_devices for c in fc_device['commands']]
    fc_commands_ids = [find_command_id(c) for c in commands]
    fc_commands_names = [command_map[c_id] for c_id in fc_commands_ids]
    commands_names = [c for commands_names in fc_commands_names for c in commands_names]
    commands_names = [list(map(operator.itemgetter(0), lemmatize_sentence(command_name, lev=False))) for command_name in
                      commands_names]
    commands_name_dict = [w for command_name in commands_names for w in command_name]

    command_name = list(
        map(operator.itemgetter(0), [p for p in lemmatize_sentence(fc_sentence, wv=commands_name_dict) if len(p) > 0]))
    command_name = [c.split('::')[0] for c in command_name]
    fc_commands = [
        (c, max([calculate_compliance([fc_cmd_name_var], command_name) for fc_cmd_name_var in fc_commands_names[i]]))
        for i, c in enumerate(commands)]
    fc_commands.sort(key=lambda x: x[1], reverse=True)

    max_compliance = max([c[1] for c in fc_commands])
    fc_commands = [c[0] for c in fc_commands if max_compliance > 1e-5 > max_compliance - c[1]]
    if len(fc_commands) == 0:
        fc_commands = commands

    return fc_commands


def find_command_value(cv_configuration, cv_sentence, cv_commands):
    def get_cv_values_for_ranges(ranges):
        if isinstance(ranges, list):
            [v1s, v2s] = [get_cv_values_for_ranges(r) for r in ranges]
            return [[str(v1), f'{int(v2):02d}'] for v1 in v1s for v2 in v2s]

        result = [str(n) for n in range(int(ranges['min']), int(ranges['max'] + 1))]
        if 'iteration' in ranges:
            result += [ranges['iteration']['incr'], ranges['iteration']['decr']]
        return result

    def find_specific_command_value(cv_command):
        if 'values' in cv_command:
            cv_values = cv_command['values']
        elif 'ranges' in cv_command:
            ranges = cv_command['ranges']
            cv_values = get_cv_values_for_ranges(ranges)
            if cv_values is None:
                return None
        else:
            return None

        cv_ids = [id for id in cv_values]
        cv_values = [v if isinstance(v, list) else [v, num2words(v, lang='pl'),
                                                    num2words(v, lang='pl', to='ordinal')] if v.isdigit() else
        command_value_map[v] if v in command_value_map else [v] for v in cv_values]
        cv_values = [[x.split('::')[0] for x in list(
            map(operator.itemgetter(0), [p for p in lemmatize_sentence(' '.join(cv_value), lev=False) if len(p) > 0]))]
                     for cv_value in cv_values]

        cv_lem_sentence = list(map(operator.itemgetter(0), [p for p in lemmatize_sentence(cv_sentence) if len(p) > 0]))
        cv_lem_sentence = [v.split('::')[0] for v in cv_lem_sentence]
        cv_values = [(cv_ids[i], calculate_compliance(v, cv_lem_sentence)) for i, v in enumerate(cv_values)]
        cv_values.sort(key=lambda x: x[1], reverse=True)

        cv_values = [c[0] for c in cv_values if c[1] > 1e-5]
        if len(cv_values) == 0:
            return None

        return ':'.join(cv_values[0]) if isinstance(cv_values[0], list) else cv_values[0]

    results = [(i, '' if type(c) is str else find_specific_command_value(c)) for i, c in enumerate(cv_commands)]
    results = [r for r in results if r[1] is not None]
    if len(results) == 1:
        return cv_commands[results[0][0]], results[0][1] if len(results[0][1]) > 0 else None
    elif len(results) > 1:
        more_specific_results = [r for r in results if len(r[1]) > 0]
        if len(more_specific_results) == 1:
            return cv_commands[more_specific_results[0][0]], more_specific_results[0][1]
        elif len(more_specific_results) == 0:
            return cv_commands[results[0][0]], None

    return None, None


def create_result(cr_rooms, cr_devices, cr_command, cr_command_value):
    if cr_command is None:
        return 'error'

    cr_devices = [crd for crd in cr_devices if cr_command in crd['commands']]
    if len(cr_devices) >= 1:
        cr_device = cr_devices[0]
    else:
        return 'error'

    cr_rooms = [crr for crr in cr_rooms if cr_device in crr['devices']]
    if len(cr_rooms) == 1:
        [cr_room] = cr_rooms
    else:
        return 'error'

    print(f'Room: {cr_room["name"]}')
    print(f'Device: {cr_device["name"]}')
    if isinstance(cr_command, str):
        print(f'Command: {cr_command}')
        result = f'{cr_command} {cr_device["id"]}'
    else:
        print(f'Command: {cr_command["id"]}')
        print(f'Command value: {cr_command_value}')
        result = f'set {cr_device["id"]} {cr_command["id"]} {cr_command_value}'

    return result


def resolve_command(rc_configuration, rc_transcript, r_setup, d_setup):
    _rc_transcript = ' '.join([num2words(w, lang='pl') if w.isdigit() else w for w in rc_transcript.split(' ')])

    _rooms, _rooms_names, _rooms_names_dict, _max_room_name_len = r_setup
    _rc_rooms = find_room(_rc_transcript, _rooms, _rooms_names, _rooms_names_dict, _max_room_name_len)

    _all_devices_in_room_map = d_setup
    _rc_devices = find_device(_rc_transcript, _all_devices_in_room_map, _rc_rooms)
    if _rc_devices is None:
        return 'error'

    _rc_commands = find_command(rc_configuration, _rc_transcript, _rc_devices)
    print(f'Possible commands: {", ".join([c["id"] if "id" in c else c for c in _rc_commands])}')

    if len(_rc_commands) == 1:
        [_rc_command] = _rc_commands
        if type(_rc_command) is str:
            return create_result(_rc_rooms, _rc_devices, _rc_command, None)

    _rc_command, _rc_command_value = find_command_value(rc_configuration, _rc_transcript, _rc_commands)
    if _rc_command is None:
        return 'error'

    return create_result(_rc_rooms, _rc_devices, _rc_command, _rc_command_value)


resolve_command = Memory('./cache/resolve_command', verbose=0).cache(resolve_command)
