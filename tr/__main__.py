import argparse
import tr
import simplejson as json
import sys
def add_args(parser, settings):
  for item in settings["idc"]:
    parser.add_argument(f"--{item}", required=False, help=f"{item} sampleidcontainer")
def getidc(args:dict, settings):
  out = {}
  for item in settings["idc"]:
    if item in args and args[item] != None:
      out[item] = args[item].split(",")
  return out
def main():
    settings = tr._readsettings()
    if settings == None:
        return
    parser = argparse.ArgumentParser()

    # in any case take the database target
    parser.add_argument("db", help="db target")

    parser.add_argument("what", help="sample|patient|trial|finding|method|labval|name - finding: messbefund; method: messprofil; labval: messparam; name: table name for which the display names of the codes should be fetched.")
    parser.add_argument("--sampleid", required=False, help="sampleid(s)")
    parser.add_argument("--patientid", required=False, help="patientid(s)")
    parser.add_argument("--trial", required=False, help="trial code(s)")
    parser.add_argument("--locationpath", required=False, help="locationpath(s)")
    parser.add_argument("--kitid", required=False, help="kitid(s)")
    parser.add_argument("--cxxkitid", required=False, help="cxxkitid(s)")
    parser.add_argument("--dtype", required=False, help="MASTER|DERIVED|ALIQUOTGROUP")
    parser.add_argument("--orgunit", required=False, help="organisation unit")    
    parser.add_argument("--method", required=False, help="for labormethod(s) (messprofil)")
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
    add_args(parser, settings)
    args = parser.parse_args()

    # print(args.verbose)
    # print(args)
    verbose = []
    if args.verbose != None:
        verbose = args.verbose.split(",")
    traction = tr.traction(args.db)
    sampleids = extsampleids = patientids = trials = locationpaths = kitids = cxxkitids = dtypes = methods = orgunits = likes = None
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
    if args.dtype: 
        if "f" in args: # quickfix read from file if -f
            dtypes = open(args.dtype).read().split("\n") # list
        dtypes = args.dtype.split(",")
    if args.orgunit: 
        if "f" in args: # quickfix read from file if -f
            orgunits = open(args.orgunit).read().split("\n") # list
        orgunits = args.orgunit.split(",")
    if args.like:
        # don't read as file
        likes = args.like.split(",")
        
        
    if args.what == "sample":
        sample = traction.sample(sampleids=sampleids, idc=getidc(vars(args), settings), patientids=patientids, trials=trials, locationpaths=locationpaths, kitids=kitids, cxxkitids=cxxkitids, dtypes=dtypes, verbose=verbose, verbose_all=args.verbose_all, like=likes, missing=args.missing, where=args.where, order_by=args.order_by, top=args.top, print_query=args.query) # todo different arguments for string and array
        # print json
        print(json.dumps(sample, default=str))
    if args.what == "patient":
        patients = traction.patient(patientids=patientids, trials=trials, orgunits=orgunits, verbose=verbose, verbose_all=args.verbose_all, like=likes, order_by=args.order_by, top=args.top, print_query=args.query)
        print(json.dumps(patients, default=str))
    if args.what == "trial":
        res = traction.trial()
        print(json.dumps(res, default=str))
    if args.what == "labval":
        res = traction.labval(methods=methods)
        print(json.dumps(res, default=str))
    if args.what == "finding":
        res = traction.finding(sampleids=sampleids, methods=methods, trials=trials)
        print(json.dumps(res, default=str))
    if args.what == "name":
        # res = traction.name("laborfinding")
        res = traction.name(args.table, args.ml_table)
        print(json.dumps(res, default=str))


sys.exit(main())
