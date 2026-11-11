import pytest
from lxml import etree

from globe import speech_fixes as sf

T = "http://www.tei-c.org/ns/1.0"


def body():
    return etree.fromstring(f"""<body xmlns="{T}"><div n="4"><div n="1">
<sp who="pet."><speaker>Pet.</speaker><l>Where is the life that late I led?</l></sp>
<sp who="pet."><speaker>Pet.</speaker><l>He kills her in her own humour.</l></sp>
</div><div n="2">
<sp who="g"><speaker>First Gent.</speaker><p>One.</p></sp>
<sp who="g"><speaker>Sec. Gent.</speaker><p>Two.</p></sp>
<sp who="g"><speaker>Sec. Gent.</speaker><p>Three.</p></sp>
</div></div></body>""")


def fix(**kw):
    base = dict(play="x", scene="", label="", first_words="", who_from="", who_to="", label_to="")
    return sf.Fix(**{**base, **kw})


def whos(b):
    return [(sp.get("who"), sp.find(f"{{{T}}}speaker").text) for sp in b.iter(f"{{{T}}}sp")]


def test_one_speech_by_first_words():
    b = body()
    sf.apply(b, [fix(scene="4.1", label="Pet.", first_words="he kills her", who_from="pet.",
                     who_to="peter.", label_to="Peter.")])
    assert whos(b)[:2] == [("pet.", "Pet."), ("peter.", "Peter.")]


def test_every_speech_by_label():
    b = body()
    sf.apply(b, [fix(label="Sec. Gent.", who_from="g", who_to="g2")])
    assert [w for w, _ in whos(b)[2:]] == ["g", "g2", "g2"]


def test_no_match_stops():
    with pytest.raises(sf.SpeechFixError):
        sf.apply(body(), [fix(scene="4.2", label="Pet.", who_from="pet.", who_to="peter.")])


def test_first_words_matching_two_stops():
    with pytest.raises(sf.SpeechFixError):
        sf.apply(body(), [fix(label="Sec. Gent.", first_words="", who_from="g", who_to="g2",
                              scene="4.9")])


def test_read_table(tmp_path):
    p = tmp_path / "t.tsv"
    p.write_bytes(b"# c\r\n" + "\t".join(sf.COLUMNS).encode() + b"\r\n\t\t\t\r\n"
                  b"shr\t4.1\tPet.\the kills\tpet.\tpeter.\tPeter.\t\tn\r\n")
    (r,) = sf.read_table(p)
    assert r.who_to == "peter." and r.pending
