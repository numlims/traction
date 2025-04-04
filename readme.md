# traction

samples and patients in centraxx

```
tr = new traction("num_test")
pat = tr.patient(sampleid="abc")
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

build and install

```
python -m build --no-isolation; pip install dist/traction-<version>-py3-none-any.whl --no-deps --force-reinstall
```