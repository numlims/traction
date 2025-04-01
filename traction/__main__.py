# __main__.py is a little traction cli

import argparse
from traction import traction
import simplejson as json
import sys

# main offers a cli for traction
def main():
    # target = sys.argv[1]
    # operation = sys.argv[2]

    parser = argparse.ArgumentParser()

    # in any case take the database target
    parser.add_argument("target", help="db target")

    # after the target comes a subcommand. different subcommands come
    # with different flags, so make subparsers for them. dest: name of
    # the field to write to which subparser was selected
    subparsers = parser.add_subparsers(dest="operation")

    # the sample subparser
    parser_sample = subparsers.add_parser("sample", help="find sample(s)")
    parser_sample.add_argument("sampleid", help="sample id", nargs="?") # not required
    parser_sample.add_argument("-f", help="file with sample ids", required=False)
    parser_sample.add_argument("--verbose", help="join in more info for sample, takes longer", action=argparse.BooleanOptionalAction) # optional boolean flag

    # the patient subparser
    parser_patient = subparsers.add_parser("patient", help="find patient(s)")
    parser_patient.add_argument("--sample-id", required=False, help="find patient for sample")
    
    # parse all arguments, also for the subparsers
    args = parser.parse_args()

    tr = traction(args.target)

    # print(args.verbose)
    # print(args)

    # get a sample
    if args.operation == "sample":
        # print("f: " + args.f)

        # read sampleids from file
        if args.f:
            sampleids = open(args.f).read().split("\n") # list
        elif args.sampleid: # read sampleid from cmd line
            # sampleid = sys.argv[3] # string # todo parse arg
            sampleids = [args.sampleid]

        sample = tr.sample(sampleids=sampleids, verbose=args.verbose) # todo different arguments for string and array
        # print json
        print(json.dumps(sample, default=str))
    # get a patient
    if args.operation == "patient":
        #parser.add_argument("--sample-id", required=False)
        #args = parser.parse_args()
        if args.sample_id:
            sampleid = args.sample_id
            patient = tr.patient(sampleid=sampleid)
            print(json.dumps(patient, default=str))

# run
sys.exit(main())
