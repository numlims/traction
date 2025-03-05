# __main__.py is a little traction cli

import argparse
from traction import traction
import simplejson as json
import sys

# main offers a cli for traction
def main():
    target = sys.argv[1]
    operation = sys.argv[2]

    tr = traction(target)

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="db target")
    parser.add_argument("method", help="method")

    # get a sample
    if operation == "sample":
        parser.add_argument("-f", help="sample ids", required=False)
        args = parser.parse_args()
        # read sampleids from file
        if args.f:
            sampleid = open(args.f).read().split("\n") # list
        else: # read sampleid from cmd line
            sampleid = sys.argv[3] # string
        sample = tr.sample(sampleid=sampleid)
        # print json
        print(json.dumps(sample, default=str))
    # get a patient
    if operation == "patient":
        parser.add_argument("--sample-id", required=False)
        args = parser.parse_args()
        if args.sample_id:
            sampleid = args.sample_id
            patient = tr.patient(sampleid=sampleid)
            print(json.dumps(patient, default=str))

# run
sys.exit(main())
