# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import itertools

from .base import Num2Word_Base
from .utils import get_digits, splitbyx

ZERO = ('zero', 'zerowy')

ONES = {
    1: ('jeden', 'pierwszy'),
    2: ('dwa', 'drugi'),
    3: ('trzy', 'trzeci'),
    4: ('cztery', 'czwarty'),
    5: ('pięć', 'piąty'),
    6: ('sześć', 'szósty'),
    7: ('siedem', 'siódmy'),
    8: ('osiem', 'ósmy'),
    9: ('dziewięć', 'dziewiąty'),
}

TENS = {
    0: ('dziesięć', 'dziesiąty'),
    1: ('jedenaście', 'jedenasty'),
    2: ('dwanaście', 'dwunasty'),
    3: ('trzynaście', 'trzynasty'),
    4: ('czternaście', 'czternasty'),
    5: ('piętnaście', 'pietnasty'),
    6: ('szesnaście', 'szesnasty'),
    7: ('siedemnaście', 'siedemnasty'),
    8: ('osiemnaście', 'osiemnasty'),
    9: ('dziewiętnaście', 'dziewietnasty'),
}

TWENTIES = {
    2: ('dwadzieścia', 'dwudziesty'),
    3: ('trzydzieści', 'trzydziesty'),
    4: ('czterdzieści', 'czterdziesty'),
    5: ('pięćdziesiąt', 'pięćdziesiąty'),
    6: ('sześćdziesiąt', 'sześćdziesiąty'),
    7: ('siedemdziesiąt', 'siedemdziesiąty'),
    8: ('osiemdziesiąt', 'osiemdziesiąty'),
    9: ('dziewięćdzisiąt', 'dziewięćdziesiąty'),
}

HUNDREDS = {
    1: ('sto', 'sto'),
    2: ('dwieście', 'dwieście'),
    3: ('trzysta', 'trzysta'),
    4: ('czterysta', 'czterysta'),
    5: ('pięćset', 'pięćset'),
    6: ('sześćset', 'sześćset'),
    7: ('siedemset', 'siedemset'),
    8: ('osiemset', 'osiemset'),
    9: ('dziewięćset', 'dziewięćset'),
}

THOUSANDS = {
    1: ('tysiąc', 'tysiące', 'tysięcy',),  # 10^3
}

prefixes = (   # 10^(6*x)
    "mi",      # 10^6
    "bi",      # 10^12
    "try",     # 10^18
    "kwadry",  # 10^24
    "kwinty",  # 10^30
    "seksty",  # 10^36
    "septy",   # 10^42
    "okty",    # 10^48
    "nony",    # 10^54
    "decy"     # 10^60
)
suffixes = ("lion", "liard")  # 10^x or 10^(x+3)

for idx, (p, s) in enumerate(itertools.product(prefixes, suffixes)):
    name = p + s
    THOUSANDS[idx+2] = (name, name + 'y', name + 'ów')


class Num2Word_PL(Num2Word_Base):
    CURRENCY_FORMS = {
        'PLN': (
            ('złoty', 'złote', 'złotych'), ('grosz', 'grosze', 'groszy')
        ),
        'EUR': (
            ('euro', 'euro', 'euro'), ('cent', 'centy', 'centów')
        ),
    }

    def setup(self):
        self.negword = "minus"
        self.pointword = "przecinek"

    def to_cardinal(self, number):
        n = str(number).replace(',', '.')
        if '.' in n:
            left, right = n.split('.')
            return u'%s %s %s' % (
                self._int2word(int(left), 0),
                self.pointword,
                self._int2word(int(right), 0)
            )
        else:
            return self._int2word(int(n), 0)

    def pluralize(self, n, forms):
        if n == 1:
            form = 0
        elif 5 > n % 10 > 1 and (n % 100 < 10 or n % 100 > 20):
            form = 1
        else:
            form = 2
        return forms[form]

    def to_ordinal(self, number):
        n = str(number).replace(',', '.')
        if '.' in n:
            raise NotImplementedError()
        else:
            return self._int2word(int(n), 1)

    def _int2word(self, n, t):
        if n == 0:
            return ZERO[t]

        words = []
        chunks = list(splitbyx(str(n), 3))
        i = len(chunks)
        for x in chunks:
            i -= 1

            if x == 0:
                continue

            n1, n2, n3 = get_digits(x)

            if n3 > 0:
                words.append(HUNDREDS[n3][t])

            if n2 > 1:
                words.append(TWENTIES[n2][t])

            if n2 == 1:
                words.append(TENS[n1][t])
            elif n1 > 0 and not (i > 0 and x == 1):
                words.append(ONES[n1][t])

            if i > 0:
                words.append(self.pluralize(x, THOUSANDS[i]))

        return ' '.join(words)
