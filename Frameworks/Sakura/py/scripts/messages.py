# coding: utf8
# initmsg.py
# 3/26/2014 jichi

def info(name='', location='', urls=[], size=0):
  urls = '\n         '.join(urls)
  print """\
VNR is fetching "{name}" now, which is at least {size} bytes.
This usually takes less than 15min.

If VNR hangs for a long time because of the slow Internet, or, say,
if you are temporarily in Mainland China, you can also manually
download the archive and extract it to the following location.
Be careful that the location name is case-sensitive.

    Name: {name}
    Location: {location}
    URL: {urls}
""".format(**locals())

if __name__ == '__main__':
  info(
    name="UniDic",
    location="Caches/Dictionaries/UniDic",
    size=123,
    urls=[
      'http://www.google.com',
      'http://www.twitter.com',
    ],
  )

# EOF
