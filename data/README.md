# The measurement data goes here

This folder is intentionally empty. The `.dm4` files are hundreds of megabytes, so
they are not kept in the repository.

**Download link:** <PUT THE DOWNLOAD LINK HERE>

Unpack the ZIP so that the `nanopore` folder sits **directly here**:

```
data/
├── README.md                 <- this file
└── nanopore/
    ├── EELS Spectrum Image (high-loss).dm4
    ├── EELS Spectrum Image (low-loss).dm4
    ├── EDS Spectrum Image.dm4
    ├── ADF Image.dm4
    ├── ADF Image (SI Survey).dm4
    └── Si Standards/
```

That is all the workshop needs.

Your own measurements go into subfolders next to `nanopore`, for example
`data/my_sample/`. `03_your_own_data.ipynb` shows how to use them; nothing in
`data/` is ever committed to the repository.

Not like this (one folder level too many - the most common mistake):

```
data/
└── measurements/
    └── nanopore/
```

To check that everything is found:

```bash
pixi run check
```
