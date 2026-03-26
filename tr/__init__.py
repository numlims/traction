# automatically generated, DON'T EDIT. please edit init.ct from where this file stems.
from dbcq import dbcq
import cnf
from dip import dig
from tram import Sample, Idable, Amount, Identifier
from tram import Patient
from tram import Finding
from tram import Rec, BooleanRec, NumberRec, StringRec, DateRec, MultiRec, CatalogRec
from tram import User
import re
import csv
import sys
address = "address"
appointment = "appointment"
catalog = "catalog"
category = "category" # MASTER, ALIQUOTGROUP, DERIVED. dtype in db.
concentration = "concentration"
cxxkitid = "cxxkitid"
creationdate = "creationdate" 
derivaldate = "derivaldate" # aufteilungsdatum / date of distribution
email = "email"
initialamount = "initialamount"
initialunit = "initialunit"
first_repositiondate = "first_repositiondate" # datum der ersten einlagerung / date of first storage (not in fhir). is identical to derivaldate. first_repositiondate in db.
method = "method"
kitid = "kitid"
labval = "labval"
lastlogin = "lastlogin"
login = "login"
locationname = "locationname"
locationpath = "locationpath"
orga = "orga"
parentid = "parentid"
parentoid = "parentoid"
patientid = "patientid"
project = "project"
receiptdate = "receiptdate" # eingangsdatum / date of receipt. receiptdate in db.
receptacle = "receptacle"
repositiondate = "repositiondate" # datum der letzten einlagerung / most recent storage date. 
restamount = "restamount"
restunit = "restunit"
sampleid = "sampleid"
sampleoid = "sampleoid"
samplingdate = "samplingdate" # entnahmedatum / extraction date.
secondprocessing = "secondprocessing"
secondprocessingdate = "secondprocessingdate"
stockprocessing = "stockprocessing"
stockprocessingdate = "stockprocessingdate"
trial = "trial"
type = "type" # sampletype (EDTA, stool etc) in db.
username = "username"
values = "values"
xposition = "xposition"
yposition = "yposition"
cnftemplate = """
# settings for traction.

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

# cxx holds the centraxx version for db target
cxx:
  <db target>: 3|4
"""

def _checkverbose(verbose, possible):
    """
     _checkverbose makes shure that only allowed keys are in the verbose array. 
    """
    for verb in verbose:
        if verb not in possible: 
            print(f"error: verbose entry {verb} must be in {possible}.")
            return False
    return True
def floatornull(x):
    """
     floatornull casts to float or returns None. somehow the values passed
     to Amount need float casts, and float casts don't accept None.
    """
    if x is None:
        return None
    return float(x)
def get_ids(idables:list, code:str|None=None) -> list:
    """
     get_ids returns a list of string ids from a list of Idables (Sample or
     Patient).
    """
    return [ x.id(code) for x in idables ]
def isnumber(a) -> bool:
    """
     isnumber returns if a string is a number to prevent sql injection.  is
     this handled better by an existing library function?
    """
    return re.match(r"^[0-9](.[0-9]*)?$", a) is not None
def isidentifier(a) -> bool:
    """
     isidentifier returns whether a string is a sql identifier to prevent
     sql injection.  like isnumber, could this be handled better by a library?
    """
    return re.match(r"^[A-Za-z_0-9\.#]+$", a) is not None
def _dextend(d:dict, key, lst:list|None):
    """
     _dextends extends an array in a dictionary at the given key with the
     values in the passed list.
    """
    if lst is not None:
        if key not in d:
            d[key] = []
        d[key].extend(lst)
def _tablelists(all:dict, cutoff:int): # -> (dict, dict)
    """
     _tablelists returns a dict of the lists smaller than cutoff and a
     second dict of the lists larger than cutoff that go into temporary
     tables.
    """
    outsmall = {}
    outlarge = {}
    for key, lst in all.items():
        if lst is not None and len(lst) > cutoff:
            outlarge[key] = lst
        else:
            outsmall[key] = lst
    return outsmall, outlarge
def _uniq(lst): # -> list
    """
     _uniq returns a new list containing the unique items of the list passed, preserving order.
    """
    out = []
    for e in lst:
        if e not in out:
            out.append(e)
    return out
def _byifone(alllists):
    """
     _byifone sets by to the only passed query parameter, if missing is
     true and there is only one query parameter.
    """
    throwtogether = list(alllists["idc"].keys()) + list(alllists["nonidc"].keys())
    if len(throwtogether) == 1:
        return throwtogether[0]
    else:
        raise Exception("--missing needs a tr constant or idc passed to --by")
def _prepby(alllists:dict, by:str=None, missing:bool=None):
    """
     _prepby returns a bydict that holds the query params for the by as key
     (if there are any), and a second list, missinglst, that holds these
     query params so that they can subsequently be deleted so that the
     truly missing remain.
    """
    bydict = None
    missinglst = None
    if by is not None:
        if missing:
            missinglst = []
            # todo wrap this in function: missinglst =  idc_or_not(alllists, by)
            if by in alllists["idc"]:
                missinglst = alllists["idc"][by]
            elif by in alllists["nonidc"]:
                missinglst = alllists["nonidc"][by]
        else:
            bydict = {}
            if by in alllists["idc"]:
                for byval in alllists["idc"][by]:
                    bydict[byval] = []
            if by in alllists["nonidc"]:
                for byval in alllists["nonidc"][by]:
                    bydict[byval] = []
    return bydict, missinglst
def _fillby(bydict, by, row, what):
    """
     _fillby puts a value into the bydict at the key of the by-field.
    """
    if bydict is not None:
        bykey = dig(row, by.lower())
        if bykey is not None and not bykey in bydict:
            bydict[bykey] = []
        bydict[bykey].append(what)
def _updatemissing(missinglst, by, row):
    """
     _updatemissing removes the value at the by-field from the missing list.
    """
    bykey = dig(row, by.lower())
    if bykey in missinglst:
        missinglst.remove(bykey)

def dict_csv(lst:list, colnames=None, outfile=None, delim:str=",") -> str|None:
    """
     dict_csv writes a list of dicts to csv file. if no column names are
     given, the fields in the first dict are used as column names.
    """
    if delim is None:
        delim = ","
    if lst is None or len(lst) == 0: # todo throw error?
        return None
    out = sys.stdout 
    if isinstance(outfile, str):
        out = open(outfile, "w", newline="")
    if colnames is None:
        colnames = list(lst[0].keys())
    
    writer = csv.DictWriter(out, fieldnames=colnames, delimiter=delim) 
    writer.writeheader()
    for d in lst:
        writer.writerow(d)
    out.close()
    return outfile
def flat_csv(lst:list, outfile=None, delim:str=",") -> str|None:
    """
     flat_csv writes a list of 'flat' tram objects like User (that don't
     need to pull in nested data into their dict root) to csv file.
    """
    if delim is None:
        delim = ","
    if lst is None or len(lst) == 0: # todo throw error?
        #print("no idables")
        return None
    rows = []
    for e in lst:
        rows.append(e.__dict__)
    return dict_csv(rows, outfile=outfile, delim=delim)    
def idable_csv(idables:list, outfile=None, delim:str=",", *idcs) -> str|None:
    """
     idable_csv writes a list of Idables to the given csv file. the given
     idcontainers become columns in the csv. if no idcontainers are given,
     all are included. if True is passed as file, the output is
     printed. (todo pass sys.stdout instead?)
    """
    if delim is None:
        delim = ","
    if idables is None or len(idables) == 0: # todo throw error?
        #print("no idables")
        return None
    colnames = []
    for idable in idables:
        for col in list(idable.iddict(*idcs).keys()):
            if col not in colnames:
                colnames.append(col)
    rows = []
    for idable in idables:
        d = idable.iddict(*idcs)
        rows.append(d)
    return dict_csv(rows, colnames=colnames, outfile=outfile, delim=delim)    
def finding_csv(findings:list, outfile=None, delim:str=",", delim_cmp:str=",") -> str:
    """
     finding_csv writes a list of Findings along their recorded values to
     the given csv file, the recorded values in the same row as their
     respective finding. if True is passed as file the output is printed. todo use sys.stdout instead of True.
    """
    if delim is None:
        delim = ","
    if delim_cmp is None:
        delim_cmp = ","
    if findings is None or len(findings) == 0: # todo throw error?
        print("no findings")
        return None
    fdicts = []
    colnames = []

    for finding in findings:
        fdict = finding.__dict__.copy()
        del fdict["recs"]
        if len(colnames) == 0:
            colnames.extend(list(fdict.keys()))
        for code, rec in finding.recs.items():
            tkey = f"cmp_t_{rec.labval}"
            vkey = f"cmp_v_{rec.labval}"
            if tkey not in colnames:
                colnames.append(tkey)
            if vkey not in colnames:
                colnames.append(vkey)
            if isinstance(rec, BooleanRec):
                fdict[tkey] = "BOOL"
                fdict[vkey] = rec.rec
            if isinstance(rec, NumberRec):
                fdict[tkey] = "NUMBER"
                fdict[vkey] = rec.rec
            if isinstance(rec, StringRec):
                fdict[tkey] = "STRING"
                fdict[vkey] = rec.rec
            if isinstance(rec, DateRec):
                fdict[tkey] = "DATE"
                fdict[vkey] = rec.rec
            if isinstance(rec, MultiRec):
                fdict[tkey] = "MULTI"
                fdict[vkey] = delim_cmp.join(rec.rec)
            if isinstance(rec, CatalogRec):
                fdict[tkey] = "CATALOG"
                fdict[vkey] = delim_cmp.join(rec.rec)
                
        fdicts.append(fdict)
    return dict_csv(fdicts, colnames=colnames, outfile=outfile, delim=delim)    
def method_csv(methods:list, outfile=None, delim:str=",", delim_usageentry:str=",") -> str:
    """
     method_csv writes a list of Methods to the given csv file, one row per labval in the method. if True is passed as file the output is printed. todo use sys.stdout instead of True.
    """
    if delim is None:
        delim = ","
    if delim_usageentry is None:
        delim_usageentry = ","
    if methods is None or len(methods) == 0: # todo throw error?
        return None
    rows = []
    colnames = { "method": None, "method_de": None, "method_en": None, "labval": None, "labval_en": None, "labval_de": None, "labval_type": None }

    for method in methods:
        for labval in method["labvals"].values():
            row = {}
            row["method"] = method["code"]
            row["method_de"] = method["name_de"]
            row["method_en"] = method["name_en"]
            row["labval"] = labval["code"]
            row["labval_de"] = labval["name_de"]
            row["labval_en"] = labval["name_en"]
            row["labval_type"] = labval["type"]
            if "catalog" in labval:
                if "labval_catalog" not in colnames:
                    colnames["labval_catalog"] = None
                row["labval_catalog"] = labval["catalog"]
            if "usageentry" in labval:
                if "labval_usageentry" not in colnames:
                    colnames["labval_usageentry"] = None
                row["labval_usageentry"] = delim_usageentry.join(list(labval["usageentry"].keys()))
            rows.append(row)
    return dict_csv(rows, colnames=list(colnames.keys()), outfile=outfile, delim=delim)
def catalog_csv(catalogs:list, outfile=None, delim:str=",") -> str:
    """
     catalog_csv writes a list of catalog dicts to the given csv file, one
     row per entry in the catalog. if True is passed as file the output is
     printed. todo use sys.stdout instead of True.
    """
    if delim is None:
        delim = ","
    if catalogs is None or len(catalogs) == 0: # todo throw error?
        return None
    rows = []
    for catalog in catalogs:
        for entry in catalog["entries"].values():
            row = {}
            row["catalog"] = catalog["code"]
            row["catalog_de"] = catalog["name_de"]
            row["catalog_en"] = catalog["name_en"]
            row["entry"] = entry["code"]
            row["entry_de"] = entry["name_de"]
            row["entry_en"] = entry["name_en"]
            rows.append(row)
    return dict_csv(rows, outfile=outfile, delim=delim)

class traction:
    def __init__(self, target):
        """
         __init__ takes the db target either as string or dbcq object.
        """
        self.settings = cnf.makeload(path=".traction/settings.yaml", root=cnf.home, fmt="yaml", make=cnftemplate)        
        if self.settings is None:
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
        self.jd = {
            "sample_to_samplekit": [f"left join centraxx_samplekititem as samplekititem on samplekititem.tubebarcode = idc_{self.sidc()}.psn", "left join centraxx_samplekit as samplekit on samplekit.oid = samplekititem.samplekit"],
            "sample_to_parentid": [f"left join centraxx_sampleidcontainer parentidc on parentidc.sample = sample.parent and parentidc.idcontainertype={self._idcoid[self.sidc()]}"],
            "sample_to_samplelocation": ["left join centraxx_samplelocation samplelocation on samplelocation.oid = sample.samplelocation"],
            "sample_to_sampletype": ["left join centraxx_sampletype as sampletype on sampletype.oid = sample.sampletype"],
            "sample_to_stockprocessing": ["left join centraxx_stockprocessing as stockprocessing on sample.stockprocessing = stockprocessing.oid"],
            "sample_to_secondprocessing": ["left join centraxx_stockprocessing as secondprocessing on sample.secondprocessing = secondprocessing.oid"],
            "sample_to_project": ["left join centraxx_project as project on sample.project = project.oid"],
            "sample_to_patient": ["left join centraxx_patientcontainer as patientcontainer on sample.patientcontainer = patientcontainer.oid"],
            "sample_to_receptacle": ["left join centraxx_samplereceptable as receptable on sample.receptable = receptable.oid"], # receptable seems to be a typo in the table naming
            "sample_to_orga": ["left join centraxx_organisationunit as organisationunit on sample.orgunit = organisationunit.oid"],
            "sample_to_trial": ["left join centraxx_flexistudy as flexistudy on sample.flexistudy = flexistudy.oid"]
            ,
            "patient_to_orga": ["left join centraxx_patientorgunit patientorgunit on patientcontainer.oid=patientorgunit.patientcontainer_oid", "left join centraxx_organisationunit organisationunit on patientorgunit.orgunit_oid=organisationunit.oid"],
            "patient_to_trial": ["left join centraxx_patientstudy as patientstudy on patientstudy.patientcontainer = patientcontainer.oid", "left join centraxx_flexistudy as flexistudy on flexistudy.oid = patientstudy.flexistudy"],
            "patient_to_sample": ["left join centraxx_sample sample on sample.patientcontainer = patientcontainer.oid"]
            ,
            "participant_to_address": ["left join centraxx_participantaddress participantaddress on participantaddress.participant = participant.oid", "left join centraxx_address address on address.oid = participantaddress.oid"],
            "participant_to_credential": ["left join centraxx_credential credential on credential.participant = participant.oid"]
            ,
            "usageentry_to_labval": [ "left join centraxx_labvalenum_usageentry labvalenum_usageentry on labvalenum_usageentry.usageentry = usageentry.oid", "left join centraxx_laborvalue labval on labvalenum_usageentry.labvalueenum = labval.oid" ]
        }
        self.names_labval = None
        self.names_catalogentry = None
        self.names_usageentry = None

    def sample(self, sampleids:list|None=None, oids:list|None=None, idc:dict|None=None, patientids:list|None=None, pidc:str|None=None, parentids:list|None=None, parentoids:list|None=None, locationpaths:list|None=None, locationnames:list|None=None, trials:list|None=None, kitids:list|None=None, cxxkitids:list|None=None, categories:list|None=None, types:list|None=None, orgas:list|None=None, samplingdates:list|None=None, receiptdates:list|None=None, derivaldates:list|None=None, first_repositiondates:list|None=None, repositiondates:list|None=None, stockprocessingdates:list|None=None, secondprocessingdates:list|None=None, files:dict|None=None, verbose:list|None=None, verbose_all:bool=False, primaryref:bool=False, incl_parents:bool=False, incl_childs:bool=False, incl_tree:bool=False, like:list|None=None, missing=False, order_by:str|None=None, top:int|None=None, by=None, print_query:bool=False, raw:bool=False):
        """
         sample gets sample(s) and returns them as a list of Sample instances.
         
         pass sampleids and other values to filter for as lists of strings,
         e.g. `sampleids=["a", "b", "c"]`.
         
         pass idcontainer lists to idc, like `idc={"extsampleid": ["a", "b", "c"]}`.
         
         pass fields that should be joined in into the verbose array, e.g.
         `verbose=[tr.locationpath]`. to join in everything, say
         `verbose_all=True`. this is slower than non-verbose.
         
         pass dates as a tuple of from and to datetime, e.g. `samplingdates=(datefrom, None)`.
         
         to match via like as opposed to exact, pass the respective tr
         constants or idcs to like, e.g. `like=[tr.locationpath]`.
         
         pass `by` to key returned samples by that tr constant or idc. if
         missing is also passed, only missings are returned.
        """
        if verbose is None:
            verbose = []
        if like is None:
            like = []
        if files is None:
            files = {}
        if idc is None:
            idc = {}
        vaa = [cxxkitid, kitid, locationname, locationpath, orga, parentid, patientid,
               project, receptacle, type,
               secondprocessing, stockprocessing, trial]
        vaa.extend(self._pidcs(pidc))
        vaa.extend(self._sidcs())                
        if self.sidc() not in verbose:
            verbose.insert(0, self.sidc())
        if verbose_all:
            verbose = vaa
        verbose = self._concrete_idcs(verbose, pidc=pidc)
        files = self._concrete_idcs_dict(files, pidc=pidc)        
        if not _checkverbose(verbose, vaa): 
            raise Exception(f"verbose keys {verbose} need to be in {vaa}.")
        if incl_parents or incl_childs or incl_tree or primaryref:
            verbosepass = []
            if primaryref:
                verbosepass = verbose
            res = self.sample(sampleids=sampleids, idc=idc, parentids=parentids, parentoids=parentoids, patientids=patientids, pidc=pidc, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, categories=categories, samplingdates=samplingdates, receiptdates=receiptdates, derivaldates=derivaldates, first_repositiondates=first_repositiondates, repositiondates=repositiondates, stockprocessingdates=stockprocessingdates, secondprocessingdates=secondprocessingdates, verbose=verbosepass, verbose_all=False, like=like, missing=missing, order_by=order_by, top=top, print_query=print_query)
            if primaryref:
                for sample in res:
                    self._fill_in_primary(sample)
                return res
            
            s_oids = get_ids(res, "oid")
            withincl = []
            for s_oid in s_oids:
               if incl_parents:
                   p_oids = []
                   self._get_parents(s_oid, p_oids)
                   withincl.extend(p_oids)
                   withincl.append(s_oid)
               if incl_childs:
                   c_oids = []
                   self._get_childs(s_oid, c_oids)
                   withincl.append(s_oid)
                   withincl.extend(c_oids)
               if incl_tree:
                   p_oids = []
                   self._get_parents(s_oid, p_oids)
                   if len(p_oids) > 0:
                       root = p_oids[0]
                   else:
                       root = s_oid
                   c_oids = []
                   self._get_childs(root, c_oids)
                   withincl.append(root)
                   withincl.extend(c_oids)
            withincl = list(dict.fromkeys(withincl))
            return self.sample(oids=withincl, verbose=verbose, print_query=print_query, raw=raw) # todo pass verbose_all?
        lists = {
          sampleoid: oids,
          parentid: parentids,
          parentoid: parentoids,
          locationpath: locationpaths,
          locationname: locationnames,
          trial: trials,
          kitid: kitids,
          cxxkitid: cxxkitids,
          category: categories,
          orga: orgas,
          samplingdate: samplingdates,
          receiptdate: receiptdates,
          derivaldate: derivaldates,
          first_repositiondate: first_repositiondates,
          repositiondate: repositiondates,
          stockprocessingdate: stockprocessingdates,
          secondprocessingdate: secondprocessingdates,
          type: types
        }
        _dextend(idc, self.sidc(), sampleids)
        _dextend(idc, self.pidc(pidc), patientids)
        alllists = self._makealllists(lists, idc, files)
        (nontable, table) = self._makemove(alllists, 50)
        jselects = {
            self.sidc(): [f"idc_{self.sidc()}.psn as '{sampleid}'"],
            self.pidc(pidc): [f"idc_{self.pidc(pidc)}.psn as '{patientid}'"],                   
            cxxkitid: [f"samplekit.cxxkitid as '{cxxkitid}'"],
            #sampleid: [f"sidc.psn as '{sampleid}'"],
            parentid: [f"parentidc.psn as '{parentid}'"],
            kitid: [f"samplekit.kitid as '{kitid}'"],
            locationname: [f"samplelocation.locationid as '{locationname}'"], 
            locationpath: [f"samplelocation.locationpath as '{locationpath}'"],
            type: [f"sampletype.code as '{type}'"], # is there a type field already?
            stockprocessing: [f"stockprocessing.code as '{stockprocessing}'"],
            secondprocessing: [f"secondprocessing.code as '{secondprocessing}'"],
            project: [f"project.code as '{project}'"],
            #patientid: [f"patidc.psn as '{patientid}'"],
            receptacle: [f"receptable.code as '{receptacle}'"],
            orga: [f"organisationunit.code as '{orga}'"],
            trial: [f"flexistudy.code as '{trial}'"],
        }
        lselects = [
          f"sample.amountrest as {restamount}",
          f"sample.appointmentnumber as {appointment}",
          f"sample.dtype as {category}",
          f"sample.oid as {sampleoid}",
          f"sample.parent as {parentoid}",
          "sample.*"
        ]
        selectstr = self._selectstr(jselects, lselects, nontable, table, verbose)
        joins = {
            cxxkitid: self.jd["sample_to_samplekit"],
            parentid: self.jd["sample_to_parentid"],
            kitid: self.jd["sample_to_samplekit"],
            locationname: self.jd["sample_to_samplelocation"],
            locationpath: self.jd["sample_to_samplelocation"],
            type: self.jd["sample_to_sampletype"],
            stockprocessing: self.jd["sample_to_stockprocessing"],
            secondprocessing: self.jd["sample_to_secondprocessing"],
            project: self.jd["sample_to_project"],
            receptacle: self.jd["sample_to_receptacle"],
            orga: self.jd["sample_to_orga"],
            trial: self.jd["sample_to_trial"]
        }
        for pidc in self._pidcs(pidc):
            joins[pidc] = self.jd["sample_to_patient"]
        joinstr = self._joinstr(joins, nontable, table, verbose, pidc=pidc)
        (wherestr, whereargs) = self._where(nontable, table, like=like)
        topstr = self._top(top)
        query = f"select {topstr} {selectstr} from centraxx_sample sample \n{joinstr}"
        if wherestr.strip() != "":
            query += f"\nwhere {wherestr}"
        if order_by is not None:
            query += " " + self._order_by(order_by)
            
        if print_query:
           print(query)
           print(whereargs)

        res = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])
        if raw:
            return res
        if missing and by is None:
            by = _byifone(alllists)
        bydict, missinglst = _prepby(alllists, by, missing)
        sarr = []
        for r in res:
            ids = []
            #if dig(r, sampleid) is not None:
            #    ids.append(Identifier(id=dig(r, sampleid), code=self.sidc()))
            for idc in self._sidcs():
                #print("idc:" + idc)
                #print("r:" + str(r))
                if idc.lower() in r and r[idc.lower()] is not None:
                    ids.append( Identifier(id=dig(r, idc.lower()), code=idc.upper()) )
            ids.append( Identifier(id=int(dig(r, sampleoid)), code="oid") ) # todo rename sampleoid?
            pids = []
            if r[parentoid] is not None:
                pids.append(Identifier(id=int(r[parentoid]), code="oid"))
            if dig(r, parentid) is not None:
                pids.append(Identifier(id=dig(r, parentid), code=self.sidc()))
            parent = None
            if len(pids) > 0:
                parent = Idable(ids=pids, mainidc=self.sidc())
            patids = []
            for idc in self._pidcs(pidc):
                if idc.lower() in r and r[idc.lower()] is not None:
                    patids.append( Identifier(id=dig(r, idc.lower()), code=idc.upper()) )

            patient = None
            if len(patids) > 0:
                patient = Idable(ids=patids, mainidc=self.pidc(pidc))
            s = Sample(
                appointment=dig(r, appointment),
                category=dig(r, category),
                samplingdate=dig(r, samplingdate),
                concentration=dig(r, concentration),
                cxxkitid=dig(r, cxxkitid),
                creationdate=dig(r, creationdate),
                derivaldate=dig(r, derivaldate),
                ids=Idable(ids=ids, mainidc=self.sidc()),
                initialamount=Amount(floatornull(dig(r, initialamount)), dig(r, initialunit)), # apparently the cast to float is explicitly needed
                kitid=dig(r, kitid),
                locationpath=dig(r, locationpath),
                locationname=dig(r, locationname),
                orga=dig(r, orga),
                parent=parent,
                patient=patient,
                project=dig(r, project),
                receiptdate=dig(r, receiptdate),
                receptacle=dig(r, receptacle),
                repositiondate=dig(r, repositiondate),
                restamount=Amount(floatornull(dig(r, restamount)), dig(r, restunit)),
                secondprocessing=dig(r, secondprocessing),
                secondprocessingdate=dig(r, secondprocessingdate),
                stockprocessing=dig(r, stockprocessing),
                stockprocessingdate=dig(r, stockprocessingdate),
                trial=dig(r, trial),
                type=dig(r, type), 
                xposition=dig(r, xposition), 
                yposition=dig(r, yposition)
            )
            if by is not None:
                if missing:
                    _updatemissing(missinglst, by, r)
                _fillby(bydict, by, r, s)
            else:
                sarr.append(s)
        if by is not None:
            if missing:
                return missinglst
            else:
                return bydict
        else:
            return sarr
    def _get_parents(self, oid, out):
        """
         _get_parents collects the parent sample oids of a sample in the `out`
         list, in order from root to leaf. take oids to include aliquotgroups,
         they don't necessarily have an idcontainer attached to them.
        """
        res = self.db.qfad("select parent from centraxx_sample where oid = ?", oid)
        pid = dig(res[0], "parent")
        if pid is not None:
            out.insert(0, pid)
            self._get_parents(pid, out)
    def _get_childs(self, oid, out):
        """
         _get_childs collects the oids of the sample's children in the `out`
         list, in order from root-to-leaf. take oids to include aliquotgroups.
        """
        res = self.db.qfad("select oid from centraxx_sample where parent = ?", oid)
        for child in res:
            out.append(child["oid"])
            self._get_childs(child["oid"], out)
    def patient(self, patientids:list|None=None, pidc:str|None=None, sampleids:list|None=None, idc:dict|None=None, trials:list|None=None, orgas:list|None=None, files:dict|None=None, verbose:list|None=None, verbose_all:bool=False, like:list|None=None, order_by:str|None=None, top:int|None=None, by:str=None, missing:bool=False, print_query:bool=False, raw:bool=False):
        """
         patient gets patients and returns them as a list of Patient instances.
         
         the parameters work analog to the sample method.
        """
        if verbose is None:
            verbose = []
        if like is None:
            like = []
        if files is None:
            files = {}
        if idc is None:
            idc = {}
        vaa = [orga]
        vaa.extend(self._pidcs(pidc))        
        if self.pidc(pidc) not in verbose:
            verbose.insert(0, self.pidc(pidc))
        verbose = self._concrete_idcs(verbose, pidc=pidc)
        files = self._concrete_idcs_dict(files, pidc=pidc)
        lists = {
          trial: trials,
          orga: orgas
        }
        _dextend(idc, self.sidc(), sampleids)
        _dextend(idc, self.pidc(pidc), patientids)
        alllists = self._makealllists(lists, idc, files)
        (nontable, table) = self._makemove(alllists, 50)
        if verbose_all:
            verbose = vaa
        if not _checkverbose(verbose, vaa):
            return None # throw error?
        selects = {
            self.pidc(pidc): [f"idc_{self.pidc(pidc)}.psn as '{patientid}'"],
            orga: [f"organisationunit.code as '{orga}'"],
            trial: [f"flexistudy.code as '{trial}'"],
        }
        joins = {
            orga: self.jd["patient_to_orga"],
            trial: self.jd["patient_to_trial"]
        }
        for sidc in self._sidcs():
            joins[sidc] = self.jd["patient_to_sample"]
        selectstr = self._selectstr(selects, ["patientcontainer.*"], nontable, table, verbose, pidc=pidc)
        joinstr = self._joinstr(joins, nontable, table, verbose, pidc=pidc)  
        (wherestr, whereargs) = self._where(nontable, table, like=like)
        #print(whereargs)
        topstr = self._top(top)
        query = f"select distinct {topstr} {selectstr} from centraxx_patientcontainer patientcontainer \n{joinstr}"
        if wherestr.strip() != "":
            query += f"\nwhere {wherestr}"
        if order_by is not None:
            query += " " + self._order_by(order_by)
        if print_query:
           print(query)
        res = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])        
        if raw:
            return res
        if missing and by is None:
            by = _byifone(alllists)
        bydict, missinglst = _prepby(alllists, by, missing)
        pats = []
        for r in res:
            ids = []
            for idc in self._pidcs(pidc):
                if idc.lower() in r and r[idc.lower()] is not None:
                    ids.append( Identifier(id=dig(r, idc.lower()), code=idc) )
            pat = Patient(
              ids=Idable(ids=ids, mainidc=self.pidc(pidc)),
              orga=dig(r, orga)
            )
            if by is not None:
                if missing:
                    _updatemissing(missinglst, by, r)
                _fillby(bydict, by, r, pat)
            else:
                pats.append(pat)
        if by is not None:
            if missing:
                return missinglst
            else:
                return bydict
        else:
            return pats
    def trial(self):
        """
         trial gives trials.
        """
        query = "select code, study_name as name from centraxx_flexistudy"
        res = self.db.qfad(query)
        return res
    def finding(self, sampleids:list|None=None, patientids:list|None=None, pidc:str|None=None, idc:dict|None=None, methods:list|None=None, trials:list|None=None, values:bool=True, verbose:list|None=None, files:dict|None=None, verbose_all:bool=False, names:bool=False, top:int|None=None, print_query:bool=False, raw:bool=False):
        """
         finding gets the laborfindings ("messbefund" / "begleitschein") for
         sampleids or method.  it returns a list of Finding instances.
         
         you can pass these to verbose: tr.patientid  // maybe also tr.values?
        """
        if verbose is None:
            verbose = []
        if files is None:
            files = {}
        if idc is None:
            idc = {}
        vaa = [patientid] # include trial?
        if verbose_all:
            verbose = vaa
        if self.sidc() not in verbose:
            verbose.append(self.sidc())
        verbose = self._concrete_idcs(verbose, pidc=pidc)
        files = self._concrete_idcs_dict(files, pidc=pidc)
        lists = {
          method: methods,
          trial: trials
        }
        _dextend(idc, self.sidc(), sampleids)
        _dextend(idc, self.pidc(pidc), patientids)
        alllists = self._makealllists(lists, idc, files)
        (nontable, table) = self._makemove(alllists, 50)
        selects = {
            self.sidc(): [f"idc_{self.sidc()}.psn as '{sampleid}'"],
            self.pidc(pidc): [f"idc_{self.pidc(pidc)}.psn as '{patientid}'"],                   
        }
        idcselectstr = self._selectstr(selects, [], nontable, table, verbose, pidc=pidc)  
        joins = {
            trial: self.jd["sample_to_trial"]
        }
        for pidc in self._pidcs(pidc):
            joins[pidc] = self.jd["sample_to_patient"]
        idcjoinstr = self._joinstr(joins, nontable, table, verbose, pidc=pidc)
        topstr = self._top(top)
        query = f"""select {topstr} laborfinding.oid as "laborfinding_oid", laborfinding.*, labormethod.code as {method}, {idcselectstr}
        from centraxx_laborfinding as laborfinding

        -- go from laborfinding to sample
        left join centraxx_labormethod as labormethod on laborfinding.labormethod = labormethod.oid
        left join centraxx_labormapping as labormapping on labormapping.laborfinding = laborfinding.oid
        left join centraxx_sample sample on labormapping.relatedoid = sample.oid
        {idcjoinstr}"""
        (wherestr, whereargs) = self._where(nontable, table)
        if wherestr.strip() != "":
            query += f"\nwhere {wherestr}"
            
        if print_query:
            print(query)
            print(whereargs)
        results = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])        
        if names is True:
            self.names_laborvalue = self.name(table="laborvalue")
        for i, finding in enumerate(results):
            if not values: # todo put this outside of the loop?
                continue
            query = """select recordedvalue.*, laborvalue.code as laborvalue_code, laborvalue.dtype as laborvalue_type, laborvalue.custom_catalog as laborvalue_catalog_oid, unit.code as laborvalue_unit
                from centraxx_laborfinding as laborfinding

                -- go from laborfinding to recorded value
                join centraxx_labfindinglabval as labfindinglabval on labfindinglabval.laborfinding = laborfinding.oid
                join centraxx_recordedvalue as recordedvalue on labfindinglabval.oid = recordedvalue.oid"""
            if self.cxx() == "3":
                query += """--go directly to laborvalue
                join centraxx_laborvalue laborvalue on labfindinglabval.laborvalue = laborvalue.oid"""
            elif self.cxx() == "4":
                query += """                
                -- go to laborvalue via crftempfield
                join centraxx_crftempfield crftempfield on labfindinglabval.crftempfield = crftempfield.oid
                join centraxx_laborvalue laborvalue on crftempfield.laborvalue = laborvalue.oid
                """
            query += """
                --go from laborvalue to unit
                left join centraxx_unity unit on laborvalue.unit = unit.oid

                where laborfinding.oid = ?
            """
            recvals = self.db.qfad(query, finding['laborfinding_oid'])
            valsbycode = {}
            for recval in recvals:
              valsbycode[recval["laborvalue_code"]] = self._make_rec(recval, finding, names)
            results[i]["values"] = valsbycode
        if raw:
            return results
        findings = []
        for res in results:
            patids = []
            for idc in self._pidcs(pidc):
                if idc.lower() in res and res[idc.lower()] is not None:
                    patids.append( Identifier(id=dig(res, idc.lower()), code=idc.upper()) )

            patient = None
            if len(patids) > 0:
                patient = Idable(ids=patids, mainidc=self.pidc(pidc))
            finding = Finding(
                findingdate=dig(res, "findingdate"),
                method=res["method"],
                name=res["shortname"],
                patient=patient,
                recs=res["values"] if "values" in res else None, # todo None ok?
                sample=Idable(id=res[sampleid], code=self.sidc(), mainidc=self.sidc()),
                sender=None
            )
            findings.append(finding)
        return findings
    def method(self, methods:list|None=None, files:dict|None=None):
        """
         method (messprofil) gets method(s) and their labvals (messparameter).
        """
        if files is None:
            files = {}
        lists = {
          method: methods
        }
        alllists = self._makealllists(lists, {}, files)
        (nontable, table) = self._makemove(alllists, 50)
        query = """select laborvalue.code as labval, labormethod.code as "method", laborvalue.dtype as labval_type, catalog.code as catalog
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
    on crf_tf.laborvalue=laborvalue.oid
left join centraxx_catalog catalog
    on catalog.oid = laborvalue.custom_catalog"""
        (wherestr, whereargs) = self._where(nontable, table)

        if wherestr and wherestr.strip != "()":
          query += " where " + wherestr
        # print(query)
        res = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])
        methodnames = self.name(table="labormethod")
        labvalnames = self.name(table="laborvalue")
        out = {}
        for row in res:
            methodcode = row["method"]
            if methodcode not in out:
                out[methodcode] = {}
                out[methodcode]["code"] = methodcode
                out[methodcode]["name_de"] = dig(methodnames, methodcode + "/de")
                out[methodcode]["name_en"] = dig(methodnames, methodcode + "/en")
                out[methodcode]["labvals"] = {}
            labvalcode = row["labval"]

            labval = {}
            labval["code"] = labvalcode
            labval["name_de"] = dig(labvalnames, labvalcode + "/de")
            labval["name_en"] = dig(labvalnames, labvalcode + "/en")
            if dig(row, "catalog") is not None:
                labval["catalog"] = dig(row, "catalog")
            labval["type"] = row["labval_type"]
            if labval["type"] == "OPTIONGROUP" or labval["type"] == "ENUMERATION":
                labval["usageentry"] = self.usageentry(labvals=[labval["code"]])
            out[methodcode]["labvals"][labvalcode] = labval
        return out
    def user(self, usernames:list|None=None, emails:list|None=None, lastlogins:list|None=None, files:dict|None=None, verbose:list|None=None, top:int|None=None, verbose_all:bool=False, print_query:bool=False):
        """
        """
        if verbose is None:
            verbose = []
        if files is None:
            files = {}
        vaa = [address, login]
        if verbose_all:
            verbose = vaa
        lists = {
          username: usernames,
          address: emails,
          login: lastlogins
        }
        alllists = self._makealllists(lists, {}, files)
        (nontable, table) = self._makemove(alllists, 50)
        jselects = {
            address: [f"address.email as email"],
            login: [f"credential.last_login_on as lastlogin"]
        }
        lselects = [
            f"participant.username as {username}",
            f"participant.firstname as firstname",
            f"participant.lastname as lastname"
        ]
        selectstr = self._selectstr(jselects, lselects, nontable, table, verbose)
        joins = {
            address: self.jd["participant_to_address"],
            login: self.jd["participant_to_credential"]
        }
        joinstr = self._joinstr(joins, nontable, table, verbose)
        (wherestr, whereargs) = self._where(nontable, table, like=[])
        topstr = self._top(top)
        query = f"select {topstr} {selectstr} from centraxx_participant participant\n{joinstr}"
        if wherestr.strip() != "":
            query += f"\nwhere {wherestr}"
        if print_query:
            print(query)
            print(whereargs)
        res = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])        
        out = []
        for r in res:
            user = User(
                email=dig(r, email),
                lastlogin=dig(r, lastlogin),
                username=dig(r, username),
                firstname=dig(r, "firstname"),
                lastname=dig(r, "lastname")
            )
            out.append(user)
        return out
    def orga(self, names:bool=False):
        """
         orga returns organisationunits.
        """
        query = "select code from centraxx_organisationunit"
        res = self.db.qfad(query)
        names = self.name(table="organisationunit", ml_table="organisatunit_ml_name")
        for i, _ in enumerate(res):
            nam = names[res[i]["code"]]
            res[i]["name_de"] = nam["de"]
            res[i]["name_en"] = nam["en"]
        return res
    def catalog(self, catalogs:list|None=None, files:dict|None=None):
        """
         catalog gives the catalogentries per catalog.
        """
        if files is None:
            files = {}
        lists = {
            catalog: catalogs
        }
        alllists = self._makealllists(lists, {}, files)
        (nontable, table) = self._makemove(alllists, 50)
        query = """select catalogentry.code as 'entry_code', catalog.code as 'catalog_code' from centraxx_catalogentry catalogentry
join centraxx_catalog catalog on catalogentry.catalog = catalog.oid"""
        (wherestr, whereargs) = self._where(nontable, table) 
        if wherestr and wherestr.strip() != "()":
            query += f"\nwhere {wherestr}"
        res = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])
        catnames = self.name(table="catalog")
        entrynames = self.name(table="catalogentry")
        out = {}
        for row in res:
            entrycode = dig(row, "entry_code")
            catcode = dig(row, "catalog_code")
            # create the catalog
            if catcode not in out:
                out[catcode] = {}
                out[catcode]["code"] = catcode
                out[catcode]["name_de"] = dig(catnames, catcode + "/de")
                out[catcode]["name_en"] = dig(catnames, catcode + "/en")
                out[catcode]["entries"] = {}
            # add the entry
            entry = {}
            entry["code"] = entrycode
            entry["name_de"] = dig(entrynames, entrycode + "/de")
            entry["name_en"] = dig(entrynames, entrycode + "/en")        
            out[catcode]["entries"][entrycode] = entry
        return out
    def usageentry(self, labvals:list=None, files:dict=None):
        """
         usageentry gives the usageentries.
        """
        lists = {
           labval: labvals
        }
        alllists = self._makealllists(lists, {}, files)
        (nontable, table) = self._makemove(alllists, 50)
        selectstr = self._selectstr([], ["usageentry.code"], nontable, table, verbose=[])
        joins = {
                labval: self.jd["usageentry_to_labval"]
        }
        joinstr = self._joinstr(joins, nontable, table, [])
        (wherestr, whereargs) = self._where(nontable, table, like=[])
        query = f"select {selectstr} from centraxx_usageentry usageentry \n{joinstr}"
        if wherestr.strip() != "":
            query += f"\nwhere {wherestr}"
        #if print_query:
        #    print(query)
        #    print(whereargs)
        res = self.db.qfad(query, whereargs)
        self._cleartt(table["nonidc"])
        self._cleartt(table["idc"])
        names = self.name(table="usageentry")
        out = {}
        for row in res:
            code = row["code"]
            out[code] = {}
            out[code]["name_de"] = dig(names, code + "/de")
            out[code]["name_en"] = dig(names, code + "/en")
            out[code]["code"] = code
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
         ml_table (cxx3): if the name of the table connecting to multilingualentry is not simlpy the queried table name followed by "_ml_name", give the connecting table's name here. eg: name('laborvaluegroup', ..., ml_name='labval_grp_ml_name')
        """
        if self.cxx() == "3":
            return self._name_cxx3(table, code, lang, ml_table)
        elif self.cxx() == "4":
            return self._name_cxx4(table, code, lang)
    def _name_cxx3(self, table:str, code:str=None, lang:str=None, ml_table:str=None):
        """
         _name_cxx3 gives display names for cxx 3.
        """
        if not isidentifier(table) or (ml_table is not None and not isidentifier(ml_table)):
            raise Exception(f"names {table} and {ml_table} need to be valid sql identifiers.")
        query = "select [" + table + "].code, multilingual.value as name, multilingual.lang as lang"
        query += " from [centraxx_" + table + "] as [" + table + "]"
        ml_name = ""
        if ml_table is not None: # the name is different
            ml_name = "centraxx_" + ml_table
        else: # the name is the same
            ml_name = "centraxx_" + table + "_ml_name"
        query += " inner join [" + ml_name + "] mlname on mlname.related_oid = [" + table + "].oid"
        query += " inner join centraxx_multilingualentry multilingual on mlname.oid = multilingual.oid"
        wherestrings = []
        args = []
        if code is not None:
            wherestrings.append(self._whereparam("[" + table + "].code"))
            args.append(code)
        if lang is not None:
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
            if code not in out:
               out[code] = {}
            out[code][lang] = line["name"]
        return out
    def _name_cxx4(self, table:str, code:str=None, lang:str=None):
        """
         _name_cxx4 gives display names for cxx 4.
        """
        if not isidentifier(table):
            raise Exception(f"name {table} needs to be a valid sql identifier.")
        fieldname = table
        if table == "organisationunit":
            fieldname = "organizationunit"
        query = f"select lang, ml_name as name, {table}.code from centraxx_multilingual multilingual join centraxx_{table} {table} on {table}.oid = multilingual.{table} where multilingual.{fieldname} is not null"
        wherestrings = []
        args = []
        if code is not None:
            wherestrings.append(self._whereparam("[" + table + "].code"))
            args.append(code)
        if lang is not None:
            wherestrings.append(self._whereparam("multilingual.lang"))
            args.append(lang)
        if len(wherestrings) > 0:
            query += " where "
            # join where clauses by and
            query += " and ".join(wherestrings)
        res = self.db.qfad(query, *args)
        out = {}
        for line in res:
            code = line["code"]
            lang = line["lang"]
            if code not in out:
               out[code] = {}
            out[code][lang] = line["name"]
        return out

    # query
    def _selectstr(self, selects, selecta, nontable, table, verbose, pidc:str=None):
        """
         _selectstr gives the selects for idc keys and verbose array. unlike
         _joinstr, keys in lists and tmptables aren't included automatically,
         cause they may be needed in where but are not necessarily interesting
         for the output (is that true?). selecta is for fields that should be
         selected regardless if they're in the verbose array or not.
         
         the idc argument assumes that the sample table is joined it. // todo is this still true?
        """
        (vnonidc, vidc) = self._splitidc(verbose, pidc=pidc)
        nonidc = self._collkeys(nontable["nonidc"], table["nonidc"], vnonidc)
        idc = self._collkeys(nontable["idc"], table["idc"], vidc)
        for key in nonidc:
            if key not in selects:
                continue
            for s in selects[key]:
                selecta.append(s)
        selecta = self._select_idc(selecta, idc)
        selectstr = ", \n".join(selecta)
        return selectstr
    def _select_idc(self, selecta, idca:list):
        """
         _select_idc adds the sql select statements for a list of idc keys.
        """
        for item in idca:
          selectstr = f"idc_{item}.psn as '{item}'"
          if selectstr not in selecta:
            selecta.append(selectstr)
        return selecta
    def _joinstr(self, joins, nontable, table, verbose, pidc:str|None=None):
        """
         _joinstr puts together the joins needed for the lists and temporary
         tables of non-idc and idc keys, and verbose. it returns the sql join
         string.
        """
        (vnonidc, vidc) = self._splitidc(verbose, pidc=pidc)
        nonidc = self._collkeys(nontable["nonidc"], table["nonidc"], vnonidc)
        idc = self._collkeys(nontable["idc"], table["idc"], vidc)
        joina = []
        joina = self._join_idc(joina, idc, joins)
        for key in nonidc: 
            if key not in joins:
                continue
            for s in joins[key]:
                if s not in joina:
                    joina.append(s)
        joinstr = " \n".join(joina)
        return joinstr
    def _join_idc(self, joina, idca:list, joins):
        """
         _join_idc adds the sql join statements for the idc keys of the query.
        """
        for item in idca:
          if item in joins:
            for s in joins[item]:
              if s not in joina:
                joina.append(s)
          if self._idckind[item] == "SAMPLE":
            joinstr = f"left join centraxx_sampleidcontainer as idc_{item} on idc_{item}.sample = sample.oid and idc_{item}.idcontainertype = {self._idcoid[item]}"
    
            if joinstr not in joina:
              joina.append(joinstr)
          elif self._idckind[item] == "PATIENT":
            joinstr = f"left join centraxx_idcontainer as idc_{item} on idc_{item}.patientcontainer = patientcontainer.oid and idc_{item}.idcontainertype = {self._idcoid[item]}"
            if joinstr not in joina: # neccessary?
              joina.append(joinstr)
          else:
            print(f"error: idcontainer kind {self._idckind[item]} not supported.")
        return joina
    def _where(self, nontable:dict, table:dict, like:list=None): # -> (str, list)
        """
         _where returns the wherestring and args array for the provided
         lists and temporary tables.
         
         the user needs to make sure that whatever is used here is joined
         into the query before.
         
         the keys in nontable["nonidc"] and table["nonidc"] are assumed to be
         the tr constants, e.g. tr.locationpath, the keys in nontable["idc"]
         and table["idc"] are assumed to be idcontainers.
         
         like holds tr constants and idcontainers for which to check likeness
         instead of equality.
        """
        if like is None:
            like = []
        wheredict = { 
          trial: { "field": "flexistudy.code" },
          locationpath: { "field": "samplelocation.locationpath" },
          locationname: { "field": "samplelocation.locationid" },          
          method: { "field": "labormethod.code" },
          kitid: { "field": "samplekit.kitid" },
          cxxkitid: { "field": "samplekit.cxxkitid" },
          catalog: { "field": "catalog.code" },
          category: { "field": "sample.dtype" },
          type: { "field": "sampletype.code" },          
          orga: { "field": "organisationunit.code" },
          parentid: { "field": "parentidc.psn" },
          parentoid: { "field": "sample.parent" },
          sampleoid: { "field": "sample.oid" },          
          samplingdate: { "field": "sample.samplingdate", "type": "date" },
          receiptdate: { "field": "sample.receiptdate", "type": "date" },
          derivaldate: { "field": "sample.derivaldate", "type": "date" },
          first_repositiondate: { "field": "sample.first_repositiondate", "type": "date" },
          repositiondate: { "field": "sample.repositiondate", "type": "date" },
          stockprocessingdate: { "field": "sample.stockprocessingdate", "type": "date" },
          secondprocessingdate: { "field": "sample.secondprocessingdate", "type": "date" },
          username: { "field": "participant.username" },
          address: { "field": "address.email" },
          login: { "field": "credential.last_login_on", "type": "date" },
          labval: { "field": "labval.code" }
        }
        wherestrs = []
        whereargs = []
        for key in _uniq(list(nontable["nonidc"].keys()) + list(table["nonidc"].keys())):
           if dig(nontable["nonidc"], key) is not None and dig(wheredict, key + "/type") == "date":
               (wstr, wargs) = self._wheredate(dig(nontable["nonidc"], key), wheredict[key]["field"])
           else:
               (wstr, wargs) = self._whereexact(dig(nontable["nonidc"], key), dig(table["nonidc"], key), wheredict[key]["field"])
           if wstr != "()":
               wherestrs.append(wstr)
               whereargs.extend(wargs)
        for key in _uniq(list(nontable["idc"].keys()) + list(table["idc"].keys())):
            (wstr, wargs) = self._whereexact(dig(nontable["idc"], key), dig(table["idc"], key), f"idc_{key}.psn")
            if wstr != "()":
                wherestrs.append(wstr)
                whereargs.extend(wargs)
        wherestr = " and ".join(wherestrs)
        return (wherestr, whereargs)
    def _whereexact(self, lst, tmptable, dbfield:str): # -> (str, list)
        """
         _whereexact returns a where clause and argument list for exact
         matching of items in list and temporary table. NULL string is list is
         treated as sql NULL value.
        """
        wherearg = []
        wherestr = "("
        needsor = False
        if lst is not None and 'NULL' in lst:
            lst.remove("NULL")
            wherestr += dbfield + " is NULL"
            needsor = True
        if lst is not None and len(lst) > 0:
            if needsor:
                wherestr += " or "
            placeholder = traction._sqlinplaceholder(len(lst)) # todo put in package? tr._sqlinplaceholder
            wherestr += dbfield + " in " + placeholder # e.g. samplelocation.locationpath in (?, ?, ?)
            wherearg.extend(lst)
            # if something comes next, chain it with or
            needsor = True
        if tmptable is not None:
            if needsor:
                wherestr += " or "
            wherestr += dbfield + " in "
            wherestr += f"(select stdin from tempdb..{tmptable})"
        wherestr += ")"
        return (wherestr, wherearg)
    def _wheredate(self, tpl, dbfield): # -> (str, list)
        """
         _wheredate makes a date check. for now only check that it's between
         the two values of the array passed as date parameter.
        """
        wstr = ""
        wargs = []
        if tpl == 'NULL':
            wstr = "(" + dbfield + " is NULL)"
        else:
            s = "(CAST(" + dbfield + " as date) between ISNULL(?, " + dbfield + ") and ISNULL(?, " + dbfield + "))"
            wstr = s
            wargs.extend(tpl)
        return (wstr, wargs)
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
        if like is None or not like:
            return name + " = ?"
        else:
            return name + " like '%' + ? + '%'"
    def _wherelike(self, name):
        """
         _wherelike gives a ?-parameterized sql where like expression.
        """
        return name + " like '%' + ? + '%'"

    def _wherelikes(self, field, n):
        """
         _wherelikes gives a ?-parameterized sql of or-joined where-like
         expressions, as many as given n.
        """
        a = []
        for i in range(n):
            a.append(field + " like '%' + ? + '%'") # the sql takes literal plusses like here
        return " or ".join(a)
    def _top(self, top):
        """
         _top returns an injection-safe top string, for, e.g. `select top 100 * from table`, if
         top is None return an empty string.
        """
        if top is not None:
           if not isnumber(top):
               raise Exception(f"top param {top} needs to be a number")
           return f"top {top}"
        return ""
    def _order_by(self, order_by):
        """
         _order_by returns an injection safe order by string.
        """
        if not isidentifier(order_by):
            raise Exception(f"order_by param {order_by} needs to be an sql identifier.")
        return f"order by {order_by}"
    def _idcinit(self):
        """
         _idcinit makes a mapping of idcontainers from their code (lower-case)
         to respective oid and kind, and makes a list containing all idcs
         including sidc and pidc.
        """
        query = "select code, oid, kind from centraxx_idcontainertype"
        res = self.db.qfad(query)
        self._idcoid = {}
        self._idckind = {}
        for row in res:
          self._idcoid[row["code"]] = row["oid"]
          self._idckind[row["code"]] = row["kind"]
        self._idcs = []
        for id in self.settings['idc'] + [self.sidc(), self.pidc()]:
            if id not in self._idcs:
                self._idcs.append(id)
    def _make_rec(self, recval, finding, names:bool=False) -> Rec:
        """
         _make_rec makes a recorded value instance for finding from db results with display names if wished.
        """
        out:Rec = None
        if recval["laborvalue_type"] == "BOOLEAN":
            val = True if recval["boolvalue"] == 1 else False
            out = BooleanRec(method=finding["method"], labval=recval["laborvalue_code"], rec=val)
        elif recval["laborvalue_type"] == "DECIMAL":
            #print(recval["laborvalue_code"])
            #print(recval)
            value = float(recval["numericvalue"]) if recval["numericvalue"] is not None else None
            out = NumberRec(method=finding["method"], labval=recval["laborvalue_code"], rec=value, unit=recval["laborvalue_unit"])
        elif recval["laborvalue_type"] == "STRING" or recval["laborvalue_type"] == "LONGSTRING":
            out = StringRec(method=finding["method"], labval=recval["laborvalue_code"], rec=recval["stringvalue"])
        elif recval["laborvalue_type"] == "DATE":
            out = DateRec(method=finding["method"], labval=recval["laborvalue_code"], rec=recval["datevalue"])
        elif recval["laborvalue_type"] == "LONGDATE":
            out = DateRec(method=finding["method"], labval=recval["laborvalue_code"], rec=recval["datevalueprecision"])
        elif recval["laborvalue_type"] == "CATALOG":
            # get the catalog code
            query = """select catalog.code as 'catalog_code' from centraxx_catalog as catalog
            where catalog.oid = ?""" # do this once for all catalogs on startup or finding() call?
            res = self.db.qfad(query, recval['laborvalue_catalog_oid'])
            catalog_code = res[0]["catalog_code"]
            # get the catalog entries
            query = """select catalogentry.code as 'catalogentry_code' from centraxx_recordedvalue as recordedvalue
            join centraxx_recordedval_catentry as recordedval_catentry on recordedval_catentry.recordedvalue_oid = recordedvalue.oid
            join centraxx_catalogentry as catalogentry on catalogentry.oid = recordedval_catentry.catalogentry_oid
            where recordedvalue.oid = ?"""
            res = self.db.qfad(query, recval['oid'])
            # get the catalogentry names if they are not already loaded, and cache them. maybe it's faster to load the whole names map once instead of joining them in each time?
            if names is True and self.names_catalogentry is None:
                self.names_catalogentry = self.name(table="catalogentry")
            entries = []
            value_name = {}
            for r in res:
                code = r["catalogentry_code"]
                entries.append(code)
                if names is True:
                    value_name[code] = self.names_catalogentry[code]
            
            out = CatalogRec(method=finding["method"], labval=recval["laborvalue_code"], catalog=catalog_code, rec=entries, rec_name=value_name)
        elif recval["laborvalue_type"] == "ENUMERATION" or recval["laborvalue_type"] == "OPTIONGROUP":
            query = """select usageentry.code as 'usageentry_code' from centraxx_recordedvalue as recordedvalue
            join centraxx_recordedval_usagentry as recordedval_usagentry on recordedval_usagentry.recordedvalue_oid = recordedvalue.oid
            join centraxx_usageentry as usageentry on usageentry.oid = recordedval_usagentry.usageentry_oid
            where recordedvalue.oid = ?"""
            res = self.db.qfad(query, recval['oid'])

            # get the usageentry names if they are not already loaded, and cache them. maybe it's faster to load the whole names map once instead of joining them in each time?
            if names is True and self.names_usageentry is None:
                self.names_usageentry = self.name(table="usageentry")

            entries = []
            value_name = {}
            for r in res:
                code = r["usageentry_code"]
                entries.append(code)
                if names is True:
                    value_name[code] = self.names_usageentry[code]
            
            out = MultiRec(method=finding["method"], labval=recval["laborvalue_code"], rec=entries, rec_name=value_name)
        else:
            raise Exception(f"no record class for laborvalue of type {recval['laborvalue_type']}")
        return out
    
    def _fill_in_primary(self, sample:Sample):
        """
         _fill_in_primary adds a reference to the given sample's primary sample,
         if there is one.
        """
        poids = []
        self._get_parents(sample.id("oid"), poids)
        if len(poids) > 0:
            primary_oid = poids[0]
            primary = self.sample(oids=[primary_oid])[0]
            sample.primary = Idable(ids=primary.ids, mainidc=primary.mainidc)

    # lists and tmp tables
    def _makemove(self, alllists:dict, cutoff:int): # -> (dict, dict)#bm
        """
         _makemove makes temporary tables from the given lists that are longer
         than cutoff. it returns one dict holding the remaining, non-table
         lists and one dict holding the table names of the created temporary
         tables, both return dicts distinguishing between nonidc and idc.
        """
        nontables = {}
        (nontables["nonidc"], ttlists) = _tablelists(alllists["nonidc"], cutoff)
        (nontables["idc"], ttidclists) = _tablelists(alllists["idc"], cutoff)        
        tables = {}
        tables["nonidc"] = self._maketables(ttlists, "tmp_")
        tables["idc"] = self._maketables(ttidclists, "tmp_idc_")
        return (nontables, tables) 
    def _makealllists(self, lists, idc, files):
        """
         _makealllists reads the lists from files, puts them together with the
         lists passed as lists, and returns them all in one dict,
         keeping nonidc and idc seperate.
        """
        alllists = {}
        alllists["nonidc"] = {}
        alllists["idc"] = {}
        for key, lst in lists.items():
            if lst is not None:
                alllists["nonidc"][key] = lst
        for key, lst in idc.items():
            alllists["idc"][key] = lst
        (ff, ffidc) = self._readfiles(files)
        for key, lst in ff.items():
            if key not in alllists["nonidc"]:
                alllists["nonidc"][key] = []
            alllists["nonidc"][key].extend(lst)
        for key, lst in ffidc.items():
            if key not in alllists["idc"]:
                alllists["idc"][key] = []
            alllists["idc"][key].extend(lst)
        return alllists
    def _readfiles(self, files, sidc:str=None, pidc:str=None):
        """
         _readfiles reads the files from which tmp tables should be build into
         lists.  it returns a tuple of one dict holding the non-idc lists and
         one dict holding the idc lists.
        """
        if files is None:
            return ({}, {})
        both = {}
        for key, filepath in files.items():
            lst = []
            with open(filepath, "r") as f:
                for line in f:
                    lst.append(line.rstrip())
            both[key] = lst
        nonidc = {}
        idc = {}
        for key, _ in both.items():
            if key == sampleid:
                idc[self.sidc()] = both[key]
            elif key == patientid:
                idc[self.pidc(pidc)] = both[key]
            elif self._is_idc(key, sidc=sidc, pidc=pidc):
                idc[key] = both[key]
            else:
                nonidc[key] = both[key]
        return (nonidc, idc)
    def _maketables(self, d:dict, prefix:str=""): #-> dict
        """
         _maketables makes temporary tables for each key in the given dict,
         inserts the list of values belonging to that key, and returns a dict
         the table names by key.
        """
        out = {}
        for key, lst in d.items():
            #name = "tempdb..#" + prefix + key
            name = "#" + prefix + key
            if not isidentifier(name):
                raise Exception(f"name {name} needs to be a valid sql identifier.")
            self.db.query(f"create table {name} (stdin varchar (255) )")
            for e in lst:
                self.db.query(f"insert into {name} values (?)", e)
            out[key] = name
        return out
    def _cleartt(self, tmptables:dict):
        """
         _cleartt drops the temporary tables tables that were created with
         _maketables after the query using their data was run. it takes the
         dict of filetables that was returned by _maketables.
         
         they would be dropped automatically after the session, but in case
         several queries are sent in one session, maybe it's better to drop
         them after each query.
        """
        for key, tablename in tmptables.items():
            if not isidentifier(tablename):
                raise Exception("table name {tablename} needs to be a valid sql identifier.")
            q = f"drop table tempdb..{tablename}"
            #print(q)
            self.db.query(q)  # todo is kairos_spring used again after this?

    # settings / idc related
    def sidc(self) -> str:
        """
         sidc returns the main idc code by which samples are referenced as
         specified in the settings. 
        """
        if self.db.target not in self.settings['sampleid']:
            raise Exception(f"please specify the main sample idcontainer for {self.db.target} in settings.yaml")
        return self.settings['sampleid'][self.db.target]
    def pidc(self, pidc:str|None=None) -> str:
        """
        """
        if pidc is not None:
            return pidc
        if self.db.target not in self.settings['patientid']:
            raise Exception(f"please specify the main patient idcontainer for {self.db.target} in settings.yaml")
        return self.settings['patientid'][self.db.target]
    def _sidcs(self) -> list:
        """
         _sidcs returns the idcs from settings that are specific for sample.
         
         rather make this a section in conf? but maybe not, keep the conf simple and let the program sort out pidc and sidc.
         
         # idc holds idcontainer codes that should be queryable as command line flags 
         idc:
           sample:
             - extsampleid
             - modul
             - tier
           patient:
             - mpi
        """
        out = []
        for idc in self.settings["idc"]:
            if idc in self._idckind and self._idckind[idc] == "SAMPLE" and not idc in out:
                out.append(idc)
        sidc = self.sidc()
        if sidc not in out:
            out.append(self.sidc())
        return out
    def _pidcs(self, pidc:str=None) -> list:
        """
         _pidcs returns the idcs from settings that are specific for
         sample.
        """
        out = []
        for idc in self.settings["idc"]:
            if idc in self._idckind and self._idckind[idc] == "PATIENT" and idc not in out:
                out.append(idc)
        pidc = self.pidc(pidc)
        if pidc not in out:
            out.append(pidc)
        return out
    def _concrete_idcs(self, verbose, pidc=None):
        """
         _concrete_idcs replaces traction constants patientid and sampleid with their
         respective idc for array.
        """
        out = []
        for verb in verbose:
            if verb == patientid:
                out.append(self.pidc(pidc))
            elif verb == sampleid:
                out.append(self.sidc())
            else:
                out.append(verb)
        return out
    def _concrete_idcs_dict(self, d, pidc=None):
        """
         _concrete_idcs_dict replaces traction constants patientid and sampleid with their
         respective idc for dict.
        """
        out = {}
        for key, val in d.items():
            #print("key: " + key)
            if key == patientid:
                out[self.pidc(pidc)] = val
            elif key == sampleid:
                #print("here: " + self.sidc())
                out[self.sidc()] = val
            else:
                out[key] = val
        return out
    def cxx(self) -> str:
        """
         cxx gives the centraxx version for db target from settings.
        """
        v = dig(self.settings, f"cxx/{self.db.target}")
        if v is None:
            return None
        return str(v)

    def _is_idc(self, key:str, sidc:str=None, pidc:str=None): # -> bool
        """
         _is_idc says whether a string is an idcontainer mentioned in
         settings.yaml or passed as sidc or pidc argument.
        """
        return key in self.settings["idc"] or key == self.sidc() or key == self.pidc(pidc)
    def _splitidc(self, arr:list, pidc:str=None): # -> (list, list)
        """
         _splitidc splits an array of tr constants and idc keys into non-idc
         (tr constants) and idc keys.
        """
        nonidc = []
        idc = []
        for k in arr:
            if self._is_idc(k, pidc=pidc):
                idc.append(k)
            else:
                nonidc.append(k)
        return (nonidc, idc)
    def _collkeys(self, lists:dict=None, tmptables:dict=None, verbose:list=None):
        """
         _collkeys collects the keys join needs from lists, temporary tables
         and verbose. preserves order and ensures uniqueness.
        """
        if lists is None:
            lists = {}
        if tmptables is None:
            tmptables = {}
        if verbose is None:
            verbose = []
        out = []
        for k in lists.keys():
            if lists[k] is not None and k not in out:
                out.append(k)
        for k in tmptables.keys():
            if tmptables[k] is not None and k not in out:
                out.append(k)
        for k in verbose:
            if k not in out:
                out.append(k)
        return out
    
