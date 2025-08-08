from dbcq import *
import yaml
collectiondate = "samplingdate" # entnahmedatum / extraction date
derivaldate = "derivaldate" # aufteilungsdatum / date of distribution
extsampleid = "extsampleid"
first_repositiondate = "first_repositiondate" # datum der ersten einlagerung / date of first storage (not in fhir). is identical to derivaldate.
method_code = "method_code"
module = "module"
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
study_code = "study_code"
tier = "tier"
values = "values"
def _readsettings():
  if not _hassettings():
    with open(_settingspath(), "w") as file:
      settingsstr = """
# settings for traction.

# sampleid sets the default sample id container type
sampleid: <an idcontainertype code, e.g. SAMPLEID>
# patientid sets the default patient id container type
patientid: <an idcontainertype code, e.g. LIMSPSN>

# sidc holds codes for sampleidcontainers that will be queryable as command line flags 
sidc:
 - <an idcontainertype code>
 - <another idcontainertype code>
"""
      file.write(settingsstr)
      print(f"please fill in the sampleidcontainer types for sample and patient in {_settingspath()}, then run again.")
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
        self._idctypes = self._getidctypes()
        #print(f"_idctypes: {self._idctypes}")

    def sample(self, sampleids=None, sidc=None, patientids=None, locationpaths=None, studies=None, verbose=[], verbose_all=False, missing=False):
        # print("try:" + tr.sampleid)
        vaa = [locationname, locationpath, orgunit_code, parentid,
               patientid, project_code, receptacle_code, sampleid, sampletype_code,
               secondprocessing_code, stockprocessing_code, study_code]
        if not sampleid in verbose:
            verbose.append(sampleid)
        if patientids:
            verbose.append(patientid)
        if studies:
            verbose.append(study_code)
        #if tiers:
        #    verbose.append(tier)
        #if modules:
        #    verbose.append(module)
        if locationpaths:
            verbose.append(locationpath)
        if verbose_all == True:
            verbose = vaa
        selects = {
            sampleid: [f"sidc.psn as '{sampleid}'"],
            # extsampleid: [f"extsidc.psn as '{extsampleid}'"],
            parentid: [f"parentidc.psn as '{parentid}'"],
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
            study_code: [f"flexistudy.code as '{study_code}'"],
            # tier: [f"tiersidc.psn as '{tier}'"]
        }
        joins = {
            sampleid: ["inner join centraxx_sampleidcontainer as sidc on sidc.sample = sample.oid"],
            # extsampleid: ["inner join centraxx_sampleidcontainer as extsidc on extsidc.sample = sample.oid"],
            # module: ["inner join centraxx_sampleidcontainer as modulesidc on modulesidc.sample = sample.oid"],
            parentid: ["left join centraxx_sampleidcontainer parentidc on parentidc.sample = sample.parent"],
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
            study_code: ["left join centraxx_flexistudy as flexistudy on sample.flexistudy = flexistudy.oid"]
        }
        selecta = ["sample.*"]
        joina = []
        possibleverbose = vaa + self.settings["sidc"]
        for verb in verbose:
            if not verb in possibleverbose: 
                print(f"error: key {verb} must be in {possibleverbose}.")

            # continue if verb not in selects, it could be handled by sidc
            if not verb in selects:
                continue
        
            # put in the select line(s)
            for s in selects[verb]:
                selecta.append(s)

            # continue if verb not in joins, it could be handled by sidc
            if not verb in joins:
                continue

            for s in joins[verb]:
                # both locationpath and locationname join in samplelocation, so check that it's not already in the join array
                if not s in joina:
                    joina.append(s)
        selecta = self._append_sidc_select(selecta, sidc, verbose)
        joina = self._append_sidc_join(joina, sidc, verbose)
        selectstr = ", \n".join(selecta)
        joinstr = "\n ".join(joina)
        (wherestr, whereargs) = self._where(sampleids=sampleids, sidc=sidc, patientids=patientids, studies=studies, locationpaths=locationpaths, verbose=verbose)
        query = f"select {selectstr} from centraxx_sample sample {joinstr} where {wherestr}"
        #print(query)
        #print(whereargs)
        res = self.db.qfad(query, whereargs)

        return res
    def patient(self, patientids=None, sampleids=None, studies=None):
        query = f"""
        select patc.*, patidc.psn as {patientid} from centraxx_idcontainer patidc
        left join centraxx_patientcontainer patc on patidc.patientcontainer = patc.oid
        left join centraxx_sample sample on sample.patientcontainer = patc.oid
        left join centraxx_sampleidcontainer sidc on sidc.sample = sample.oid
        where patidc.idcontainertype = 8"""
        (wherestr, whereargs) = self._where(sampleids=sampleids, patientids=patientids, studies=studies)

        query += " and " + wherestr
        #print(query)
        #print(whereargs)
        res = self.db.qfad(query, whereargs)

        return res
    def finding(self, sampleids=None, methods=None, studies=None, patientids=None, verbose=[], verbose_all=False):
        query = f"""select laborfinding.oid as "laborfinding_oid", laborfinding.*, labormethod.code as {method_code}, sidc.psn as {sampleid}
        from centraxx_laborfinding as laborfinding

        -- go from laborfinding to sample
        left join centraxx_labormethod as labormethod on laborfinding.labormethod = labormethod.oid
        left join centraxx_labormapping as labormapping on labormapping.laborfinding = laborfinding.oid
        left join centraxx_sample sample on labormapping.relatedoid = sample.oid
        left join centraxx_sampleidcontainer sidc on sidc.sample = sample.oid"""
        (wherestr, whereargs) = self._where(sampleids=sampleids, methods=methods, studies=studies)

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

    def _append_sidc_select(self, selecta, sidc, verbose):
      sidca = []
      for verb in verbose:
        if verb in self.settings["sidc"]:
          sidca.append(verb)
      sidca.extend(sidc.keys())
      for item in sidca:
        selectstr = f"sidc_{item}.psn as '{item}'"
        if not selectstr in selecta:
          selecta.append(selectstr)
      return selecta
    def _append_sidc_join(self, joina, sidc, verbose):
      sidca = []
      for verb in verbose:
        if verb in self.settings["sidc"]:
          sidca.append(verb)
      sidca.extend(sidc.keys())
      for item in sidca:
        joinstr = f"inner join centraxx_sampleidcontainer as sidc_{item} on sidc_{item}.sample = sample.oid"
        if not joinstr in joina:
          joina.append(joinstr)
      return joina
    def _where(self, sampleids=None, sidc={}, patientids=None, studies=None, locationpaths=None, methods=None, like=[], verbose=[]): # -> (str, [])
        wheredict = {
          sampleid: { "arr": sampleids, "field": "sidc.psn", "morewhere": f"sidc.idcontainertype = {self._idctypes[self.settings['sampleid'].lower()]}" }, # pass the idcontainertype check along

          patientid: { "arr": patientids, "field": "patidc.psn", "morewhere": f"patidc.idcontainertype = {self._idctypes[self.settings['patientid'].lower()]}" },
          study_code: { "arr": studies, "field": "flexistudy.code" },
          locationpath: { "arr": locationpaths, "field": "samplelocation.locationpath" },
          method_code: { "arr": methods, "field": "labormethod.code" },
        }
        sidca = list(sidc.keys()) + list(set(verbose).intersection(self.settings["sidc"]))
        for item in sidca:
            wheredict[item] = { "arr": sidc[item] if item in sidc else None, 
                               "field": f"sidc_{item}.psn", 
                               "morewhere": f"sidc_{item}.idcontainertype = {self._idctypes[item]}"
                             }
        (wherearr, whereargs) = self._wherebuild(wheredict, like, verbose)

        wherestr = " and ".join(wherearr)
        return (wherestr, whereargs)
    def _wherebuild(self, wheredict, likearr=[], verbose=[]): # ([]string, [])
        wherearr = []
        whereargs = []
        for (key, row) in wheredict.items():
            if row["arr"] == None or len(row["arr"]) == 0:
                # the key is in the verbose-output selection
                if key in verbose and "morewhere" in row:
                    # we're not searching for specific values, so only add the morewhere clause
                    wherearr.append(row["morewhere"])
                continue
            if key in likearr: 
                # put in an or-chain of like checks over all elements
                s = self._wherelikes(row["field"], row["arr"]) 
                wherearr.append(s)
                whereargs.append(row["arr"])
            else:
                placeholder = traction._sqlinplaceholder(len(row["arr"])) # todo put in package? tr._sqlinplaceholder
                # fill wherearr and whereargs
                wherearr.append(row["field"] + " in " + placeholder) # e.g. samplelocation.locationpath in (?, ?, ?)
                whereargs.extend(row["arr"])
            if "morewhere" in row:
                wherearr.append(row["morewhere"])
        return (wherearr, whereargs)
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
    def _getidctypes(self):
        query = "select code, oid from centraxx_idcontainertype"
        res = self.db.qfad(query)
        out = {}
        for row in res:
          out[row["code"].lower()] = row["oid"]
        return out
  
