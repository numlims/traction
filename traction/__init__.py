# traction.py gives commonly used getters (and setters?) for centraxx db

# functions:

# smpl(?samplepsn, ?locationpath, ?like)
# patient(sampleid)

from dbcq import *

class traction:

    #def __init__(self, target):
    #    self.db = dbcq(target)
    external_sampleid_type = "..."
    sampleid_type = "..."

    def __init__(self, target):
        """__init__ takes the db target either as string or dbcq object."""
        # pass a string argument to dbcq
        if isinstance(target, str):
            self.db = dbcq(target)
        elif isinstance(target, dbcq): # use dbcq instance directly
            self.db = target
        else:
            raise Exception("target needs to be string or dbcq instance")
        
    #get("sample", "samplelocation.locationpath = 'dresden'")
    # get pspawn samples with patients, wobei, das waer schon fast unabhaengig von centraxx db
    # a|b ist nur moeglich, wenn maximal ein fk aus b a referenziert, sonst error
    #get("sample.patientcontainer|idcontainer.psn, sample|sampleidcontainer.psn", where="idcontainer like 'pspawn' and sampleidcontainer.idcontainertype=6")
    
    
    def sample(self, sampleids=None, extsampleids=None, verbose=False):
        """sample gets sample(s) by sampleid or external id. pass sampleids as array. to join in more information, say verbose=True, this is slower than non-verbose."""

        # ids used in query
        queryids = []
        
        # set the idcontainer type we search for
        if not sampleids == None:
            idcontainertype = 6
            queryids = sampleids
        if not extsampleids == None:
            idcontainertype = 7
            queryids = extsampleid
            
        psnwhere = "in " + traction._sqlinplaceholder(len(queryids))

        # todo for verbose and non-verbose: incorporate where locationpath (and like)? like this: (see smpl in dump.txt)
        """
        if queryids != None:
            # query = query + " and " + self._whereparam("sidc.psn", like=like)
            query = query + f" and sidc.psn {psnwhere} "
            args.append(queryids)
        if locationpath != None:
            query = query + " and " + self._whereparam("samplelocation.locationpath", like=like)
            args.append(locationpath)
        """
        
        if not verbose:
            # a non-verbose query (quicker)
            query = f"select s.*, c.psn as 'sampleidcontainer.psn' from centraxx_sample s inner join centraxx_sampleidcontainer as c on c.sample = s.oid where c.idcontainertype = {idcontainertype} and c.psn {psnwhere}"
            
        else:
            # a verbose query (slower)
            # we would like to be able to return the column names prefixed by the table names, to avoid clashes when column names appear in more than one table. unfortunately there seems to be no standard sql way of doing this, see https://stackoverflow.com/a/57832920
            # so for now say: select <table short>.<column name> as '<table name>.<column name>'

            # use left joins to return something if a value is null
            query = f"""
            select s.*,
            sidc.psn as 'sampleidcontainer.psn',
            samplelocation.locationid as 'samplelocation.locationid', 
            samplelocation.locationpath as 'samplelocation.locationpath',
            sampletype.code as 'sampletype.code',
            stockprocessing.code as 'stockprocessing.code',
            secondprocessing.code as 'secondprocessing.code',
            project.code as 'project.code',
            receptable.code as 'receptable.code',
            orgunit.code as 'orgunit.code',
            flexistudy.code as 'flexistudy.code'
            from centraxx_sample s
            inner join centraxx_sampleidcontainer as sidc on sidc.sample = s.oid
            left join centraxx_samplelocation samplelocation on samplelocation.oid = s.samplelocation
            left join centraxx_sampletype as sampletype on sampletype.oid = s.sampletype
            left join centraxx_stockprocessing as stockprocessing on s.stockprocessing = stockprocessing.oid
            left join centraxx_stockprocessing as secondprocessing on s.secondprocessing = secondprocessing.oid
            left join centraxx_project as project on s.project = project.oid
            left join centraxx_samplereceptable as receptable on s.receptable = receptable.oid
            left join centraxx_organisationunit as orgunit on s.orgunit = orgunit.oid
            left join centraxx_flexistudy as flexistudy on s.flexistudy = flexistudy.oid
            
            where sidc.idcontainertype = {idcontainertype}
            and sidc.psn {psnwhere}
            """
            
        result = self.db.qfad(query, queryids) 

        return result

    def _sqlinplaceholder(n):
        """_sqlinplaceholder returns a string like (?, ?, ?, ? ...) with n question marks for sql in"""
        # put this in a package sqlutil?

        out = "("
        for i in range(n):
            out += "?"
            if i < n - 1:
                out += ","
        out += ")"
        return out

    def _whereparam(self, name, like:bool=None):
        """_wherestring gives a ?-parameterized sql where expression for name equal or like parameter for use in queries"""

        if like == None or like == False:
            return name + " = ?"
        else:
            return name + " like '%' + ? + '%'"
        

    def patient(self, sampleid:str=None):
        """patient gives the patient of sample."""
        
        # get from sample to patient psn: sample to patientcontainer, patientcontainer to idcontainer, idcontainer has psn.
        query = """
        select idc.psn as "idcontainer.psn", pc.* from centraxx_idcontainer idc
        inner join centraxx_patientcontainer pc on idc.patientcontainer = pc.oid
        inner join centraxx_sample s on s.patientcontainer = pc.oid
        join centraxx_sampleidcontainer sidc on sidc.sample = s.oid
        where idc.idcontainertype = 8 and sidc.psn = ?
        """
        result = self.db.qfad(query, sampleid)
        if len(result) == 0:
            return None
        return result[0]


    def name(self, table:str, code:str=None, lang:str=None, ml_table:str=None):
        """name gives the name for a code or a list of names for all codes in a table in de or en.
        table: the name of the centraxx table without centraxx_ prefix
        code: the code
        lang: de|en
        ml_table: if the table connecting to multilingualentry is named different, give it here. eg: name('laborvaluegroup', ... ml_name='labval_grp_ml_name')"""

        # interlacing the table name assumes that the referencing pattern for multilingual entries stays the same across table names.
        query = "select [" + table + "].code, multilingual.value as name, multilingual.lang as lang"
        query += " from [centraxx_" + table + "] as [" + table + "]"
        # put together the name for the ml_table
        ml_name = ""
        if ml_table != None: # the name is different
            ml_name = "centraxx_" + ml_table
        else: # the name is the same
            ml_name = "centraxx_" + table + "_ml_name"
        query += " inner join [" + ml_name + "] mlname on mlname.related_oid = [" + table + "].oid"
        query += " inner join centraxx_multilingualentry multilingual on mlname.oid = multilingual.oid"
        
        # restrict the query to specific lang or code if given
        wherestrings = []
        args = []
        if code != None:
            wherestrings.append(self._whereparam("[" + table + "].code"))
            args.append(code)
        if lang != None:
            wherestrings.append(self._whereparam("multilingual.lang"))
            args.append(lang)


        # only add sql-where if needed
        if len(wherestrings) > 0:
            query += " where "
            # join where clauses by and
            query += " and ".join(wherestrings)

        # print(query)


        # return the result
        res = self.db.qfad(query, *args)
        return res


    def names_by_codes(self, table:str, lang:str, ml_table:str=None):
        """names_by_code returns the multilingual name entries by code for quick access. for params see name()
        e.g.:
        names_by_codes("laborvalue", "de") returns:
        {
          "NUM_STOOL_LAXATIVE": "Abführmittel",
          "NUM_NMR_ACETONE_VALUE": "Aceton",
          ...
        }
        """

        # get the full result
        res = self.name(table, lang=lang, ml_table=ml_table)

        # key by code
        out = {}
        for line in res:
            out[line["code"]] = line["name"]
            
        return out
    
            
