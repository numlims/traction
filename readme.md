# traction

samples and patients in centraxx

```
tr = new traction("num_test")
pat = tr.patient(sampleids=["abc"])
```

on the command line:

```
traction num_test sample 1449330267 --verbose
```

see `traction -h`.

## install

download traction whl from
[here](https://github.com/numlims/traction/releases). install with
pip:

```
pip install traction-<version>.whl
```

for database connection setup see
[dbcq](https://github.com/numlims/dbcq?tab=readme-ov-file#db-connection).


## dev

get [codetext](github.com/tnustrings/codetext) for assembling init.ct
and main.ct.

build and install:

```
make install
```