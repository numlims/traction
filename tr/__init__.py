from dbcq import *
cxxkitid = "cxxkitid"
collectiondate = "samplingdate" # entnahmedatum / extraction date
derivaldate = "derivaldate" # aufteilungsdatum / date of distribution
dtype = "dtype" # MASTER, ALIQUOTGROUP, DERIVED. maybe rename this to sampletype and sampletype (EDTA, stool etc) to samplekind as in the ui?
extsampleid = "extsampleid"
first_repositiondate = "first_repositiondate" # datum der ersten einlagerung / date of first storage (not in fhir). is identical to derivaldate.
method_code = "method_code"
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
values = "values"
cnftemplate = """
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
def _checkverbose(verbose, possible):
    """
    _checkverbose makes shure that only allowed keys are in the verbose array. 
    """
    for verb in verbose:
        if not verb in possible: 
            print(f"error: verbose entry {verb} must be in {possible}.")
            return False
    return True
class traction:
    jd = {
            "sample_to_sampleid": ["inner join centraxx_sampleidcontainer as sidc on sidc.sample = sample.oid"],
            "sample_to_samplekit": ["left join centraxx_samplekititem as samplekititem on samplekititem.tubebarcode = sidc.psn", "left join centraxx_samplekit as samplekit on samplekit.oid = samplekititem.samplekit"],                  
            "sample_to_parentid": ["left join centraxx_sampleidcontainer parentidc on parentidc.sample = sample.parent"],
            "sample_to_samplelocation": ["left join centraxx_samplelocation samplelocation on samplelocation.oid = sample.samplelocation"],
            "sample_to_sampletype": ["left join centraxx_sampletype as sampletype on sampletype.oid = sample.sampletype"],
            "sample_to_stockprocessing": ["left join centraxx_stockprocessing as stockprocessing on sample.stockprocessing = stockprocessing.oid"],
            "sample_to_secondprocessing": ["left join centraxx_stockprocessing as secondprocessing on sample.secondprocessing = secondprocessing.oid"],
            "sample_to_project": ["left join centraxx_project as project on sample.project = project.oid"],
            "sample_to_patientid": ["left join centraxx_patientcontainer as patientcontainer on sample.patientcontainer = patientcontainer.oid",
            "left join centraxx_idcontainer as patidc on patidc.patientcontainer = patientcontainer.oid"], 
            "sample_to_receptacle": ["left join centraxx_samplereceptable as receptable on sample.receptable = receptable.oid"], # receptable seems to be a typo in the table naming
            "sample_to_orgunit": ["left join centraxx_organisationunit as organisationunit on sample.orgunit = organisationunit.oid"],
            "sample_to_trial": ["left join centraxx_flexistudy as flexistudy on sample.flexistudy = flexistudy.oid"]
        ,
            "patient_to_orgunit": ["left join centraxx_patientorgunit patientorgunit on patidc.patientcontainer=patientorgunit.patientcontainer_oid", "left join centraxx_organisationunit organisationunit on patientorgunit.orgunit_oid=organisationunit.oid"],
            "patient_to_patientid": ["left join centraxx_idcontainer patidc on patidc.patientcontainer = patientcontainer.oid"],
            "patient_to_trial": ["left join centraxx_patientstudy as patientstudy on patientstudy.patientcontainer = patientcontainer.oid", "left join centraxx_flexistudy as flexistudy on flexistudy.oid = patientstudy.flexistudy"],
            "patient_to_sample": ["left join centraxx_sample sample on sample.patientcontainer = patientcontainer.oid"]
    }
    def __init__(self, target):
        """
        __init__ takes the db target either as string or dbcq object.
        """
        self.settings = cnf.makeload(path=".traction/settings.yaml", root=cnf.home, fmt="yaml", make=cnftemplate)        
        if self.settings == None:
            raise Exception("no settings.")
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
        """
        sample gets sample(s) by sampleid or external id. pass sampleids as
        array. to join in more information, say verbose_all=True, this is
        slower than non-verbose.
        
        the first implementation tried to take the tablenames/colums as keys
        for the returned json fields, but that doesn't quite work for
        patientpsn, where the key would be just 'idcontainer.psn'. so maybe
        rename the joined-in fields to sampleid, *_code, patientid,
        parentid etc.
        """
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
        if locationpaths:
            verbose.append(locationpath)
        if kitids:
            verbose.append(kitid)
        if cxxkitid:
            verbose.append(cxxkitid)
        if verbose_all == True:
            verbose = vaa
        if not _checkverbose(verbose, vaa + self.settings["idc"]):
            return None # throw error?
        selects = {
            cxxkitid: [f"samplekit.cxxkitid as '{cxxkitid}'"],
            sampleid: [f"sidc.psn as '{sampleid}'"],
            parentid: [f"parentidc.psn as '{parentid}'"],
            kitid: [f"samplekit.kitid as '{kitid}'"],
            locationname: [f"samplelocation.locationid as '{locationname}'"], 
            locationpath: [f"samplelocation.locationpath as '{locationpath}'"],
            sampletype_code: [f"sampletype.code as '{sampletype_code}'"],
            stockprocessing_code: [f"stockprocessing.code as '{stockprocessing_code}'"],
            secondprocessing_code: [f"secondprocessing.code as '{secondprocessing_code}'"],
            project_code: [f"project.code as '{project_code}'"],
            patientid: [f"patidc.psn as '{patientid}'"],
            receptacle_code: [f"receptable.code as '{receptacle_code}'"],
            orgunit_code: [f"organisationunit.code as '{orgunit_code}'"],
            trial_code: [f"flexistudy.code as '{trial_code}'"],
        }
        joins = {
            sampleid: self.jd["sample_to_sampleid"],
            cxxkitid: self.jd["sample_to_samplekit"],
            parentid: self.jd["sample_to_parentid"],
            kitid: self.jd["sample_to_samplekit"],
            locationname: self.jd["sample_to_samplelocation"],
            locationpath: self.jd["sample_to_samplelocation"],
            sampletype_code: self.jd["sample_to_sampletype"],
            stockprocessing_code: self.jd["sample_to_stockprocessing"],
            secondprocessing_code: self.jd["sample_to_secondprocessing"],
            project_code: self.jd["sample_to_project"],
            patientid: self.jd["sample_to_patientid"],
            receptacle_code: self.jd["sample_to_receptacle"],
            orgunit_code: self.jd["sample_to_orgunit"],
            trial_code: self.jd["sample_to_trial"]
        }
        selectstr = self._selectstr(selects, verbose, ["sample.*"], idc)  
        joinstr = self._joinstr(joins, verbose, idc)  
        (wherestr, whereargs) = self._where(sampleids=sampleids, idc=idc, patientids=patientids, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, dtypes=dtypes, verbose=verbose, like=like, wherearg=where) 
        topstr = self._top(top)
        query = f"select {topstr} {selectstr} from centraxx_sample sample {joinstr} where {wherestr}"
        if order_by is not None:
            query += f" order by {order_by}"
        if print_query:
           print(query)
        #print(whereargs)
        res = self.db.qfad(query, whereargs)

        return res
    def patient(self, patientids=None, trials=None, orgunits=None, idc=None, verbose=[], verbose_all=False, like=[], order_by=None, top=None, print_query=False):
        """
        patient gives patients.
        """
        # print("try:" + tr.sampleid)
        vaa = [patientid, trial_code, orgunit_code]
        if not patientid in verbose:
            verbose.insert(0, patientid)
        silent = []
        if trials:
            silent.append(trial_code)
        if orgunits:
            silent.append(orgunit_code)
        if idc:
            silent.append(sampleid)
        if verbose_all == True:
            verbose = vaa
        if not _checkverbose(verbose, vaa + self.settings["idc"] + [sampleid]):
            return None # throw error?
        selects = {
            patientid: [f"patidc.psn as '{patientid}'"],
            orgunit_code: [f"organisationunit.code as '{orgunit_code}'"],
            trial_code: [f"flexistudy.code as '{trial_code}'"],
        }
        joins = {
            patientid: self.jd["patient_to_patientid"],
            orgunit_code: self.jd["patient_to_orgunit"],
            sampleid: self.jd["patient_to_sample"] + self.jd["sample_to_sampleid"], # add sample_to_sampleid to not mess up where clause for now
            trial_code: self.jd["patient_to_trial"]
        }
        selectstr = self._selectstr(selects, verbose, ["patientcontainer.*"], idc)  
        joinstr = self._joinstr(joins, verbose + silent, idc)  
        (wherestr, whereargs) = self._where(patientids=patientids, trials=trials, idc=idc, verbose=verbose, like=like) 
        topstr = self._top(top)
        query = f"select distinct {topstr} {selectstr} from centraxx_patientcontainer patientcontainer {joinstr} where {wherestr}"
        if order_by is not None:
            query += f" order by {order_by}"
        if print_query:
           print(query)
        res = self.db.qfad(query, whereargs)
        return res
    def trial(self):
        """
        trial gives trials.
        """
        query = "select code from centraxx_flexistudy"
        res = self.db.qfad(query)
        return res
    def finding(self, sampleids=None, methods=None, trials=None, patientids=None, verbose=[], verbose_all=False):
        """
        finding gets the laborfinding (messbefund / begleitschein) for
        sampleid or messbefund.  (if verbose with its recorded values?)
        """
        query = f"""select laborfinding.oid as "laborfinding_oid", laborfinding.*, labormethod.code as {method_code}, sidc.psn as {sampleid}
        from centraxx_laborfinding as laborfinding

        -- go from laborfinding to sample
        left join centraxx_labormethod as labormethod on laborfinding.labormethod = labormethod.oid
        left join centraxx_labormapping as labormapping on labormapping.laborfinding = laborfinding.oid
        left join centraxx_sample sample on labormapping.relatedoid = sample.oid
        left join centraxx_sampleidcontainer sidc on sidc.sample = sample.oid"""
        (wherestr, whereargs) = self._where(sampleids=sampleids, methods=methods, trials=trials)

        query += " where " + wherestr
        #print(query)
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
    def method(self, methods=None):
        """
        method (messprofil) gets method(s) and their labvals (messparameter).
        """
        query = f"""select laborvalue.*, labormethod.code as "method_code"
from centraxx_labormethod labormethod
inner join centraxx_crftemplate crf_t
    on labormethod.crf_template=crf_t.oid
inner join centraxx_crftempsection crf_ts
    on crf_t.oid=crf_ts.crftemplate
inner join centraxx_crftempsection_fields crf_tsf
    on crf_ts.oid=crf_tsf.crftempsection_oid
inner join centraxx_crftempfield crf_tf
    on crf_tsf.crftempfield_oid=crf_tf.oid
inner join centraxx_laborvalue laborvalue
    on crf_tf.laborvalue=laborvalue.oid"""
        (wherestr, whereargs) = self._where(methods=methods)

        if wherestr:
          query += " where " + wherestr
        # print(query)
        res = self.db.qfad(query, whereargs)
        out = {}
        for row in res:
          mc = row[method_code]
          if mc not in out:
            out[mc] = {}
          del row[method_code]
          out[mc] = row
        
        return out
    def name(self, table:str, code:str=None, lang:str=None, ml_table:str=None):
        """
        name gives the multilingual names for a code or all codes in a table.
        
        the result is keyed by code and language like this:
        
        
        "NUM_NMR_ISOLEUCINE_VALUE": {  
           "de": "Isoleucin",  
           "en": "Isoleucine"  
        }
        
        
        table: the name of the centraxx table without centraxx_ prefix  
        code: a specific code, if none given, all code - name mappings for table are given  
        lang: de|en  
        ml_table: if the name of the table connecting to multilingualentry is not simlpy the queried table name followed by "_ml_name", give the connecting table's name here. eg: name('laborvaluegroup', ..., ml_name='labval_grp_ml_name')  
        """
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

    def _selectstr(self, selects, verbose, selecta, idc):
        """
        _selectstr filters the selects by the verbose array and returns the
        sql select string. selecta is for fields that should be selected
        regardless if they're in the verbose array or not.
        
        the idc argument assumes that the sample table is joined it.
        """
        for verb in verbose:
            if not verb in selects:
                continue
            for s in selects[verb]:
                selecta.append(s)
        selecta = self._append_idc_select(selecta, idc, verbose)
        selectstr = ", \n".join(selecta)
        return selectstr
    def _joinstr(self, joins, verbose, idc):
        """
        _joinstr filters the joins by the verbose array and returns the sql join string.
        
        the idc argument assumes that the sample table is joined in.
        """
        joina = []
        for verb in verbose:
            if not verb in joins:
                continue
            for s in joins[verb]:
                if not s in joina:
                    joina.append(s)
        joina = self._append_idc_join(joina, idc, verbose)
        joinstr = "\n ".join(joina)
        return joinstr
    def _append_idc_select(self, selecta, idc, verbose):
        """
        _append_idc_select adds the sql select statements for an idc dict.
        """
        idca = []
        for verb in verbose:
          if verb in self.settings["idc"]:
            idca.append(verb)
        for item in idca:
          selectstr = f"idc_{item}.psn as '{item}'"
          if not selectstr in selecta:
            selecta.append(selectstr)
        return selecta
    def _append_idc_join(self, joina, idc, verbose):
        """
        _append_idc_join adds the sql join statements for an idc dict.
        """
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
    def _where(self, sampleids=None, idc={}, patientids=None, trials=None, locationpaths=None, kitids=None, cxxkitids=None, dtypes=None, methods=None, like=[], verbose=[], wherearg:str=None): # -> (str, [])
        """
        _where returns the wherestring and args array for the provided arguments (that are not None).
        the user needs to make sure that whatever is referenced here is joined into the query before.
        the names are assumed to be the tr constants, like e.g. tr.sampleid.
        like is an array of tr constants of the arguments for which we check likeness. we only check likeness for the first passed string of an argument array. if for example like=[tr.locationpath], we check likeness of locationpaths[0].
        
        make sure only one of sampleids or extsampleids is passed?
        """
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
        if wherearg is not None:
           wherestr += " and (" + wherearg + ")"
        return (wherestr, whereargs)
    def _wherebuild(self, wheredict, likearr=[], verbose=[]): # ([]string, [])
        """
        _wherebuild builds wherestrings and fills whereargs.
        """
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
        """
        _sqlinplaceholder returns a string like (?, ?, ?, ? ...) with n question marks for sql in.
        """

        # put this in a package sqlutil?

        out = "("
        for i in range(n):
            out += "?"
            if i < n - 1:
                out += ","
        out += ")"
        return out
    def _whereparam(self, name, like:bool=None):
        """
        _whereparam gives a ?-parameterized sql where expression for name
        equal or like parameter for use in queries.
        """
        if like == None or like == False:
            return name + " = ?"
        else:
            return name + " like '%' + ? + '%'"
    def _wherelike(self, name):
        """
        _wherelike gives a ?-parameterized sql where like expression.
        """
        return name + " like '%' + ? + '%'"

    def _wherelikes(self, fieldarr):
        """
        _wherelikes gives a ?-parameterized sql of or-joined where-like expressions.
        """
        a = []
        for f in fieldarr:
            a.append(f + " like '%' + ? + '%'") # the sql takes literal plusses like here
        return " or ".join(a)
    def _top(self, top):
        """
        _top returns the top string, for, e.g. `select top 100 * from table`, if
        top is None return an empty string.
        """
        if top is not None:
           return f"top {top}"
        return ""
    def _idcinit(self):
        """
        _idcinit makes a mapping of idcontainers from their code (lower-case) to respective oid and kind.
        """
        query = "select code, oid, kind from centraxx_idcontainertype"
        res = self.db.qfad(query)
        self._idcoid = {}
        self._idckind = {}
        for row in res:
          self._idcoid[row["code"].lower()] = row["oid"]
          self._idckind[row["code"].lower()] = row["kind"]
