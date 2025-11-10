# automatically generated, DON'T EDIT. please edit main.ct from where this file stems.
import argparse
import cnf
from dbcq import dbcq
from dbcq import TargetException
import tr
import simplejson as json
import sys
import jsonpickle
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
def datefromto(datestr):
    """
     datefromto turns a passed datestring like `%YYYY-%mm-%dd:%YYY-%mm-%dd`
     into a tuple of two and from dates.
    """
    if datestr is None:
        return None
    a = datestr.split(":")
    if len(a) != 2:
       raise Exception("date needs to be in format <from>:<to>, <from> or <to> can be left out.")
    dfrom = None
    dto = None
    dfrom = datetime.strptime(a[0], "%Y-%m-%d")
    dto = datetime.strptime(a[1], "%Y-%m-%d")    
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
    parser.add_argument("--method", required=False, help="labormethod(s) (messprofil)")
    parser.add_argument("--table", required=False, help="the table to get names for codes for")
    parser.add_argument("--ml-table", required=False, help="if the table mapping from codes to in mytable to names is not called centraxx_mytable_ml_name, give its name here.")
    parser.add_argument("--verbose", help="comma-separated tr constants for additional info, e.g. 'patientid,locationpath'") # -v?  nargs=1?
    parser.add_argument("--verbose-all", help="join in all additional info, takes longer", action="store_true") # -a?
    parser.add_argument("--like", required=False, help="list of arguments where to check for like instead of equal")
    parser.add_argument("--missing", help="get missing. not yet implemented.", action="store_true") # -m?
    parser.add_argument("--where", required=False, help="additional sql where string")
    parser.add_argument("--order-by", required=False, help="order by on sql query level")
    parser.add_argument("--top", required=False, help="first n results on sql query level")    
    parser.add_argument("--query", required=False, help="print the query", action="store_true")
    parser.add_argument("--raw", help="return raw results", action="store_true")
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
    sampleids = extsampleids = patientids = trials = locationpaths = kitids = cxxkitids = categories = methods = orgunits = likes = None
    if args.sampleid: # read sampleid from cmd line
        if "f" in args: # quickfix read from file if -f
            sampleids = open(args.sampleid).read().split("\n") # list
        sampleids = args.sampleid.split(",")
#    if args.extsampleid: 
#        if "f" in args: # quickfix read from file if -f
#            extsampleids = open(args.extsampleid).read().split("\n") # list
#        extsampleids = args.extsampleid.split(",")
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
        sample = traction.sample(sampleids=sampleids, idc=getidc(vars(args), settings), patientids=patientids, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, categories=categories, samplingdates=datefromto(args.sampling_date), receiptdates=datefromto(args.receipt_date), derivaldates=datefromto(args.derival_date), first_repositiondates=datefromto(args.first_reposition_date), repositiondates=datefromto(args.reposition_date), verbose=verbose, verbose_all=args.verbose_all, like=likes, missing=args.missing, where=args.where, order_by=args.order_by, top=args.top, print_query=args.query) 
        # print json
        #print(json.dumps(sample, default=str))
        print(jsonpickle.encode(sample, unpicklable=False))
    if args.what == "patient":
        patients = traction.patient(patientids=patientids, sampleids=sampleids, idc=getidc(vars(args), settings), trials=trials, orgas=orgunits, verbose=verbose, verbose_all=args.verbose_all, like=likes, order_by=args.order_by, top=args.top, print_query=args.query)
        #print(json.dumps(patients, default=str))
        print(jsonpickle.encode(patients, unpicklable=False))
    if args.what == "trial":
        res = traction.trial()
        print(json.dumps(res, default=str))
    if args.what == "method":
        res = traction.method(methods=methods)
        print(json.dumps(res, default=str))
    if args.what == "finding":
        res = traction.finding(sampleids=sampleids, patientids=patientids, idc=getidc(vars(args), settings), methods=methods, trials=trials, print_query=args.query, raw=args.raw)
        print(jsonpickle.encode(res, unpicklable=False))
        #print(json.dumps(res, default=str))
    if args.what == "name":
        # res = traction.name("laborfinding")
        res = traction.name(args.table, args.ml_table)
        print(json.dumps(res, default=str))


sys.exit(main())
