# traction

samples and patients in centraxx

```
trac = new tr.traction("num_test")
pat = trac.patient(sampleids=["abc"])
```

on the command line:

```
traction num_test sample --sampleid 1449330267 --verbose
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


## more usage

**command line**

get the samples of a patient:

```
traction <db> sample --patientid lims_565551365
```

get all samples in a study.

```
traction <db> sample --study "NUM RAPID_REVIVE"
```

get the findings (messbefunde) and their values for a bunch of samples:

```
traction <db> finding --sampleid sample1,sample2,sample3
```

get names for messparameters.

```
traction <db> name --table laborvalue
```

**python**

start a new traction instance.

```
trac = tr.traction("db_target")
```

get samples barebone.

```
res = trac.sample(sampleids=["sid1", "sid2", "sid3"])
```

get samples with all joined in info (slower).

```
res = trac.sample(sampleids=["sid1", "sid2", "sid3"], verbose_all=True)
```

get samples with specific joined in info.

```
res = trac.sample(sampleids=["sid1", "sid2", "sid3"], verbose=[tr.locationpath])
```

get the samples of a patient.

```
res = trac.sample(patientids=["pid1"], verbose_all=True)
```

get all samples in a study.

```
res = trac.sample(studies=["NUM RAPID_REVIVE"])
```

get the samples on a locationpath.

```
res = trac.sample(locationpaths=["my --> location --> path"])
```

get a patient.

```
res = trac.patient(patiendids=["pid1"])
```

get the patient for a sample.

```
pat = trac.patient(sampleids=["sid1"])
```

TODO get all patients in a study.

```
res = trac.patient(studies=["NUM RAPID_REVIVE"])
```

get the findings and their values for a sample.

```
res = trac.finding(sampleids=["sid1"])
```

get the display name for laborvalues (messparameters) by code.

```
acetone_name = trac.name("laborvalue")["NUM_NMR_ACETONE_VALUE"]["en"]
```

## dev

get [codetext](github.com/tnustrings/codetext) for assembling init.ct
and main.ct.

build and install:

```
make install
```