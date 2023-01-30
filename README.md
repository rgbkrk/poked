# PokéDEX

This package was put together as a teaching tool for working with data. The PokéAPI provides the core data for this package.

To be friendly to the PokéAPI, this package caches queries.

## Installation

```bash
pip install poked
```

## Usage

```python
In [1]: import poked

In [2]: poked.list_pokemon()
Out[2]: <coroutine object list_pokemon at 0x106541440>

In [3]: await poked.list_pokemon()
Out[3]:
                         name  base_experience  height  weight Type (Primary) Type (Secondary)  ...  Is Mythical  Is Legendary                      Evolution Chain  Evolution Chain Length   Color      Shape
id                                                                                              ...
1                   bulbasaur             64.0       7      69          grass           poison  ...        False         False       [bulbasaur, ivysaur, venusaur]                     3.0   green  quadruped
2                     ivysaur            142.0      10     130          grass           poison  ...        False         False       [bulbasaur, ivysaur, venusaur]                     3.0   green  quadruped
3                    venusaur            263.0      20    1000          grass           poison  ...        False         False       [bulbasaur, ivysaur, venusaur]                     3.0   green  quadruped
4                  charmander             62.0       6      85           fire             None  ...        False         False  [charmander, charmeleon, charizard]                     3.0     red    upright
5                  charmeleon            142.0      11     190           fire             None  ...        False         False  [charmander, charmeleon, charizard]                     3.0     red    upright
...                       ...              ...     ...     ...            ...              ...  ...          ...           ...                                  ...                     ...     ...        ...
10245           dialga-origin              NaN      70    8487          steel           dragon  ...        False          True                             [dialga]                     1.0   white  quadruped
10246           palkia-origin              NaN      63    6590          water           dragon  ...        False          True                             [palkia]                     1.0  purple    upright
10247  basculin-white-striped              NaN      10     180          water             None  ...        False         False                           [basculin]                     1.0   green       fish
10248      basculegion-female              NaN      30    1100          water            ghost  ...        False         False                                 None                     NaN   green       fish
10249        enamorus-therian              NaN      16     480          fairy           flying  ...        False          True                                 None                     NaN    pink       arms

[1154 rows x 29 columns]
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

Formatting is done with [black](https://black.readthedocs.io/en/stable/). To format the code, before committing, run:

```bash
black .
```

There are pre commit hooks. To install them, run:

```bash
pre-commit install
```

## License

[BSD 3-Clause License](https://choosealicense.com/licenses/bsd-3-clause/)
