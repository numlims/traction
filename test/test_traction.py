import tr
def test_run():
    """
    """
    trac = tr.traction("num_test")
    res = trac.sample(sampleids=["abc"])
    assert len(res) == 0
