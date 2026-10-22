# Source Robotics documentation

The landing page of [docs.source-robotics.com](https://docs.source-robotics.com/): one card per product, each
linking to that product's own documentation site.

## How the domain works

This repository is the organisation's own GitHub Pages site, so its custom domain, `docs.source-robotics.com`, is
also the domain of every other documentation site in the organisation. A docs repository named `par6` is served at
`docs.source-robotics.com/par6/`, `PAROL-docs` at `docs.source-robotics.com/PAROL-docs/`, and so on.

- **Do not rename or delete this repository.** Every Source Robotics docs site would move back to its github.io
  address.
- **Renaming a docs repository changes its address,** and links to the old one stop working. A redirect page can be
  added here under the old name.
- **A new product** gets a card in `docs/index.md` once its docs repository publishes.

## Preview it locally

```bash
git clone https://github.com/Source-Robotics/source-robotics.github.io.git
cd source-robotics.github.io
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve
```

Open `http://127.0.0.1:8000/`. Every push to `main` builds the site and publishes it.

## License

- **Text and images:** [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
  see [LICENSE](LICENSE).
- **Code:** the [MIT license](LICENSE-CODE).
- **Names and logos:** the Source Robotics name, the product names and the logos are not covered by either license.
