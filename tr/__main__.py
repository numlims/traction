import argparse
import tr
import simplejson as json
import sys
def main():
    parser = argparse.ArgumentParser()

    # in any case take the database target
    parser.add_argument("db", help="db target")

    parser.add_argument("what", help="sample|patient|finding|method|labval|name - finding: messbefund; method: messprofil; labval: messparam; name: en and de display names for code field in table")
    parser.add_argument("--sampleid", required=False, help="for sampleid(s)")
    parser.add_argument("--extsampleid", required=False, help="for sampleid(s)")
    parser.add_argument("--patientid", required=False, help="for patient(s)")
    parser.add_argument("--locationpath", required=False, help="for locationpath(s)")
    parser.add_argument("--method", required=False, help="for labormethod(s) (messprofil)")
    parser.add_argument("--verbose", nargs=1, help="join in additional info, pass tr constants comma-seperated by comma, e.g. 'patientid,locationpath'") # -v?
    parser.add_argument("--verbose-all", help="join in more info, takes longer", action="store_true") # -a?
    
    # parse all arguments, also for the subparsers
    args = parser.parse_args()


    # print(args.verbose)
    # print(args)
    traction = tr.traction(args.db)
    sampleids = extsampleids = patientids = locationpaths = methods = None
    if args.sampleid: # read sampleid from cmd line
        if "f" in args: # quickfix read from file if -f
            sampleids = open(args.sampleid).read().split("\n") # list
        sampleids = args.sampleid.split(",")
    if args.extsampleid: 
        if "f" in args: # quickfix read from file if -f
            extsampleids = open(args.extsampleid).read().split("\n") # list
        extsampleids = args.extsampleid.split(",")
    if args.patientid: 
        if "f" in args: # quickfix read from file if -f
            patientids = open(args.patientid).read().split("\n") # list
        patientids = args.patientid.split(",")
    if args.locationpath: 
        if "f" in args: # quickfix read from file if -f
            locationpaths = open(args.locationpath).read().split("\n") # list
        locationpaths = args.locationpath.split(",")
    if args.method: 
        if "f" in args: # quickfix read from file if -f
            methods = open(args.method).read().split("\n") # list
        methods = args.method.split(",")
    if args.what == "sample":
        sample = traction.sample(sampleids=sampleids, extsampleids=extsampleids, patientids=patientids, locationpaths=locationpaths, verbose_all=args.verbose_all) # todo different arguments for string and array
        # print json
        print(json.dumps(sample, default=str))
    if args.what == "patient":
        patients = traction.patient(patientids=patientids, sampleids=sampleids)
        print(json.dumps(patients, default=str))
    if args.what == "labval":
        res = traction.labval(methods=methods)
        print(json.dumps(res, default=str))
    if args.what == "name":
        res = traction.name("laborfinding")
        # res = traction.name(args.table, args.ml_table)
        print(json.dumps(res, default=str))

sys.exit(main())
