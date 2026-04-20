# use

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
