# PokéDEX

This package was put together as a teaching tool for learning how to work with data. The PokéAPI provides the core data for this package.

To be friendly to the PokéAPI, this package will only make one request to the API per session. This means that if you want to use the data in a different session, you will need to make a new request.

## Installation

```bash
pip install poked
```

## Usage

```python
from poked import poked

df = poked.get_pokemon()

df.head()
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
