from dbcq import *
import yaml
cxxkitid = "cxxkitid"
collectiondate = "samplingdate" # entnahmedatum / extraction date
derivaldate = "derivaldate" # aufteilungsdatum / date of distribution
dtype = "dtype" # MASTER, ALIQUOTGROUP, DERIVED. maybe rename this to sampletype and sampletype (EDTA, stool etc) to samplekind as in the ui?
extsampleid = "extsampleid"
first_repositiondate = "first_repositiondate" # datum der ersten einlagerung / date of first storage (not in fhir). is identical to derivaldate.
method_code = "method_code"
module = "module"
kitid = "kitid"
locationname = "locationname"
locationpath = "locationpath"
orgunit_code = "orgunit_code"
parentid = "parentid"
patientid = "patientid"
project_code = "project_code"
receiptdate = "receiptdate" # eingangsdatum / date of receipt
receptacle_code = "receptacle_code"
repositiondate = "repositiondate" # einlagerungsdatum / storage date
sampleid = "sampleid"
sampletype_code = "sampletype_code"
secondprocessing_code = "secondprocessing_code"
stockprocessing_code = "stockprocessing_code"
trial_code = "trial_code"
tier = "tier"
values = "values"
def _readsettings():
  if not _hassettings():
    with open(_settingspath(), "w") as file:
      settingsstr = """
# settings for traction.

# sampleid sets the idcontainertype code that is used when searching for sampleid
sampleid: <an idcontainertype code, e.g. SAMPLEID>
# patientid sets the idcontainertype code that is used when searching for patientid
patientid: <an idcontainertype code, e.g. LIMSPSN>

# idc holds additional idcontainertype codes that will be queryable as command line flags 
idc:
 - <an idcontainertype code>
 - <another idcontainertype code>
"""
      file.write(settingsstr)
      print(f"please fill in the idcontainertype codes for sampleid and patientid in {_settingspath()}, then run again.")
      return None
  else:
    # read settings file yaml
    with open(_settingspath(), "r") as file:
      settings = yaml.safe_load(file)
      return settings
def _hassettings():
    return _settingspath().is_file()

def _settingspath():
    home = Path.home()
    return home / ".traction" / "settings.yaml"
class traction:
  #`vars``
    def __init__(self, target):
        self.settings = _readsettings()
        if self.settings == None:
            raise Exception("settings missing.")
            return
        if isinstance(target, str):
            self.db = dbcq(target)
        elif isinstance(target, dbcq): 
            self.db = target
        else:
            raise Exception("target needs to be string or dbcq instance")
        self._idcinit()
        #print(f"_idcoids: {self._idcoids}")

    def sample(self, sampleids=None, idc=None, patientids=None, locationpaths=None, trials=None, kitids=None, cxxkitids=None, dtypes=None, verbose=[], verbose_all=False, like=[], missing=False, where=None, order_by=None, top=None, print_query=False):
        # print("try:" + tr.sampleid)
        vaa = [sampleid, cxxkitid, kitid, locationname, locationpath, orgunit_code, parentid,
               patientid, project_code, receptacle_code, sampletype_code,
               secondprocessing_code, stockprocessing_code, trial_code]
        if not sampleid in verbose:
            verbose.insert(0, sampleid)
        if patientids:
            verbose.append(patientid)
        if trials:
            verbose.append(trial_code)
        #if tiers:
        #    verbose.append(tier)
        #if modules:
        #    verbose.append(module)
        if locationpaths:
            verbose.append(locationpath)
        if kitids:
            verbose.append(kitid)
        if cxxkitid:
            verbose.append(cxxkitid)
        if verbose_all == True:
            verbose = vaa
        selects = {
            cxxkitid: [f"samplekit.cxxkitid as '{cxxkitid}'"],
            sampleid: [f"sidc.psn as '{sampleid}'"],
            # extsampleid: [f"extsidc.psn as '{extsampleid}'"],
            parentid: [f"parentidc.psn as '{parentid}'"],
            kitid: [f"samplekit.kitid as '{kitid}'"],
            locationname: [f"samplelocation.locationid as '{locationname}'"], 
            locationpath: [f"samplelocation.locationpath as '{locationpath}'"],
            # module: [f"modulesidc.psn as '{module}'"],
            sampletype_code: [f"sampletype.code as '{sampletype_code}'"],
            stockprocessing_code: [f"stockprocessing.code as '{stockprocessing_code}'"],
            secondprocessing_code: [f"secondprocessing.code as '{secondprocessing_code}'"],
            project_code: [f"project.code as '{project_code}'"],
            patientid: [f"patidc.psn as '{patientid}'"],
            receptacle_code: [f"receptable.code as '{receptacle_code}'"],
            orgunit_code: [f"orgunit.code as '{orgunit_code}'"],
            trial_code: [f"flexistudy.code as '{trial_code}'"],
            # tier: [f"tiersidc.psn as '{tier}'"]
        }
        joins = {
            sampleid: ["inner join centraxx_sampleidcontainer as sidc on sidc.sample = sample.oid"],
            cxxkitid: ["left join centraxx_samplekititem as samplekititem on samplekititem.tubebarcode = sidc.psn", "left join centraxx_samplekit as samplekit on samplekit.oid = samplekititem.samplekit"],                  
            # extsampleid: ["inner join centraxx_sampleidcontainer as extsidc on extsidc.sample = sample.oid"],
            # module: ["inner join centraxx_sampleidcontainer as modulesidc on modulesidc.sample = sample.oid"],
            parentid: ["left join centraxx_sampleidcontainer parentidc on parentidc.sample = sample.parent"],
            kitid: ["left join centraxx_samplekititem as samplekititem on samplekititem.tubebarcode = sidc.psn", "left join centraxx_samplekit as samplekit on samplekit.oid = samplekititem.samplekit"],
            locationname: ["left join centraxx_samplelocation samplelocation on samplelocation.oid = sample.samplelocation"],
            locationpath: ["left join centraxx_samplelocation samplelocation on samplelocation.oid = sample.samplelocation"],
            sampletype_code: ["left join centraxx_sampletype as sampletype on sampletype.oid = sample.sampletype"],
            stockprocessing_code: ["left join centraxx_stockprocessing as stockprocessing on sample.stockprocessing = stockprocessing.oid"],
            secondprocessing_code: ["left join centraxx_stockprocessing as secondprocessing on sample.secondprocessing = secondprocessing.oid"],
            # tier: ["inner join centraxx_sampleidcontainer as tiersidc on tiersidc.sample = sample.oid"],
            project_code: ["left join centraxx_project as project on sample.project = project.oid"],
            patientid: ["left join centraxx_patientcontainer as patientcontainer on sample.patientcontainer = patientcontainer.oid",
            "left join centraxx_idcontainer as patidc on patidc.patientcontainer = patientcontainer.oid"], 
            receptacle_code: ["left join centraxx_samplereceptable as receptable on sample.receptable = receptable.oid"], # receptable seems to be a typo in the table naming
            orgunit_code: ["left join centraxx_organisationunit as orgunit on sample.orgunit = orgunit.oid"],
            trial_code: ["left join centraxx_flexistudy as flexistudy on sample.flexistudy = flexistudy.oid"]
        }
        selecta = ["sample.*"]
        joina = []
        possibleverbose = vaa + self.settings["idc"]
        for verb in verbose:
            if not verb in possibleverbose: 
                print(f"error: key {verb} must be in {possibleverbose}.")

            # continue if verb not in selects, it could be handled by idc
            if not verb in selects:
                continue
        
            # put in the select line(s)
            for s in selects[verb]:
                selecta.append(s)

            # continue if verb not in joins, it could be handled by idc
            if not verb in joins:
                continue

            for s in joins[verb]:
                # both locationpath and locationname join in samplelocation, so check that it's not already in the join array
                if not s in joina:
                    joina.append(s)
        selecta = self._append_idc_select(selecta, idc, verbose)
        joina = self._append_idc_join(joina, idc, verbose)
        selectstr = ", \n".join(selecta)
        joinstr = "\n ".join(joina)
        (wherestr, whereargs) = self._where(sampleids=sampleids, idc=idc, patientids=patientids, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, dtypes=dtypes, verbose=verbose, like=like) 
        if where is not None:
           wherestr += " and (" + where + ")"
        topstr = self._top(top)
        query = f"select {topstr} {selectstr} from centraxx_sample sample {joinstr} where {wherestr}"
        if order_by is not None:
            query += f" order by {order_by}"
        if print_query:
           print(query)
        #print(whereargs)
        res = self.db.qfad(query, whereargs)

        return res
    def patient(self, patientids=None, sampleids=None, trials=None):
        query = f"""
        select patc.*, patidc.psn as {patientid} from centraxx_idcontainer patidc
        left join centraxx_patientcontainer patc on patidc.patientcontainer = patc.oid
        left join centraxx_sample sample on sample.patientcontainer = patc.oid
        left join centraxx_sampleidcontainer sidc on sidc.sample = sample.oid
        where patidc.idcontainertype = 8"""
        (wherestr, whereargs) = self._where(sampleids=sampleids, patientids=patientids, trials=trials)

        query += " and " + wherestr
        #print(query)
        #print(whereargs)
        res = self.db.qfad(query, whereargs)

        return res
    def trial(self):
        query = "select code from centraxx_flexistudy"
        res = self.db.qfad(query)
        return res
    def finding(self, sampleids=None, methods=None, trials=None, patientids=None, verbose=[], verbose_all=False):
        query = f"""select laborfinding.oid as "laborfinding_oid", laborfinding.*, labormethod.code as {method_code}, sidc.psn as {sampleid}
        from centraxx_laborfinding as laborfinding

        -- go from laborfinding to sample
        left join centraxx_labormethod as labormethod on laborfinding.labormethod = labormethod.oid
        left join centraxx_labormapping as labormapping on labormapping.laborfinding = laborfinding.oid
        left join centraxx_sample sample on labormapping.relatedoid = sample.oid
        left join centraxx_sampleidcontainer sidc on sidc.sample = sample.oid"""
        (wherestr, whereargs) = self._where(sampleids=sampleids, methods=methods, trials=trials)

        query += " where " + wherestr
        # print(query)
        findings = self.db.qfad(query, whereargs)
        for i, finding in enumerate(findings):
            query = """select recordedvalue.*, laborvalue.code as laborvalue_code
                from centraxx_laborfinding as laborfinding

                -- go from laborfinding to recorded value
                join centraxx_labfindinglabval as labfindinglabval on labfindinglabval.laborfinding = laborfinding.oid
                join centraxx_recordedvalue as recordedvalue on labfindinglabval.oid = recordedvalue.oid

                --go from labfindinglabval to the laborvalue for the messparam
                join centraxx_laborvalue laborvalue on labfindinglabval.laborvalue = laborvalue.oid

                where laborfinding.oid = ?
            """
            vals = self.db.qfad(query, finding['laborfinding_oid'])
            valsbycode = {}
            for val in vals:
              valsbycode[val["laborvalue_code"]] = val
            findings[i][values] = valsbycode
        return findings
    def labval(self, methods=None):
        query = f"""select labval.*, method.code
from centraxx_labormethod method
inner join centraxx_crftemplate crf_t
    on method.crf_template=crf_t.oid
inner join centraxx_crftempsection crf_ts
    on crf_t.oid=crf_ts.crftemplate
inner join centraxx_crftempsection_fields crf_tsf
    on crf_ts.oid=crf_tsf.crftempsection_oid
inner join centraxx_crftempfield crf_tf
    on crf_tsf.crftempfield_oid=crf_tf.oid
inner join centraxx_laborvalue labval
    on crf_tf.labval=labval.oid"""
        (wherestr, whereargs) = self._where(methods=methods)

        query += " where " + wherestr
        res = self.db.qfad(query, whereargs)

        return res
    def name(self, table:str, code:str=None, lang:str=None, ml_table:str=None):
        query = "select [" + table + "].code, multilingual.value as name, multilingual.lang as lang"
        query += " from [centraxx_" + table + "] as [" + table + "]"
        ml_name = ""
        if ml_table != None: # the name is different
            ml_name = "centraxx_" + ml_table
        else: # the name is the same
            ml_name = "centraxx_" + table + "_ml_name"
        query += " inner join [" + ml_name + "] mlname on mlname.related_oid = [" + table + "].oid"
        query += " inner join centraxx_multilingualentry multilingual on mlname.oid = multilingual.oid"
        wherestrings = []
        args = []
        if code != None:
            wherestrings.append(self._whereparam("[" + table + "].code"))
            args.append(code)
        if lang != None:
            wherestrings.append(self._whereparam("multilingual.lang"))
            args.append(lang)
        if len(wherestrings) > 0:
            query += " where "
            # join where clauses by and
            query += " and ".join(wherestrings)

        # print(query)
        res = self.db.qfad(query, *args)
        out = {}
        for line in res:
            code = line["code"]
            lang = line["lang"]
            if not code in out:
               out[code] = {}
            out[code][lang] = line["name"]
        return out

    def _append_idc_select(self, selecta, idc, verbose):
      idca = []
      for verb in verbose:
        if verb in self.settings["idc"]:
          idca.append(verb)
      if idc is not None:
        idca.extend(idc.keys())
      for item in idca:
        selectstr = f"idc_{item}.psn as '{item}'"
        if not selectstr in selecta:
          selecta.append(selectstr)
      return selecta
    def _append_idc_join(self, joina, idc, verbose):
      idca = []
      for verb in verbose:
        if verb in self.settings["idc"]:
          idca.append(verb)
      if idc is not None:                                
        idca.extend(idc.keys())
      for item in idca:
        if self._idckind[item] == "SAMPLE":
          joinstr = f"inner join centraxx_sampleidcontainer as idc_{item} on idc_{item}.sample = sample.oid"
          if not joinstr in joina:
            joina.append(joinstr)
        elif self._idckind[item] == "PATIENT":
          joinstr = f"left join centraxx_patientcontainer as pc_{item} on sample.patientcontainer = pc_{item}.oid"
          if not joinstr in joina: # neccessary?
            joina.append(joinstr)
          joinstr = f"left join centraxx_idcontainer as idc_{item} on pc_{item}.oid = idc_{item}.patientcontainer"
          if not joinstr in joina: # neccessary?
            joina.append(joinstr)
        else:
          print(f"error: idcontainer kind {self._idckind[item]} not supported.")
      return joina
    def _where(self, sampleids=None, idc={}, patientids=None, trials=None, locationpaths=None, kitids=None, cxxkitids=None, dtypes=None, methods=None, like=[], verbose=[]): # -> (str, [])
        wheredict = {
          sampleid: { "arr": sampleids, "field": "sidc.psn", "morewhere": f"sidc.idcontainertype = {self._idcoid[self.settings['sampleid'].lower()]}" }, # pass the idcontainertype check along

          patientid: { "arr": patientids, "field": "patidc.psn", "morewhere": f"patidc.idcontainertype = {self._idcoid[self.settings['patientid'].lower()]}" },
          trial_code: { "arr": trials, "field": "flexistudy.code" },
          locationpath: { "arr": locationpaths, "field": "samplelocation.locationpath" },
          method_code: { "arr": methods, "field": "labormethod.code" },
          kitid: { "arr": kitids, "field": "samplekit.kitid" },
          cxxkitid: { "arr": cxxkitids, "field": "samplekit.cxxkitid" },
          dtype: { "arr": dtypes, "field": "sample.dtype" },
        }
        idckeys = [] if idc is None else idc.keys()
        idca = list(idckeys) + list(set(verbose).intersection(self.settings["idc"]))
        for item in idca:
            wheredict[item] = { "arr": idc[item] if item in idc else None, 
                                "field": f"idc_{item}.psn", 
                                "morewhere": f"idc_{item}.idcontainertype = {self._idcoid[item]}"
                             }
        (wherearr, whereargs) = self._wherebuild(wheredict, like, verbose)

        wherestr = " and ".join(wherearr)
        return (wherestr, whereargs)
    def _wherebuild(self, wheredict, likearr=[], verbose=[]): # ([]string, [])
        wherestrs = []
        whereargs = []
        for (key, row) in wheredict.items():
            if row["arr"] == None or len(row["arr"]) == 0:
                # the key is in the verbose-output selection
                if key in verbose and "morewhere" in row:
                    # we're not searching for specific values, so only add the morewhere clause
                    wherestrs.append(row["morewhere"])
                continue
            if likearr is not None and key in likearr: 
                # put in an or-chain of like checks over all elements
                s = "(" + self._wherelikes(row["field"]) + ")"
                wherestrs.append(s)
                whereargs.append(row["arr"])
            else:
                wherestr = "("
                needsor = False
                if 'NULL' in row["arr"]:
                    row["arr"].remove("NULL")
                    wherestr += row["field"] + " is NULL"
                    needsor = True
                if len(row["arr"]) > 0:
                    if needsor:
                        wherestr += " or "
                    placeholder = traction._sqlinplaceholder(len(row["arr"])) # todo put in package? tr._sqlinplaceholder
                    wherestr += row["field"] + " in " + placeholder # e.g. samplelocation.locationpath in (?, ?, ?)
                wherestr += ")"
                wherestrs.append(wherestr)
                whereargs.extend(row["arr"])
            if "morewhere" in row:
                wherestrs.append(row["morewhere"])
        return (wherestrs, whereargs)
    def _sqlinplaceholder(n):

        # put this in a package sqlutil?

        out = "("
        for i in range(n):
            out += "?"
            if i < n - 1:
                out += ","
        out += ")"
        return out
    def _whereparam(self, name, like:bool=None):
        if like == None or like == False:
            return name + " = ?"
        else:
            return name + " like '%' + ? + '%'"
    def _wherelike(self, name):
          return name + " like '%' + ? + '%'"

    def _wherelikes(self, fieldarr):
        a = []
        for f in fieldarr:
            a.append(f + " like '%' + ? + '%'") # the sql takes literal plusses like here
        return " or ".join(a)
    def _top(self, top):
        if top is not None:
           return f"top {top}"
        return ""
    def _idcinit(self):
        query = "select code, oid, kind from centraxx_idcontainertype"
        res = self.db.qfad(query)
        self._idcoid = {}
        self._idckind = {}
        for row in res:
          self._idcoid[row["code"].lower()] = row["oid"]
          self._idckind[row["code"].lower()] = row["kind"]
  
