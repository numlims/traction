# traction

samples and patients in centraxx

```
trac = new tr.traction("num_test")
result = trac.sample(sampleids=["1449330267"], verbose=[tr.locationpath])
```

on the command line:

```
traction num_test sample --sampleid 1449330267 --verbose-all
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

after the first traction run set your default idcontainer codes for
sample and patient in `~/.traction/settings.yaml`. 

## more usage

**command line**

get the samples of a patient:

```
traction <db> sample --patientid lims_565551365
```

get all samples in a trial.

```
traction <db> sample --trial "NUM RAPID_REVIVE"
```

get all master samples where the kitid is NULL that don't have a dot
at the end of their sample id (passed as an additional where clause
with --where).

```
traction <db> sample --cxxkitid NULL --dtype MASTER --where "sidc.psn not like '%.'"
```

get all patients in the BSI or CNS module of SNID.

```
traction <db> patient --trial "NUM S-SNID" --modul "BSI: Bloodstream Infections,CNS: CNS Infections"
```

get the findings (messbefunde) and their values for a bunch of samples:

```
traction <db> finding --sampleid A0942214,A0941343,A0941344
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

get samples with info from idcontainers (idc).

```
res = trac.sample(idc={"extsampleid": ["sid1", "sid2", "sid3"]}, verbose=[tr.locationpath])
```

get the samples of a patient1 in the rapid revive trial in module 1.

```
res = trac.sample(patientids=["patient1"], trials=["NUM RAPID_REVIVE"], idc={"module": ["module 1"]}, verbose_all=True)
```

get all samples in a trial.

```
res = trac.sample(trials=["NUM RAPID_REVIVE"])
```

get the samples on a locationpath.

```
res = trac.sample(locationpaths=["my --> location --> path"])
```

get a patient.

```
res = trac.patient(patientids=["patient1"])
```

get the patient for a sample.

```
pat = trac.patient(sampleids=["sample1"])
```

TODO get all patients in a trial.

```
res = trac.patient(trials=["NUM RAPID_REVIVE"])
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

get [codetext](https://github.com/tnustrings/ct) for assembling init.ct
and main.ct.

build and install:

```
make install
```