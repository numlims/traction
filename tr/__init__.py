# automatically generated, DON'T EDIT. please edit init.ct from where this file stems.
from dbcq import *
import cnf
from datetime import datetime
from dip import dig, dis
from tram import Sample, Idable, Amount, Identifier
from tram import Patient
from tram import Finding
from tram import Rec, BooleanRec, NumberRec, StringRec, DateRec, MultiRec, CatalogRec
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
def floatornull(x):
    """
     floatornull casts to float or returns None. somehow the values passed
     to Amount need float casts, and float casts don't accept None.
    """
    if x is None:
        return None
    return float(x)
def get_ids(idables:list, code:str=None) -> list:
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
    return re.match(r"^[0-9](.[0-9]*)?$", a)
def isidentifier(a) -> bool:
    """
     isidentifier returns whether a string is a sql identifier to prevent
     sql injection.  like isnumber, could this be handled better by a library?
    """
    return re.match(r"^[A-Za-z_0-9\.#]+$", a)
def _dextend(d:dict, key, l:list):
    """
     _dextends extends an array in a dictionary at the given key with the
     values in the passed list.
    """
    if l is not None:
        if not key in d:
            d[key] = []
        d[key].extend(l)
def _mvlists(dicta:dict, dictb:dict, cutoff:int):
    """
     _mvlists moves the lists that are longer than cutoff from dicta to
     dictb, deleting them in dicta. if there is already a list in dictb
     under that key, extend.
    """
    for key, lst in dicta.items():
        if lst is not None and len(lst) > cutoff:
            if key in dictb:
                dictb[key].extend(lst)
            else:
                dictb[key] = lst
            del dicta[key]
def _uniq(lst): # -> list
    """
     _uniq returns a new list containing the unique items of the list passed, preserving order.
    """
    out = []
    for e in lst:
        if e not in out:
            out.append(e)
    return out

def idable_csv(idables:list, outfile=None, delim:str=",", *idcs) -> str:
    """
     idable_csv writes a list of Idables to the given csv file. the given
     idcontainers are included as columns. if no idcontainers are given,
     all are included. if True is passed as file, the output is
     printed. (todo pass sys.stdout instead?)
    """
    if delim is None:
        delim = ","
    if idables is None or len(idables) == 0: # todo throw error?
        #print("no idables")
        return None
    with open(outfile, "w") as f:
        colnames = []
        for idable in idables:
            for col in list(idable.iddict(*idcs).keys()):
                if not col in colnames:
                    colnames.append(col)
        #print("colnames:")
        #print(colnames)
        writer = csv.DictWriter(f, fieldnames=colnames, delimiter=delim)        #bm
        writer.writeheader()
        for idable in idables:
            d = idable.iddict(*idcs)
            writer.writerow(d)
    return outfile
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
    with open(outfile, "w") as f:
        writer = csv.DictWriter(f, fieldnames=colnames, delimiter=delim)
        writer.writeheader()
        for fdict in fdicts:
            writer.writerow(fdict)
    return outfile

class traction:
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
        }
        self.names_labval = None
        self.names_catalogentry = None
        self.names_usageentry = None

    def sample(self, sampleids:list=None, oids:list=None, idc=None, patientids:list=None, pidc:str=None, parentids:list=None, parentoids:list=None, locationpaths:list=None, trials:list=None, kitids:list=None, cxxkitids:list=None, categories:list=None, types:list=None, orgas:list=None, samplingdates=None, receiptdates=None, derivaldates=None, first_repositiondates=None, repositiondates=None, stockprocessingdates=None, secondprocessingdates=None, files:dict=None, verbose:list=None, verbose_all=False, primaryref:bool=False, incl_parents:bool=False, incl_childs:bool=False, incl_tree:bool=False, like:list=None, missing=False, order_by=None, top=None, print_query:bool=False, raw:bool=False):
        """
         sample gets sample(s) and returns them as a list of Sample instances.
         
         pass sampleids and other values to filter for as lists of strings,
         e.g. `sampleids=["a", "b", "c"]`.
         
         use the idc param to filter for idcontainer lists by passing a dict of
         lists keyed by idcontainer code, e.g. `idc={"extsampleid": ["a", "b", "c"]}`.
         
         put info that should be joined into the result into the verbose array,
         e.g.  `verbose=[tr.locationpath]`. to join in everything, say
         `verbose_all=True`. this is slower than non-verbose.
         
         pass dates as a tuple of from and to datetime, e.g. `samplingdates=(datefrom, None)`.
         
         to check via like as opposed to exact, put the respective fields into
         the like array, e.g. `like=[tr.locationpath]`.
        """
        if verbose is None:
            verbose = []
        if like is None:
            like = []
        if files is None:
            files = {}
        if idc is None:
            idc = {}
        # print("try:" + tr.sampleid)
        vaa = [cxxkitid, kitid, locationname, locationpath, orga, parentid, 
               project, receptacle, type,
               secondprocessing, stockprocessing, trial]
        vaa.extend(self._patientidcs(pidc))
        vaa.extend(self._sampleidcs())                
        if not self.sidc() in verbose:
            verbose.insert(0, self.sidc())
        verbose = self._concrete_idcs(verbose, pidc=pidc)
        #files = self._concrete_idcs_dict(files, pidc=pidc)
        #print("files:")
        #print(files)

        if trials:
            verbose.append(trial)
        if locationpaths:
            verbose.append(locationpath)
        if kitids:
            verbose.append(kitid)
        if cxxkitid:
            verbose.append(cxxkitid)
        if parentids:
            verbose.append(parentid)
        if orgas:
            verbose.append(orga)
        if verbose_all == True:
            verbose = vaa
        #print("verbose:")
        #print(verbose)
        if not _checkverbose(verbose, vaa): 
            return None # throw error?
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
          secondprocessingdate: secondprocessingdates
        }
        _dextend(idc, self.sidc(), sampleids)
        _dextend(idc, self.pidc(pidc), patientids)
        (tmptables, idctmptables) = self._makemove(files, lists, idc, 100, pidc=pidc)
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
        for pidc in self._patientidcs(pidc):
            joins[pidc] = self.jd["sample_to_patient"]
        selectstr = self._selectstr(jselects, verbose, lselects, idc)  
        joinstr = self._joinstr(joins, verbose, idc, pidc=pidc)  
        (wherestr, whereargs) = self._where(lists, tmptables, idc, idctmptables, like=like)
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
        self._cleartt(tmptables)
        self._cleartt(idctmptables)
        if raw:
            return res
        sarr = []
        for r in res:
            ids = []
            #if dig(r, sampleid) is not None:
            #    ids.append(Identifier(id=dig(r, sampleid), code=self.sidc()))
            for idc in self._sampleidcs():
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
            if dig(r, patientid) is not None:   # todo include patient oid?
                patids.append(Identifier(id=dig(r, patientid), code=self.pidc(pidc)))
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
            sarr.append(s)
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
    def patient(self, patientids=None, pidc=None, sampleids=None, idc=None, trials=None, orgas:list=None, files:dict=None, verbose:list=None, verbose_all=False, like:list=None, order_by=None, top=None, print_query:bool=False, raw:bool=False):
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
        vaa.extend(self._patientidcs(pidc))        
        if not self.pidc(pidc) in verbose:
            verbose.insert(0, self.pidc(pidc))
        verbose = self._concrete_idcs(verbose, pidc=pidc)
        files = self._concrete_idcs_dict(files, pidc=pidc)
        lists = {
          trial: trials,
          orga: orgas
        }
        _dextend(idc, self.sidc(), sampleids)
        _dextend(idc, self.pidc(pidc), patientids)
        (tmptables, idctmptables) = self._makemove(files, lists, idc, 100, pidc=pidc)
        if verbose_all == True:
            verbose = vaa
        if orgas is not None:
            verbose.append(orga)
        silent = []
        if trials:
            silent.append(trial)
        if orgas:
            silent.append(orga)
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
        for sidc in self._sampleidcs():
            joins[sidc] = self.jd["patient_to_sample"]
        selectstr = self._selectstr(selects, verbose, ["patientcontainer.*"], idc)  
        joinstr = self._joinstr(joins, verbose + silent, idc, pidc=pidc)  
        (wherestr, whereargs) = self._where(lists, tmptables, idc, idctmptables, like=like)
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
        self._cleartt(tmptables)
        self._cleartt(idctmptables)        
        if raw:
            return res
        pats = []
        for r in res:
            ids = [ Identifier(id=dig(r, patientid), code=self.pidc(pidc)) ]
            for idc in self._patientidcs(pidc):
                if idc in r and r[idc] is not None:
                    ids.append( Identifier(id=dig(r, idc), code=idc.upper()) )
            pat = Patient(
              ids=Idable(ids=ids, mainidc=self.pidc(pidc)),
              orga=dig(r, orga)
            )
            pats.append(pat)
            #print("pat: " + str(pat))
        return pats
    def trial(self):
        """
         trial gives trials.
        """
        query = "select code from centraxx_flexistudy"
        res = self.db.qfad(query)
        return res
    def finding(self, sampleids=None, patientids=None, pidc:str=None, idc=None, methods=None, trials=None, values:bool=True, verbose:list=None, files:dict=None, verbose_all:bool=False, names:bool=False, top:int=None, print_query:bool=False, raw:bool=False):
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
        if verbose_all == True:
            verbose = vaa
        if trials is not None:
            verbose.append(trial)
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
        (tmptables, idctmptables) = self._makemove(files, lists, idc, 100, pidc=pidc)
        selects = {
            self.sidc(): [f"idc_{self.sidc()}.psn as '{sampleid}'"],
            self.pidc(pidc): [f"idc_{self.pidc(pidc)}.psn as '{patientid}'"],                   
        }
        idcselectstr = self._selectstr(selects, verbose, [], idc)  
        joins = {
            trial: self.jd["sample_to_trial"]
        }
        for pidc in self._patientidcs(pidc):
            joins[pidc] = self.jd["sample_to_patient"]
        idcjoinstr = self._joinstr(joins, verbose, idc, pidc=pidc)
        topstr = self._top(top)
        query = f"""select {topstr} laborfinding.oid as "laborfinding_oid", laborfinding.*, labormethod.code as {method}, {idcselectstr}
        from centraxx_laborfinding as laborfinding

        -- go from laborfinding to sample
        left join centraxx_labormethod as labormethod on laborfinding.labormethod = labormethod.oid
        left join centraxx_labormapping as labormapping on labormapping.laborfinding = laborfinding.oid
        left join centraxx_sample sample on labormapping.relatedoid = sample.oid
        {idcjoinstr}"""
        (wherestr, whereargs) = self._where(lists, tmptables, idc, idctmptables)        
        if wherestr.strip() != "":
            query += f"\nwhere {wherestr}"
            
        if print_query:
            print(query)
            print(whereargs)
        results = self.db.qfad(query, whereargs)
        self._cleartt(tmptables)
        self._cleartt(idctmptables)        
        if names is True:
            self.names_laborvalue = self.name(table="laborvalue")
        for i, finding in enumerate(results):
            if values != True: # todo put this outside of the loop?
                continue
            query = f"""select recordedvalue.*, laborvalue.code as laborvalue_code, laborvalue.dtype as laborvalue_type, laborvalue.custom_catalog as laborvalue_catalog_oid, unit.code as laborvalue_unit
                from centraxx_laborfinding as laborfinding

                -- go from laborfinding to recorded value
                join centraxx_labfindinglabval as labfindinglabval on labfindinglabval.laborfinding = laborfinding.oid
                join centraxx_recordedvalue as recordedvalue on labfindinglabval.oid = recordedvalue.oid

                --go from labfindinglabval to the laborvalue for the messparam
                join centraxx_laborvalue laborvalue on labfindinglabval.laborvalue = laborvalue.oid

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
            finding = Finding(
                findingdate=dig(res, "findingdate"),
                method=res["method"],
                methodname=res["shortname"],
                patient=Idable(id=dig(res, patientid), code=self.pidc(pidc), mainidc=self.pidc(pidc)) if dig(res, patientid) is not None else None, 
                recs=res["values"] if "values" in res else None, # todo None ok?
                sample=Idable(id=res[sampleid], code=self.sidc(), mainidc=self.sidc()),
                sender=None
            )
            findings.append(finding)
        return findings
    def method(self, methods=None, files:dict=None):
        """
         method (messprofil) gets method(s) and their labvals (messparameter).
        """
        if files is None:
            files = {}
        lists = {
          method: methods
        }
        (tmptables, idctmptables) = self._makemove(files, lists, {}, 100)
        query = f"""select laborvalue.code as labval, labormethod.code as "method", laborvalue.dtype as labval_type, catalog.code as catalog
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
        (wherestr, whereargs) = self._where(lists, tmptables, {}, idctmptables)

        if wherestr and wherestr.strip != "()":
          query += " where " + wherestr
        # print(query)
        res = self.db.qfad(query, whereargs)
        self._cleartt(tmptables)
        self._cleartt(idctmptables)        
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
            out[methodcode]["labvals"][labvalcode] = labval
        return out
    def user(self, usernames:list=None, emails:list=None, lastlogin=None, files:dict=None, verbose:list=None):
        """
        """
        if verbose is None:
            verbose = []
        if files is None:
            files = {}
        vaa = [tr.address, tr.login]
        if usernames:
            verbose.append(tr.username)
        if emails:
            verbose.append(tr.address)
        if lastlogin:
            verbose.append(tr.login)
        lists = {
          username: usernames,
          address: emails,
          login: lastlogin
        }
        (tmptables, idctmptables) = self._makemove(files, lists, idc, 100)
        self._cleartt(tmptables)
        self._cleartt(idctmptables)        
        out = []
        for r in res:
            user = User(
                email=dig(r, tr.email),
                lastlogin=dig(r, tr.lastlogin),
                username=dig(r, tr.username),
            )
            out.append(user)
        return out
    def catalog(self, catalogs:list=None, files:dict=None):
        """
         catalogentry gives the catalogentries per catalog.
        """
        if files is None:
            files = {}
        lists = {
            catalog: catalogs
        }
        (tmptables, idctmptables) = self._makemove(files, lists, {}, 100)
        query = """select catalogentry.code as 'entry_code', catalog.code as 'catalog_code' from centraxx_catalogentry catalogentry
join centraxx_catalog catalog on catalogentry.catalog = catalog.oid"""
        (wherestr, whereargs) = self._where(lists, tmptables, {}, idctmptables) # idctmptables not actually needed at the moment
        if wherestr and wherestr.strip() != "()":
            query += f"\nwhere {wherestr}"
        res = self.db.qfad(query, whereargs)
        self._cleartt(tmptables)
        self._cleartt(idctmptables)        
        catnames = self.name(table="catalog")
        entrynames = self.name(table="catalogentry")
        out = {}
        for row in res:
            entrycode = dig(row, "entry_code")
            catcode = dig(row, "catalog_code")
            # create the catalog
            if not catcode in out:
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
    def usageentry(self):
        """
         usageentry gives the usageentries.
        """
        query = "select code from centraxx_usageentry"
        res = self.db.qfad(query)
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
    
    def sidc(self) -> str:
        """
         sidc returns the main idc code by which samples are referenced as
         specified in the settings. 
        """
        if not self.db.target in self.settings['sampleid']:
            raise Exception(f"please specify the main sample idcontainer for {self.db.target} in settings.yaml")
        return self.settings['sampleid'][self.db.target]
    def pidc(self, pidc:str=None) -> str:
        """
        """
        if pidc is not None:
            return pidc
        if not self.db.target in self.settings['patientid']:
            raise Exception(f"please specify the main patient idcontainer for {self.db.target} in settings.yaml")
        return self.settings['patientid'][self.db.target]
    
    def _selectstr(self, selects, verbose, selecta, idc):
        """
         _selectstr filters the selects by the verbose array and returns the
         sql select string. selecta is for fields that should be selected
         regardless if they're in the verbose array or not.
         
         the idc argument assumes that the sample table is joined it. // todo is this still true?
        """
        for verb in verbose:
            if not verb in selects:
                continue
            for s in selects[verb]:
                selecta.append(s)
        selecta = self._append_idc_select(selecta, idc, verbose)
        selectstr = ", \n".join(selecta)
        return selectstr
    def _joinstr(self, joins, verbose, idc, pidc=None):
        """
         _joinstr puts together the joins needed by verbose array and idc keys
         and returns the sql join string.
        """
        joina = []
        joina = self._append_idc_join(joina, idc, verbose, joins, pidc=pidc)
        for verb in verbose: 
            if not verb in joins:
                continue
            for s in joins[verb]:
                if not s in joina:
                    joina.append(s)
        joinstr = " \n".join(joina)
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
    def _append_idc_join(self, joina, idc, verbose, joins, pidc=None):
        """
         _append_idc_join adds the sql join statements for an idc dict.
        """
        idca = []
        for verb in verbose:
          if verb in self.settings["idc"] or verb == self.sidc() or verb == self.pidc(pidc):
            idca.append(verb)
        if idc is not None:
          idca.extend(idc.keys())
        for item in idca:
          if item in joins:
            for s in joins[item]:
              if s not in joina:
                joina.append(s)
          if self._idckind[item] == "SAMPLE":
            joinstr = f"left join centraxx_sampleidcontainer as idc_{item} on idc_{item}.sample = sample.oid and idc_{item}.idcontainertype = {self._idcoid[item]}"
    
            if not joinstr in joina:
              joina.append(joinstr)
          elif self._idckind[item] == "PATIENT":
            joinstr = f"left join centraxx_idcontainer as idc_{item} on idc_{item}.patientcontainer = patientcontainer.oid and idc_{item}.idcontainertype = {self._idcoid[item]}"
            if not joinstr in joina: # neccessary?
              joina.append(joinstr)
          else:
            print(f"error: idcontainer kind {self._idckind[item]} not supported.")
        return joina
    def _where(self, lists:dict, tmptables:dict, idclists:dict, idctmptables:dict, like:list=None): # -> (str, list)
        """
         _where returns the wherestring and args array for the provided
         lists and temporary tables.
         
         the user needs to make sure that whatever is used here is joined
         into the query before.
         
         the keys in lists and tmptables are assumed to be the tr constants,
         e.g. tr.locationpath, the keys in idclists and idctmptables are
         assumed to be idcontainers.
         
         like holds tr constants and idcontainers for which to check likeness
         instead of equality.
        """
        if like is None:
            like = []
        wheredict = { 
          trial: { "field": "flexistudy.code" },
          locationpath: { "field": "samplelocation.locationpath" },
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
          secondprocessingdate: { "field": "sample.secondprocessingdate", "type": "date" }
        }
        wherestrs = []
        whereargs = []
        #print("lists:")
        #print(lists)
        #print("tmptables:")
        #print(tmptables)
        for key in _uniq(list(lists.keys()) + list(tmptables.keys())):
           if dig(lists, key) is not None and dig(wheredict, key + "/type") == "date":
               (wstr, wargs) = self._wheredate(dig(lists, key), wheredict[key]["field"])
           else:
               (wstr, wargs) = self._whereexact(dig(lists, key), dig(tmptables, key), wheredict[key]["field"])
           if wstr != "()":
               wherestrs.append(wstr)
               whereargs.extend(wargs)
        for key in _uniq(list(idclists.keys()) + list(idctmptables.keys())):
            (wstr, wargs) = self._whereexact(dig(idclists, key), dig(idctmptables, key), f"idc_{key}.psn")
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
            wherestr += f"(select stdin from {tmptable})"
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
            s = f"(CAST(" + dbfield + " as date) between ISNULL(?, " + dbfield + ") and ISNULL(?, " + dbfield + "))"
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
        if like == None or like == False:
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
            query = f"""select catalog.code as 'catalog_code' from centraxx_catalog as catalog
            where catalog.oid = ?""" # do this once for all catalogs on startup or finding() call?
            res = self.db.qfad(query, recval['laborvalue_catalog_oid'])
            catalog_code = res[0]["catalog_code"]
            # get the catalog entries
            query = f"""select catalogentry.code as 'catalogentry_code' from centraxx_recordedvalue as recordedvalue
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
            query = f"""select usageentry.code as 'usageentry_code' from centraxx_recordedvalue as recordedvalue
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
    
    def _sampleidcs(self) -> list:
        """
         _sampleidcs returns the idcs from settings that are specific for sample.
         
         rather make this a section in conf?
         
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
            if idc in self._idckind and self._idckind[idc] == "SAMPLE":
                out.append(idc)
        # include the main sample idcontainer
        out.append(self.sidc())
        return out
    def _patientidcs(self, pidc:str=None) -> list:
        """
        """
        out = []
        for idc in self.settings["idc"]:
            if idc in self._idckind and self._idckind[idc] == "PATIENT":
                out.append(idc)
        # include the main patient idcontainer
        out.append(self.pidc(pidc))
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

    def _makemove(self, files:dict, lists:dict, idclists:dict, cutoff:int, pidc:str=None): # -> (dict, dict)
        """
         _makemove makes temporary tables for all files and all lists (non-idc
         and idc) that are larger than cutoff. moved lists are removed from
         lists and idclists, respectively. it returns a tuple holding dicts of
         the non-idc tables and the idc tables created.
        """
        files = self._concrete_idcs_dict(files, pidc=pidc)
        #print("files:")
        #print(files)
        (ttlists, ttidclists) = self._readfiles(files)
        _mvlists(lists, ttlists, cutoff)
        _mvlists(idclists, ttidclists, cutoff)
        tmptables = self._maketables(ttlists, "tmp_")
        idctmptables = self._maketables(ttidclists, "tmp_idc_")
        return (tmptables, idctmptables) 
    def _readfiles(self, files):
        """
         _readfiles reads the files from which tmp tables should be build into
         lists.  it returns a tuple of one dict holding the non-idc lists and
         one dict holding the idc lists.
        """
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
            if key in self._idcs:
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
            name = "tempdb..#" + prefix + key
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
            q = f"drop table {tablename}"
            #print(q)
            self.db.query(q)  # todo is kairos_spring used again after this?
