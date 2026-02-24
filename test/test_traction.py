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
    res = trac.patient(sampleids=[sampleid])
    assert len(res) == 1
    pat = res[0]
    assert pat.id("LIMSPSN") == 28365
    res = trac.finding(sampleids=[sampleid])
    assert len(res) == 1
    finding = res[0]
    assert "DENGUE" in finding.recs["PATHOGEN2"].rec
