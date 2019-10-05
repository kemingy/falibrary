from falibrary.utils import parse_path


def test_parse():
    # non variable
    uri = '/api/predict'
    path, param = parse_path(uri)
    assert path == uri , "Path fault"
    assert param == [] , "Param Fault"
