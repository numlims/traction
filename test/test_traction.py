# automatically generated, DON'T EDIT. please edit test.ct from where this file stems.
import tr
def test_run():
    """
    """
    sampleid = "1478370269"
    trac = tr.traction("num_test")
    res = trac.sample(sampleids=[sampleid])
    assert len(res) == 1
    res = trac.patient(sampleids=[sampleid])
    assert len(res) == 1
    res = trac.finding(sampleids=[sampleid])
    assert len(res) == 1
