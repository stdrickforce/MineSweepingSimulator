#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: stdrickforce (Tengyuan Fan)
# Email: <stdrickforce@gmail.com> <fantengyuan@baixing.com>

# import time

from vskfz.main import Simulator

cases = {
    'basic': (9, 9, 10),
    'medium': (16, 16, 40),
    'advanced': (16, 30, 99),
}

times = 1000

res = {}

for name, args in cases.items():
    t = [0, 0]
    for i in range(times):
        s = Simulator(*args, stdout=False)
        t[s.run()] += 1
    print(t)
    res[name] = {
        'win': t[1],
        'lose': t[0],
    }
print(res)
