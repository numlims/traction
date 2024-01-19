# traction.py gives commonly used getters (and setters?) for centraxx db

# functions:

# smpl(?samplepsn, ?locationpath, ?like)
# patient(sampleid)

from dbcq import *

class traction:

    def __init__(self, target):
        self.db = dbcq(target)

    # smpl gives sample with psn or location
    # maybe pass arguments as dicts, to be able to specify equal or like matching, e.g. locationpath = {value:'<my locationpath>',like=True}
    def smpl(self, samplepsn = None, locationpath = None, like=False):
        # we would like to be able to return the column names prefixed by the table names, to avoid clashes when column names appear in more than one table. unfortunately there seems to be no standard sql way of doing this, see https://stackoverflow.com/a/57832920
        # so for now say: select <table short>.<column name> as '<table name>.<column name>'
        query = """
         select s.*,
        sidc.psn as 'sampleidcontainer.psn',
        samplelocation.locationid as 'samplelocation.locationid', samplelocation.locationpath as 'samplelocation.locationpath',
        sampletype.code as 'sampletype.code',
        stockprocessing.code as 'stockprocessing.code',
        secondprocessing.code as 'secondprocessing.code',
        project.code as 'project.code',
        receptable.code as 'receptable.code',
        orgunit.code as 'orgunit.code',
        flexistudy.code as 'flexistudy.code'
        from centraxx_sample s
        inner join centraxx_sampleidcontainer as sidc on sidc.sample = s.oid
        inner join centraxx_samplelocation samplelocation on samplelocation.oid = s.samplelocation
        inner join centraxx_sampletype as sampletype on sampletype.oid = s.sampletype
        inner join centraxx_stockprocessing as stockprocessing on stockprocessing.oid = s.stockprocessing
        left join centraxx_stockprocessing as secondprocessing on secondprocessing.oid = s.secondprocessing
        inner join centraxx_project as project on project.oid = s.project
        inner join centraxx_samplereceptable as receptable on receptable.oid = s.receptable
        inner join centraxx_organisationunit as orgunit on orgunit.oid = s.orgunit
        inner join centraxx_flexistudy as flexistudy on flexistudy.oid = s.flexistudy

        where sidc.idcontainertype = 6
        """
        args = []

        if samplepsn != None:
            query = query + " and " + self._wherestring("sidc.psn", like)
            args.append(samplepsn)
        if locationpath != None:
            query = query + " and " + self._wherestring("samplelocation.locationpath", like)
            args.append(locationpath)

        #print(query)
            
        return self.db.qfad(query, *args)

    # _wherestring gives a ?-parameterized sql where expression for name equal or like parameter for use in queries
    def _wherestring(self, name, like):
        if not like:
            return name + " = ?"
        else:
            return name + " like '%' + ? + '%'"
        
    # patient gives the patient of sample
    def patient(self, sampleid):
        # get from sample to patient: sample to patientcontainer, patientcontainer to idcontainer.
        query = """
        select idc.*, pc.* from centraxx_idcontainer idc
        inner join centraxx_patientcontainer pc on idc.patientcontainer = pc.oid
        inner join centraxx_sample s on s.patientcontainer = pc.oid
        where idc.idcontainertype = 8 and s.oid = ?
        """
        result = self.db.qfad(query, sampleid)
        if len(result) == 0:
            return None
        return result[0]
