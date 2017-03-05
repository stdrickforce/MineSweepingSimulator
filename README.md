# MineSweepingSimulator
A python mine sweeping simulator

## Installation

```bash
python setup.py install
```

## Run it!

For example, if you want to simulate a 9x9 map with 12 mines.

```bash
mine-sweeping 9 9 12
```

## Use it.

you can use it by following code. (If you want to do some research)

```python
from msim.main import Simulator

s = Simulator(height=9, width=9, mine_count=10, stdout=False)

# res will be True if the simulated game winned
res = s.run()

```
