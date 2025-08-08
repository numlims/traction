import argparse
import tr
import simplejson as json
import sys
def add_args(parser, settings):
  for item in settings["sidc"]:
    parser.add_argument(f"--{item}", required=False, help=f"{item} sampleidcontainer")
def getsidc(args:dict, settings):
  out = {}
  for item in settings["sidc"]:
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

    parser.add_argument("what", help="sample|patient|finding|method|labval|name - finding: messbefund; method: messprofil; labval: messparam; name: table name for which the display names of the codes should be fetched.")
    parser.add_argument("--sampleid", required=False, help="sampleid(s)")
    #parser.add_argument("--sidtype", required=False, "sampleid type")
    #parser.add_argument("--extsampleid", required=False, help="external sampleid(s)")
    parser.add_argument("--patientid", required=False, help="patientid(s)")
    #parser.add_argument("--pidtype", required=False, "patientid type")    
    parser.add_argument("--study", required=False, help="study code(s)")    
    parser.add_argument("--locationpath", required=False, help="for locationpath(s)")
    parser.add_argument("--method", required=False, help="for labormethod(s) (messprofil)")
    parser.add_argument("--table", required=False, help="the table to get names for codes for")
    parser.add_argument("--ml-table", required=False, help="if the table mapping from codes to in mytable to names is not called centraxx_mytable_ml_name, give its name here.")
    parser.add_argument("--verbose", help="join in additional info, pass tr constants comma-seperated by comma, e.g. 'patientid,locationpath'") # -v?  nargs=1?
    parser.add_argument("--verbose-all", help="join in more info, takes longer", action="store_true") # -a?
    parser.add_argument("--missing", help="get missing. not yet implemented.", action="store_true") # -m?
    add_args(parser, settings)
    args = parser.parse_args()

    # print(args.verbose)
    # print(args)
    verbose = []
    if args.verbose != None:
        verbose = args.verbose.split(",")
    traction = tr.traction(args.db)
    sampleids = extsampleids = patientids = studies = locationpaths = methods = modules = tiers = None
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
    if args.study: 
        if "f" in args: # quickfix read from file if -f
            studies = open(args.study).read().split("\n") # list
        studies = args.study.split(",")        
    if args.locationpath: 
        if "f" in args: # quickfix read from file if -f
            locationpaths = open(args.locationpath).read().split("\n") # list
        locationpaths = args.locationpath.split(",")
    if args.method: 
        if "f" in args: # quickfix read from file if -f
            methods = open(args.method).read().split("\n") # list
        methods = args.method.split(",")
#    if args.module: 
#        if "f" in args: # quickfix read from file if -f   ## maybe --module-f, sampleid-f, etc
#            modules = open(args.module).read().split("\n") # list
#        modules = args.module.split(",")
#    if args.tier: 
#        if "f" in args: # quickfix read from file if -f   ## maybe --module-f, sampleid-f, etc
#            tiers = open(args.tier).read().split("\n") # list
#        tiers = args.tier.split(",")
        
    if args.what == "sample":
        sample = traction.sample(sampleids=sampleids, sidc=getsidc(vars(args), settings), patientids=patientids, studies=studies, locationpaths=locationpaths, verbose=verbose, verbose_all=args.verbose_all, missing=args.missing) # todo different arguments for string and array
        # print json
        print(json.dumps(sample, default=str))
    if args.what == "patient":
        patients = traction.patient(patientids=patientids, sampleids=sampleids, studies=studies)
        print(json.dumps(patients, default=str))
    if args.what == "labval":
        res = traction.labval(methods=methods)
        print(json.dumps(res, default=str))
    if args.what == "finding":
        res = traction.finding(sampleids=sampleids, methods=methods, studies=studies)
        print(json.dumps(res, default=str))
    if args.what == "name":
        # res = traction.name("laborfinding")
        res = traction.name(args.table, args.ml_table)
        print(json.dumps(res, default=str))


sys.exit(main())
