# install traction

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
