# automatically generated, DON'T EDIT. please edit main.ct from where this file stems.
import argparse
import cnf
from dbcq import dbcq
from dbcq import TargetException
import tr
import simplejson as json
import sys
import jsonpickle
import re
from datetime import datetime
def add_args(parser, settings):
    """
     add_args adds idc args from settings.
    """
    for item in settings["idc"]:
        parser.add_argument(f"--{item.lower()}", required=False, help=f"{item} idcontainer")
def getidc(args:dict, settings):
    """
     getidc filters the arg flags according to the idcs given in settings.
    """
    out = {}
    for item in settings["idc"]:

      if item.lower() in args and args[item.lower()] != None:
        out[item] = args[item.lower()].split(",")
    return out
def datespan(datestr:str, format:str="%Y-%m-%d"):
    """
     datespan turns a passed date argument like
     `%YYYY-%mm-%dd:%YYY-%mm-%dd` to a tuple of two dates. also just one
     date can be passed, it needs to be preceeded by `=`, `>=` or `<=`,
     then just the first or second element of the tuple is set.  also
     'NULL' can be passed, in this case not a tuple is retuned, but just
     the 'NULL' string.
    """
    if datestr is None:
        return None
    if datestr == 'NULL':
        return 'NULL'
    res = re.subn(r'^>=', '', datestr)
    if res[1] > 0:
        dfrom = datetime.strptime(res[0], format)
        return (dfrom, None)
    res = re.subn(r'^<=', '', datestr)
    if res[1] > 0:
        dto = datetime.strptime(res[0], format)
        return (None, dto)
    res = re.subn(r'^=', '', datestr)
    if res[1] > 0:
        d = datetime.strptime(res[0], format)
        return (d, d)
    a = datestr.split(":")
    if len(a) != 2:
       raise Exception("date needs to be in format >=from, <=to, =date or from:to.")
    dfrom = None
    dto = None
    dfrom = datetime.strptime(a[0], format)
    dto = datetime.strptime(a[1], format)
    return (dfrom, dto)
def lfpof(name:str, passed, files:list=None):
    """
     lfpof (list from param or file) reads values passed to a flag as comma
     seperated list or from file if the value is proceeded with f:.  if the
     files flag is passed, all params given to it are read from file, and
     all others as comma seperated list, irrespective of f:.
     
     if the flag was not set, None is returned.
    """
    if passed is None:
        if files is not None and name in files:
            raise Exception(f"error: {name} is listed in --files, please pass a file path to --{name}")
        else:
            return None
    if files is not None:
        if name in files:
            return lff(passed)
        else:
            return passed.split(",")
    else:
        res = re.subn(r'^f:', '', passed)
        if res[1] > 0: # count
            return lff(res[0])
        else:
            return passed.split(",")
def lff(path):
    """
     lff (list from file) reads the contents of a file and returns them as
     list by line.
    """
    with open(path) as f:
        return f.read().split("\n") 

def main():
    """
     main holds a cli for traction. it takes a database target and
     various search flags. see `traction -h`.
    """
    try:
        settings = cnf.makeload(path=".traction/settings.yaml", root=cnf.home, fmt="yaml", make=tr.cnftemplate)        
    except cnf.MakeCnfException as e:
        print("traction: " + str(e))
        return 1
    if settings == None:
        return
    parser = argparse.ArgumentParser()

    # in any case take the database target
    parser.add_argument("db", help="db target")

    parser.add_argument("what", help="sample|patient|trial|finding|method|user|name. finding: messbefund; method: messprofil; name: get display names for a table.") # labval: messparameter
    parser.add_argument("--sampleid", help="sampleid(s)")
    parser.add_argument("--patientid", help="patientid(s)")
    parser.add_argument("--parentid", help="sampleid(s) of parent samples")    
    parser.add_argument("--trial", help="trial code(s)")
    parser.add_argument("--locationpath", help="locationpath(s)")
    parser.add_argument("--kitid", help="kitid(s)")
    parser.add_argument("--cxxkitid", help="cxxkitid(s)")
    parser.add_argument("--category", help="MASTER|DERIVED|ALIQUOTGROUP")
    parser.add_argument("--orga", help="organisation unit")
    parser.add_argument("--sampling-date", help="sampling date from:to")
    parser.add_argument("--receipt-date", help="receipt date from:to")
    parser.add_argument("--derival-date", help="derival date from:to")    
    parser.add_argument("--first-reposition-date", help="first reposition date from:to")
    parser.add_argument("--reposition-date", help="reposition date from:to")
    parser.add_argument("--stockprocessing-date", help="first stock processing date from:to")
    parser.add_argument("--secondprocessing-date", help="second stock processing date from:to")
    parser.add_argument("--primary-ref", help="reference the primary of each derived, without including it", action="store_true")    
    parser.add_argument("--parents", help="include parents starting from the root", action="store_true")
    parser.add_argument("--childs", help="include the childs up to the leafs", action="store_true")
    parser.add_argument("--tree", help="include the whole tree for each sample", action="store_true")            
    parser.add_argument("--method", help="labormethod(s) (messprofil)")
    parser.add_argument("--table", help="the table to get names for codes for")
    parser.add_argument("--ml-table", help="if the table mapping from codes to in mytable to names is not called centraxx_mytable_ml_name, give its name here.")
    parser.add_argument("--username", help="the username of user(s).")
    parser.add_argument("--email", help="the email address of user(s).")                
    parser.add_argument("--last-login", help="the date of the user's last login.")
    parser.add_argument("--verbose", help="comma-separated tr constants that should be joined in, e.g. 'patientid,locationpath'") # -v?  nargs=1?
    parser.add_argument("--verbose-all", help="join in all additional info, takes longer", action="store_true") # -a?
    parser.add_argument("--names", help="add display names", action="store_true") 
    parser.add_argument("--like", help="comma seperated list of tr constants where to check for like instead of equal")
    parser.add_argument("--files", help="comma seperated list for which flags files are passed")
    parser.add_argument("--missing", help="get missing. not yet implemented.", action="store_true") # -m?
    parser.add_argument("--order-by", help="order by on sql query level")
    parser.add_argument("--top", help="first n results on sql query level")    
    parser.add_argument("--query", help="print the query", action="store_true")
    parser.add_argument("--raw", help="return raw results", action="store_true")
    parser.add_argument("--csv", help="write results to csv file")
    add_args(parser, settings)
    args = parser.parse_args()

    # print(args.verbose)
    # print(args)
    verbose = []
    if args.verbose != None:
        verbose = args.verbose.split(",")
    try:
        traction = tr.traction(args.db)
    except TargetException as e: # is this referencable from other packages?
        print("traction: " + str(e))
        return 1
    files = None
    if args.files is not None:
        files = args.files.split(",")
    sampleids = lfpof(tr.sampleid, args.sampleid, files)
    parentids = lfpof(tr.parentid, args.parentid, files)
    patientids = lfpof(tr.patientid, args.patientid, files)
    trials = lfpof(tr.trial, args.trial, files)
    locationpaths = lfpof(tr.locationpath, args.locationpath, files)
    methods = lfpof(tr.method, args.method, files)
    kitids = lfpof(tr.kitid, args.method, files)
    cxxkitids = lfpof(tr.cxxkitid, args.cxxkitid, files)
    categories = lfpof(tr.category, args.category, files)
    orgas = lfpof(tr.orga, args.orga, files)
    usernames = lfpof(tr.username, args.username, files)
    emails = lfpof(tr.email, args.email, files)        
    likes = None
    if args.like:
        likes = args.like.split(",")
    if args.what == "sample":
        sample = traction.sample(
               sampleids=sampleids,
               idc=getidc(vars(args), settings),
               parentids=parentids,
               patientids=patientids,
               trials=trials,
               locationpaths=locationpaths,
               kitids=kitids,
               cxxkitids=cxxkitids,
               categories=categories,
               orgas=orgas,
               samplingdates=datespan(args.sampling_date),
               receiptdates=datespan(args.receipt_date),
               derivaldates=datespan(args.derival_date),
               first_repositiondates=datespan(args.first_reposition_date),
               repositiondates=datespan(args.reposition_date),
               stockprocessingdates=datespan(args.stockprocessing_date),
               secondprocessingdates=datespan(args.secondprocessing_date),
               verbose=verbose,
               verbose_all=args.verbose_all,
               primaryref=args.primary_ref,
               incl_parents=args.parents,
               incl_childs=args.childs,
               incl_tree=args.tree,
               like=likes,
               missing=args.missing,
               order_by=args.order_by,
               top=args.top,
               print_query=args.query,
               raw=args.raw)
               
        if args.csv is not None:
            outfile = tr.idable_csv(sample, args.csv) # rename csv?
            if outfile is not None:
                print(outfile)
        else:
            print(jsonpickle.encode(sample, unpicklable=False, indent=4)) # somehow include_properties=True doesn't work
    elif args.what == "patient":
        patients = traction.patient(patientids=patientids,
            sampleids=sampleids,
            idc=getidc(vars(args), settings),
            trials=trials,
            orgas=orgas,
            verbose=verbose,
            verbose_all=args.verbose_all,
            like=likes,
            order_by=args.order_by,
            top=args.top,
            print_query=args.query,
            raw=args.raw)
        #print(json.dumps(patients, default=str))
        print(jsonpickle.encode(patients, unpicklable=False, indent=4))
    elif args.what == "trial":
        res = traction.trial()
        print(json.dumps(res, default=str, indent=4))
    elif args.what == "method":
        res = traction.method(methods=methods)
        print(json.dumps(res, default=str, indent=4))
    elif args.what == "finding":
        res = traction.finding(sampleids=sampleids,
            patientids=patientids,
            idc=getidc(vars(args), settings),
            methods=methods,
            trials=trials,
            values=True, # todo make arg?
            names=args.names,
            top=args.top,
            print_query=args.query,
            verbose_all=args.verbose_all,
            raw=args.raw)
        print(jsonpickle.encode(res, unpicklable=False, indent=4))
        #print(json.dumps(res, default=str, indent=4))
    elif args.what == "user":
        res = traction.user(username=usernames, emails=emails, lastlogin=datespan(args.last_login), verbose=verbose)
        print(jsonpickle.encode(res, unpicklable=False, indent=4))
    elif args.what == "name":
        # res = traction.name("laborfinding")
        res = traction.name(args.table, args.ml_table)
        print(json.dumps(res, default=str, indent=4))
    else:
        print(f"error: {args.what} not recognized. see traction -h.")
        return 1


sys.exit(main())
