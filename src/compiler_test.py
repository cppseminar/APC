import compiler

def test_env_parse_multiline():
    # TODO: Finish
    line1 = "SystemRoot=C:\\WINDOWS"
    line2 = "TEMP=C:\\Users\\LUKAS~1.MAN\\AppData\\Local\\Temp"
    line3 = "TMP=C:\\Users\\LUKAS~1.MAN\\AppData\\Local\\Temp"
    entry = ( line1 + "\n" +
              line2 + "\n" +
              line3 + "\n")
    print(compiler.parse_env(entry))

def test_diff1():
    line1 = "aaa"
    line2 = "aab"
    assert compiler.compare_strings(line1, line2)

def test_diff2():
    line1 = "aaa"
    line2 = "aaa"
    assert len(compiler.compare_strings(line1, line2)) is 0

def test_diff3():
    line1 = "\n".join(("aaa",
        "b bc"))
    line2 = "\n".join(("aaa",
        "b bc\n"))
    assert len(compiler.compare_strings(line1, line2)) is 0

def test_diff4():
    line1 = "\n".join(("aaa",
        "b bc"))
    line2 = "\n".join(("aaa",
        "b b c\n"))
    assert len(compiler.compare_strings(line1, line2)) is not 0

if __name__ == "__main__":
    test_env_parse_multiline()