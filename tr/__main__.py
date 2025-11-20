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
     date can be passed, it needs to be preceeded by `=`, `>=` or `<=`, in
     this case just the first or second element of the tuple is set.  also
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

    parser.add_argument("what", help="sample|patient|trial|finding|method|name. finding: messbefund; method: messprofil; name: get display names for a table.") # labval: messparameter
    parser.add_argument("--sampleid", required=False, help="sampleid(s)")
    parser.add_argument("--patientid", required=False, help="patientid(s)")
    parser.add_argument("--parentid", required=False, help="sampleid(s) of parent samples")    
    parser.add_argument("--trial", required=False, help="trial code(s)")
    parser.add_argument("--locationpath", required=False, help="locationpath(s)")
    parser.add_argument("--kitid", required=False, help="kitid(s)")
    parser.add_argument("--cxxkitid", required=False, help="cxxkitid(s)")
    parser.add_argument("--category", required=False, help="MASTER|DERIVED|ALIQUOTGROUP")
    parser.add_argument("--orgunit", required=False, help="organisation unit")
    parser.add_argument("--sampling-date", required=False, help="sampling date from:to")
    parser.add_argument("--receipt-date", required=False, help="receipt date from:to")
    parser.add_argument("--derival-date", required=False, help="derival date from:to")    
    parser.add_argument("--first-reposition-date", required=False, help="first reposition date from:to")
    parser.add_argument("--reposition-date", required=False, help="reposition date from:to")
    parser.add_argument("--stockprocessing-date", required=False, help="first stock processing date from:to")
    parser.add_argument("--secondprocessing-date", required=False, help="second stock processing date from:to")
    parser.add_argument("--primary-ref", required=False, help="reference the primary of each derived, without including it", action="store_true")    
    parser.add_argument("--parents", required=False, help="include parents starting from the root", action="store_true")
    parser.add_argument("--childs", required=False, help="include the childs up to the leafs", action="store_true")
    parser.add_argument("--tree", required=False, help="include the whole tree for each sample", action="store_true")            
    parser.add_argument("--method", required=False, help="labormethod(s) (messprofil)")
    parser.add_argument("--table", required=False, help="the table to get names for codes for")
    parser.add_argument("--ml-table", required=False, help="if the table mapping from codes to in mytable to names is not called centraxx_mytable_ml_name, give its name here.")
    parser.add_argument("--verbose", help="comma-separated tr constants that should be joined in, e.g. 'patientid,locationpath'") # -v?  nargs=1?
    parser.add_argument("--verbose-all", help="join in all additional info, takes longer", action="store_true") # -a?
    parser.add_argument("--like", required=False, help="comma seperated list of tr constants where to check for like instead of equal")
    parser.add_argument("-f", required=False, help="comma seperated list of tr constants where files are passed")
    parser.add_argument("--missing", help="get missing. not yet implemented.", action="store_true") # -m?
    parser.add_argument("--where", required=False, help="additional sql where string")
    parser.add_argument("--order-by", required=False, help="order by on sql query level")
    parser.add_argument("--top", required=False, help="first n results on sql query level")    
    parser.add_argument("--query", required=False, help="print the query", action="store_true")
    parser.add_argument("--raw", help="return raw results", action="store_true")
    parser.add_argument("--csv", required=False, help="write results to csv file")
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
    sampleids = parentids = patientids = trials = locationpaths = kitids = cxxkitids = categories = methods = orgunits = likes = None
    if args.sampleid: # read sampleid from cmd line
        if "f" in args: # quickfix read from file if -f
            sampleids = open(args.sampleid).read().split("\n") # list
        sampleids = args.sampleid.split(",")
    if args.parentid: # read parentid from cmd line
        if "f" in args: # quickfix read from file if -f
            parentids = open(args.parentid).read().split("\n") # list
        parentids = args.parentid.split(",")
    if args.patientid: 
        if "f" in args: # quickfix read from file if -f
            patientids = open(args.patientid).read().split("\n") # list
        patientids = args.patientid.split(",")
    if args.trial: 
        if "f" in args: # quickfix read from file if -f
            trials = open(args.trial).read().split("\n") # list
        trials = args.trial.split(",")        
    if args.locationpath: 
        if "f" in args: # quickfix read from file if -f
            locationpaths = open(args.locationpath).read().split("\n") # list
        locationpaths = args.locationpath.split(",")
    if args.method: 
        if "f" in args: # quickfix read from file if -f
            methods = open(args.method).read().split("\n") # list
        methods = args.method.split(",")
    if args.kitid: 
        if "f" in args: # quickfix read from file if -f
            kitids = open(args.kitid).read().split("\n") # list
        kitids = args.kitid.split(",")
    if args.cxxkitid: 
        if "f" in args: # quickfix read from file if -f
            cxxkitids = open(args.cxxkitid).read().split("\n") # list
        cxxkitids = args.cxxkitid.split(",")
    if args.category: 
        if "f" in args: # quickfix read from file if -f
            categories = open(args.category).read().split("\n") # list
        categories = args.category.split(",")
    if args.orgunit: 
        if "f" in args: # quickfix read from file if -f
            orgunits = open(args.orgunit).read().split("\n") # list
        orgunits = args.orgunit.split(",")
    if args.like:
        # don't read as file
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
               where=args.where,
               order_by=args.order_by,
               top=args.top,
               print_query=args.query,
               raw=args.raw)
               
        if args.csv is not None:
            outfile = tr.idable_csv(sample, args.csv) # rename csv?
            if outfile is not None:
                print(outfile)
        else:
            print(jsonpickle.encode(sample, unpicklable=False)) # somehow include_properties=True doesn't work
    if args.what == "patient":
        patients = traction.patient(patientids=patientids,
            sampleids=sampleids,
            idc=getidc(vars(args), settings),
            trials=trials,
            orgas=orgunits,
            verbose=verbose,
            verbose_all=args.verbose_all,
            like=likes,
            order_by=args.order_by,
            top=args.top,
            print_query=args.query,
            raw=args.raw)
        #print(json.dumps(patients, default=str))
        print(jsonpickle.encode(patients, unpicklable=False))
    if args.what == "trial":
        res = traction.trial()
        print(json.dumps(res, default=str))
    if args.what == "method":
        res = traction.method(methods=methods)
        print(json.dumps(res, default=str))
    if args.what == "finding":
        res = traction.finding(sampleids=sampleids,
            patientids=patientids,
            idc=getidc(vars(args), settings),
            methods=methods,
            trials=trials,
            values=True, # todo make arg?
            print_query=args.query,
            raw=args.raw)
        print(jsonpickle.encode(res, unpicklable=False))
        #print(json.dumps(res, default=str))
    if args.what == "name":
        # res = traction.name("laborfinding")
        res = traction.name(args.table, args.ml_table)
        print(json.dumps(res, default=str))


sys.exit(main())
