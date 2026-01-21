# automatically generated, DON'T EDIT. please edit init.ct from where this file stems.
from dbcq import *
import cnf
from datetime import datetime
from dip import dig, dis
from tram import Sample, Idable, Amount, Identifier
from tram import Patient
from tram import Finding
from tram import Rec, BooleanRec, NumberRec, StringRec, DateRec, MultiRec, CatalogRec
import csv
address = "address"
appointment = "appointment"
category = "category" # MASTER, ALIQUOTGROUP, DERIVED. dtype in db.
concentration = "concentration"
cxxkitid = "cxxkitid"
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
sampletype = "sampletype"
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

def idable_csv(idables:list, filename:str=None, *idcs) -> str:
    """
     idable_csv writes a list of Idables to the given csv file. the given
     idcontainers are included as columns. if no idcontainers are given, all
     are included.
    """
    if idables is None or len(idables) == 0: # todo throw error?
        print("no idables")
        return None
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(list(idables[0].iddict(*idcs).keys()))
        for idable in idables:
            d = idable.iddict()
            writer.writerow(list(d.values()))
    return filename

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

    def sample(self, sampleids:list=None, oids:list=None, idc=None, patientids:list=None, parentids:list=None, parentoids:list=None, locationpaths:list=None, trials:list=None, kitids:list=None, cxxkitids:list=None, categories:list=None, orgas:list=None, samplingdates=None, receiptdates=None, derivaldates=None, first_repositiondates=None, repositiondates=None, stockprocessingdates=None, secondprocessingdates=None, verbose=[], verbose_all=False, primaryref:bool=False, incl_parents:bool=False, incl_childs:bool=False, incl_tree:bool=False, like=[], missing=False, where=None, order_by=None, top=None, print_query:bool=False, raw:bool=False):
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
        # print("try:" + tr.sampleid)
        vaa = [cxxkitid, kitid, locationname, locationpath, orga, parentid, 
               project, receptacle, sampletype,
               secondprocessing, stockprocessing, trial]
        vaa.extend(self._patientidcs())
        vaa.extend(self._sampleidcs())                
        if not self.sidc() in verbose:
            verbose.insert(0, self.sidc())
        verbose = self._concrete_idcs(verbose)
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
        if not _checkverbose(verbose, vaa): 
            return None # throw error?
        if incl_parents or incl_childs or incl_tree or primaryref:
            verbosepass = []
            if primaryref:
                verbosepass = verbose
            res = self.sample(sampleids=sampleids, idc=idc, parentids=parentids, parentoids=parentoids, patientids=patientids, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, categories=categories, samplingdates=samplingdates, receiptdates=receiptdates, derivaldates=derivaldates, first_repositiondates=first_repositiondates, repositiondates=repositiondates, stockprocessingdates=stockprocessingdates, secondprocessingdates=secondprocessingdates, verbose=verbosepass, verbose_all=False, like=like, missing=missing, where=where, order_by=order_by, top=top, print_query=print_query)
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
        # todo check that self.sidc() is not in idc
        if idc is None:
           idc = {}
        if sampleids is not None:
           idc[self.sidc()] = sampleids
        if patientids is not None:
           idc[self.pidc()] = patientids
        jselects = {
            self.sidc(): [f"idc_{self.sidc()}.psn as '{sampleid}'"],
            self.pidc(): [f"idc_{self.pidc()}.psn as '{patientid}'"],                   
            cxxkitid: [f"samplekit.cxxkitid as '{cxxkitid}'"],
            #sampleid: [f"sidc.psn as '{sampleid}'"],
            parentid: [f"parentidc.psn as '{parentid}'"],
            kitid: [f"samplekit.kitid as '{kitid}'"],
            locationname: [f"samplelocation.locationid as '{locationname}'"], 
            locationpath: [f"samplelocation.locationpath as '{locationpath}'"],
            sampletype: [f"sampletype.code as '{sampletype}'"],
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
            sampletype: self.jd["sample_to_sampletype"],
            stockprocessing: self.jd["sample_to_stockprocessing"],
            secondprocessing: self.jd["sample_to_secondprocessing"],
            project: self.jd["sample_to_project"],
            receptacle: self.jd["sample_to_receptacle"],
            orga: self.jd["sample_to_orga"],
            trial: self.jd["sample_to_trial"]
        }
        for pidc in self._patientidcs():
            joins[pidc] = self.jd["sample_to_patient"]
        selectstr = self._selectstr(jselects, verbose, lselects, idc)  
        joinstr = self._joinstr(joins, verbose, idc)  
        (wherestr, whereargs) = self._where(idc=idc, sampleoids=oids, parentids=parentids, parentoids=parentoids, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, categories=categories, orgas=orgas, samplingdates=samplingdates, receiptdates=receiptdates, derivaldates=derivaldates, first_repositiondates=first_repositiondates, repositiondates=repositiondates, stockprocessingdates=stockprocessingdates, secondprocessingdates=secondprocessingdates, verbose=verbose, like=like, wherearg=where) 
        topstr = self._top(top)
        query = f"select {topstr} {selectstr} from centraxx_sample sample \n{joinstr} \nwhere {wherestr}"
        if order_by is not None:
            query += f" order by {order_by}"
        if print_query:
           print(query)
           print(whereargs)

        res = self.db.qfad(query, whereargs)
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
                patids.append(Identifier(id=dig(r, patientid), code=self.pidc()))
            patient = None
            if len(patids) > 0:
                patient = Idable(ids=patids, mainidc=self.pidc())
            s = Sample(
                appointment=dig(r, appointment),
                category=dig(r, category),
                samplingdate=dig(r, samplingdate),
                concentration=dig(r, concentration),
                cxxkitid=dig(r, cxxkitid),
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
                type=dig(r, sampletype),
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
    def patient(self, patientids=None, sampleids=None, idc=None, trials=None, orgas:list=None, verbose=[], verbose_all=False, like=[], order_by=None, top=None, print_query:bool=False, raw:bool=False):
        """
         patient gets patients and returns them as a list of Patient instances.
         
         the parameters work analog to the sample method.
        """
        vaa = [orga]
        vaa.extend(self._patientidcs())        
        if not self.pidc() in verbose:
            verbose.insert(0, self.pidc())
        verbose = self._concrete_idcs(verbose)
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
        # todo check that self.sidc() is not in idc
        if idc is None:
           idc = {}
        if sampleids is not None:
           idc[self.sidc()] = sampleids
        if patientids is not None:
           idc[self.pidc()] = patientids
           
        selects = {
            self.pidc(): [f"idc_{self.pidc()}.psn as '{patientid}'"],
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
        joinstr = self._joinstr(joins, verbose + silent, idc)  
        (wherestr, whereargs) = self._where(orgas=orgas, trials=trials, idc=idc, verbose=verbose, like=like)
        #print(whereargs)
        topstr = self._top(top)
        query = f"select distinct {topstr} {selectstr} from centraxx_patientcontainer patientcontainer \n{joinstr} \nwhere {wherestr}"
        if order_by is not None:
            query += f" order by {order_by}"
        if print_query:
           print(query)
        res = self.db.qfad(query, whereargs)
        if raw:
            return res
        pats = []
        for r in res:
            ids = [ Identifier(id=dig(r, patientid), code=self.pidc()) ]
            for idc in self._patientidcs():
                if idc in r and r[idc] is not None:
                    ids.append( Identifier(id=dig(r, idc), code=idc.upper()) )
            pat = Patient(
              ids=Idable(ids=ids, mainidc=self.pidc()),
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
    def finding(self, sampleids=None, patientids=None, idc=None, methods=None, trials=None, values:bool=True, verbose=[], verbose_all:bool=False, names:bool=False, top:int=None, print_query:bool=False, raw:bool=False):
        """
         finding gets the laborfindings ("messbefund" / "begleitschein") for
         sampleids or method.  it returns a list of Finding instances.
         
         you can pass these to verbose: tr.patientid  // maybe also tr.values?
        """
        vaa = [patientid] # include trial?
        if verbose_all == True:
            verbose = vaa
        if trials is not None:
            verbose.append(trial)
        if self.sidc() not in verbose:
            verbose.append(self.sidc())
        verbose = self._concrete_idcs(verbose)
        if idc is None:
           idc = {}
        # todo check that self.sidc() is not in idc
        if sampleids is not None:
           idc[self.sidc()] = sampleids
        if patientids is not None:
           idc[self.pidc()] = patientids
        selects = {
            self.sidc(): [f"idc_{self.sidc()}.psn as '{sampleid}'"],
            self.pidc(): [f"idc_{self.pidc()}.psn as '{patientid}'"],                   
        }
        idcselectstr = self._selectstr(selects, verbose, [], idc)  
        joins = {
            trial: self.jd["sample_to_trial"]
        }
        for pidc in self._patientidcs():
            joins[pidc] = self.jd["sample_to_patient"]
        idcjoinstr = self._joinstr(joins, verbose, idc)
        topstr = self._top(top)
        query = f"""select {topstr} laborfinding.oid as "laborfinding_oid", laborfinding.*, labormethod.code as {method}, {idcselectstr}
        from centraxx_laborfinding as laborfinding

        -- go from laborfinding to sample
        left join centraxx_labormethod as labormethod on laborfinding.labormethod = labormethod.oid
        left join centraxx_labormapping as labormapping on labormapping.laborfinding = laborfinding.oid
        left join centraxx_sample sample on labormapping.relatedoid = sample.oid
        {idcjoinstr}"""
        (wherestr, whereargs) = self._where(idc=idc, methods=methods, trials=trials)

        query += " where " + wherestr
        if print_query:
            print(query)
            print(whereargs)
        results = self.db.qfad(query, whereargs)
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
                patient=Idable(id=dig(res, patientid), code=self.pidc(), mainidc=self.pidc()) if dig(res, patientid) is not None else None, 
                recs=res["values"] if "values" in res else None, # todo None ok?
                sample=Idable(id=res[sampleid], code=self.sidc(), mainidc=self.sidc()),
                sender=None
            )
            findings.append(finding)
        return findings
    def method(self, methods=None):
        """
         method (messprofil) gets method(s) and their labvals (messparameter).
        """
        query = f"""select laborvalue.code as labval, labormethod.code as "method"
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
        bymethod = {}
        for row in res:
            if row["method"] not in bymethod:
                bymethod[row["method"]] = []
            bymethod[row["method"]].append(row["labval"])
        return bymethod
    def user(self, usernames:list=None, emails:list=None, lastlogin=None, verbose:list=[]):
        """
        """
        vaa = [tr.address, tr.login]
        if usernames:
            verbose.append(tr.username)
        if emails:
            verbose.append(tr.address)
        if lastlogin:
            verbose.append(tr.login)
        out = []
        for r in res:
            user = User(
                email=dig(r, tr.email),
                lastlogin=dig(r, tr.lastlogin),
                username=dig(r, tr.username),
            )
            out.append(user)
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
        return self.settings['sampleid'][self.db.target]
    def pidc(self) -> str:
        """
        """
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
    def _joinstr(self, joins, verbose, idc):
        """
         _joinstr puts together the joins needed by verbose array and idc keys
         and returns the sql join string.
        """
        joina = []
        joina = self._append_idc_join(joina, idc, verbose, joins)
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
    def _append_idc_join(self, joina, idc, verbose, joins):
        """
         _append_idc_join adds the sql join statements for an idc dict.
        """
        idca = []
        for verb in verbose:
          if verb in self.settings["idc"] or verb == self.sidc() or verb == self.pidc():
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
    def _where(self, idc={}, sampleoids:list=None, parentids:list=None, parentoids:list=None, patientids:list=None, trials:list=None, locationpaths:list=None, kitids:list=None, cxxkitids:list=None, categories:list=None, orgas:list=None, samplingdates=None, receiptdates=None, derivaldates=None, first_repositiondates=None, repositiondates=None, stockprocessingdates=None, secondprocessingdates=None, methods=None, like=[], verbose=[], wherearg:str=None): # -> (str, [])
        """
         _where returns the wherestring and args array for the provided
         arguments (that are not None).
         
         the user needs to make sure that whatever is referenced here is joined
         into the query before.
         
         the names are assumed to be the tr constants, like
         e.g. tr.sampleid. like is an array of tr constants of the arguments
         for which it checks likeness. we only check likeness for the first
         passed string of an argument array. if for example
         like=[tr.locationpath], it checks likeness of locationpaths[0].
         
         make sure only one of sampleids or extsampleids is passed?
        """
        wheredict = { 
          trial: { "arr": trials, "field": "flexistudy.code" },
          locationpath: { "arr": locationpaths, "field": "samplelocation.locationpath" },
          method: { "arr": methods, "field": "labormethod.code" },
          kitid: { "arr": kitids, "field": "samplekit.kitid" },
          cxxkitid: { "arr": cxxkitids, "field": "samplekit.cxxkitid" },
          category: { "arr": categories, "field": "sample.dtype" },
          orga: { "arr": orgas, "field": "organisationunit.code" },
          parentid: { "arr": parentids, "field": "parentidc.psn" },
          parentoid: { "arr": parentoids, "field": "sample.parent" },
          sampleoid: { "arr": sampleoids, "field": "sample.oid" },          
          samplingdate: { "arr": samplingdates, "field": "sample.samplingdate", "type": "date" },
          receiptdate: { "arr": receiptdates, "field": "sample.receiptdate", "type": "date" },
          derivaldate: { "arr": derivaldates, "field": "sample.derivaldate", "type": "date" },
          first_repositiondate: { "arr": first_repositiondates, "field": "sample.first_repositiondate", "type": "date" },
          repositiondate: { "arr": repositiondates, "field": "sample.repositiondate", "type": "date" },
          stockprocessingdate: { "arr": stockprocessingdates, "field": "sample.stockprocessingdate", "type": "date" },
          secondprocessingdate: { "arr": secondprocessingdates, "field": "sample.secondprocessingdate", "type": "date" }
        }
        idckeys = [] if idc is None else idc.keys()
        idca = list(idckeys) + list(set(verbose).intersection(self.settings["idc"]))
        for item in idca:
            wheredict[item] = {
                                "arr": idc[item] if idc is not None and item in idc else None,
                                "field": f"idc_{item}.psn"
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

        for key, row in wheredict.items():
            #print("key:" + key)

            # somehow printing here stops the keys from being iterated in the loop. why?
            #print("field: " + row["field"])
            
            if row["arr"] == None or len(row["arr"]) == 0:
                continue

            if likearr is not None and key in likearr:
                # put in an or-chain of like checks over all elements
                s = "(" + self._wherelikes(row["field"], len(row["arr"])) + ")"
                wherestrs.append(s)
                whereargs.extend(row["arr"])
            elif row["arr"] is not None and "type" in row and row["type"] == "date":
                if row["arr"] == 'NULL':
                    wherestrs.append("(" + row['field'] + " is NULL)")
                else:
                    s = f"(CAST(" + row['field'] + " as date) between ISNULL(?, " + row['field'] + ") and ISNULL(?, " + row['field'] + "))"
                    wherestrs.append(s)
                    whereargs.extend(row["arr"])
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
          self._idcoid[row["code"]] = row["oid"]
          self._idckind[row["code"]] = row["kind"]
    def _make_rec(self, recval, finding, names:bool=False) -> Rec:
        """
         _make_rec makes a recorded value instance for finding from db results with display names if wished.
        """
        out:Rec = None
        if recval["laborvalue_type"] == "BOOLEAN":
            val = True if recval["boolvalue"] == 1 else False
            out = BooleanRec(method=finding["method"], labval=recval["laborvalue_code"], value=val)
        elif recval["laborvalue_type"] == "DECIMAL":
            #print(recval["laborvalue_code"])
            #print(recval)
            value = float(recval["numericvalue"]) if recval["numericvalue"] is not None else None
            out = NumberRec(method=finding["method"], labval=recval["laborvalue_code"], value=value, unit=recval["laborvalue_unit"])
        elif recval["laborvalue_type"] == "STRING" or recval["laborvalue_type"] == "LONGSTRING":
            out = StringRec(method=finding["method"], labval=recval["laborvalue_code"], value=recval["stringvalue"])
        elif recval["laborvalue_type"] == "DATE":
            out = DateRec(method=finding["method"], labval=recval["laborvalue_code"], value=recval["datevalue"])
        elif recval["laborvalue_type"] == "LONGDATE":
            out = DateRec(method=finding["method"], labval=recval["laborvalue_code"], value=recval["datevalueprecision"])
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
                    value_name[code] = self.names_catalogentry[code]#bm
            
            out = CatalogRec(method=finding["method"], labval=recval["laborvalue_code"], catalog=catalog_code, value=entries, value_name=value_name)
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
            
            out = MultiRec(method=finding["method"], labval=recval["laborvalue_code"], value=entries, value_name=value_name)
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
    def _patientidcs(self) -> list:
        """
        """
        out = []
        for idc in self.settings["idc"]:
            if idc in self._idckind and self._idckind[idc] == "PATIENT":
                out.append(idc)
        # include the main patient idcontainer
        out.append(self.pidc())
        return out
    def _concrete_idcs(self, verbose):
        """
        """
        out = []
        for verb in verbose:
            if verb == patientid:
                out.append(self.pidc())
            elif verb == sampleid:
                out.append(self.sidc())
            else:
                out.append(verb)
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

