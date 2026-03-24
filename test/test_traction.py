# automatically generated, DON'T EDIT. please edit test.ct from where this file stems.
import tr
def test_run():
    """
    """
    sampleid = "1478370269"
    trac = tr.traction("num_test")
    res = trac.sample(sampleids=[sampleid], verbose_all=True)
    assert len(res) == 1
    sample = res[0]
    assert sample.locationpath == "NUM --> HGW Greifswald --> PP Lager RT SNID"
    assert sample.id("EXTSAMPLEID") == "asdf4"
    assert sample.patient.id("LIMSPSN") == "fim-1"
    res = trac.trial()
    hassnid = False
    for r in res:
        if r["code"] == "NUM S-SNID":
            hassnid = True
    assert hassnid == True
    res = trac.patient(sampleids=[sampleid])
    assert len(res) == 1
    pat = res[0]
    assert pat.id("LIMSPSN") == "fim-1"
    res = trac.finding(sampleids=[sampleid])
    assert len(res) == 1
    finding = res[0]
    assert "DENGUE" in finding.recs["PATHOGEN2"].rec
    res = trac.method()
    res = trac.user(usernames=["hauboldm"], verbose_all=True)
    assert res[0].email == "max.haubold@med.uni-greifswald.de"
    res = trac.catalog(catalogs=["PATHOGEN"])
    assert res["PATHOGEN"]["entries"]["CHIKUNGUNYA"]["name_de"] == "Chikungunya"
    res = trac.usageentry()
    assert res["YES"]["name_de"] == "ja"
