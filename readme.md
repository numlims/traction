# traction

samples, patient and else from centraxx

```
trac = new tr.traction("num_test")
result = trac.sample(sampleids=["1449330267"], verbose=[tr.locationpath])
```

api docs [here](https://numlims.github.io/traction/).

on the command line:

```
traction num_test sample --sampleid 1449330267 -a
```

see `traction -h`.

## go to

<a href="https://github.com/numlims/traction#install">install</a><br>
<a href="https://github.com/numlims/traction#use">use</a><br>
<a href="https://github.com/numlims/traction#dev">dev</a><br>

## install

<!--see [install.md](./install.md).-->

download traction whl from
[here](https://github.com/numlims/traction/releases). install with
pip:

```
pip install traction-<version>.whl
```

dbcq handles the db connection. run dbcq once to create its config
file, `~/.dbc`:

```
dbcq
```

you'll get a message showing the path to the `.dbc` config file:

```
dbcq: please edit /your/home/.dbc, then run again.
```

put your connection info into `.dbc`, for example:

```
[mycxx]
type = mssql
database = KAIROS_SPRING
username = <db user>
password = <db pass>
server = <ip address>
port = <port>
driver = {ODBC Driver 18 for SQL Server}
# or, path:
# driver = /path/to/my/libmsodbcsql-18.3.so.2.1
```

in this example, the target `mycxx` would later be used in traction calls:
(`traction mycxx ...`).

after setting up dbcq, run traction once to create the traction config file,
`~/.traction/settings.yaml`:

```
traction
```

edit `~/.traction/settings.yaml` to set your default idcontainer types
for sample and patient, and to set which idcontainer types should be
queryable as command line flags.

```
# sampleid sets the idcontainertype code that is used when searching for sampleid.
# put in a code per db target.
sampleid: 
  <db target>: <an idcontainertype code, e.g. SAMPLEID>
# patientid sets the idcontainertype code that is used when searching for patientid.
# put in a code per db target.
patientid: 
  <db target>: <an idcontainertype code, e.g. LIMSPSN>

# idc holds additional idcontainertype codes that will be queryable as command line flags.
idc:
 - <an idcontainertype code>
 - <another idcontainertype code>
```

the db target(s) you enter in `settings.yaml` should correspond to
the db target(s) listed in `~/.dbc`.

<!-- todo: run `traction <db target> idc` for a list of available idcontainers. -->

after setting up traction, you should be ready to go. try to get a sample:

```
traction mycxx sample -a --top 3
```

for more, see [use.md](./use.md).


## use

<!-- see [use.md](./use.md).-->

traction can be used via the command line or from python.  

**command line**

get a sample.

```
traction <db> sample --sampleid abc -a
```

`<db>` is a db target from your `~/.dbc` file.
`-a` joins in all values. this takes longer than without joining. use
`--verbose` to tailor which values should be joined in,
e.g. `--verbose locationpath,patientid`.

get a sample as csv.

```
traction <db> sample --sampleid abc -a --csv
```

get samples from sampleids in a file.

```
traction <db> sample --sampleid f:mysampleids.txt -a
```

get the missing samples.

```
traction <db> sample --sampleid f:mysampleids.txt --missing
```

get the samples of a patient:

```
traction <db> sample --patientid lims_565551365 -a
```

get the samples of a patient that were taken after a specific date.

```
traction <db> sample --patientid lims_565551365 --sampling-date ">=2025-11-24"
```

get all samples in a trial.

```
traction <db> sample --trial "NUM RAPID_REVIVE"
```

filter out the sampleids with jq.

```
traction <db> sample --trial "NUM RAPID_REVIVE" | jq -r '.[] | .sampleid'
```

get the child samples of a sample.

```
traction <db> sample --sampleid abc --childs
```

get the patients in the BSI or CNS module of SNID. like for sample,
pass `-a` to join in all info for patient.

```
traction <db> patient --trial "NUM S-SNID" --modul "BSI: Bloodstream Infections,CNS: CNS Infections" -a
```

get the findings (messbefunde) and their values for a bunch of samples:

```
traction <db> finding --sampleid A0942214,A0941343,A0941344
```

get the trials and their display names.

```
traction <db> trial
```

get a method (messprofil) and its labvals.

```
traction <db> method --method COV_2_SEQ
```

get a catalog and its entries, as csv.

```
traction <db> catalog --catalog CP --csv
```

get the usage entries (kontrolliertes vokabular).

```
traction <db> usageentry
```

get a user.

```
traction <db> user --username bob -a
```

get the display names for a table, here for labvals (messparameters).

```
traction <db> name --table laborvalue
```

**python**

start a new traction instance.

```
trac = tr.traction("db_target")
```

get samples.

```
res = trac.sample(sampleids=["sid1", "sid2", "sid3"], verbose_all=True)
```

`verbose_all=True` joins in all values. this takes longer than without
verbose_all. use `verbose` to tailor which values should be joined in,
e.g. `verbose=[tr.locationpath,tr.patientid]`.

get missing samples.

```
res = trac.sample(sampleids=["sid1", "sid2", "sid3"], missing=True)
```

get samples using another idcontainer (idc), EXTSAMPLEID, join in the locationpath.

```
res = trac.sample(idc={"EXTSAMPLEID": ["sid1", "sid2", "sid3"]}, verbose=[tr.locationpath])
```

get the samples of a patient1 in the rapid revive trial in module 1.

```
res = trac.sample(patientids=["patient1"], trials=["NUM RAPID_REVIVE"], idc={"MODUL": ["module 1"]}, verbose_all=True)
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

get all patients in the revive trial that are in the BSI module.

```
res = trac.patient(trials=["NUM RAPID_REVIVE"], idc={"MODUL": ["BSI: Bloodstream Infections"]})
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

<!--see [dev.md](./dev.md).-->


edit [`tr/main.ct`](./tr/main.ct) and [`tr/init.ct`](./tr/init.ct).

generate the code from ct with [ct](https://github.com/tnustrings/ct) or [ct for vscode](https://marketplace.visualstudio.com/items?itemName=tnustrings.codetext).

build and install:

```
make install
```

test:

```
make test
```

generate api doc:

```
make doc
```

