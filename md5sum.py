__author__ = 'thejaswihr'
import hashlib

# Thank you to http://thejaswihr.blogspot.com.au/2008/06/python-md5-checksum-of-file.html for this.
def compute(fileName, excludeLine="", includeLine=""):
    """Compute md5 hash of the specified file"""
    m = hashlib.md5()
    fd = open(fileName,"rb")
    content = fd.readlines()
    fd.close()
    for eachLine in content:
        if excludeLine and eachLine.startswith(excludeLine):
            continue
        m.update(eachLine)
    m.update(includeLine)
    return m.hexdigest()