data = [
           {
               "key_as_string": "1980-01-01T00:00:00.000Z",
               "key": 315532800000,
               "doc_count": 1
            },
            {
               "key_as_string": "1981-01-01T00:00:00.000Z",
               "key": 347155200000,
               "doc_count": 1
            },
            {
               "key_as_string": "1982-01-01T00:00:00.000Z",
               "key": 378691200000,
               "doc_count": 2
            },
            {
               "key_as_string": "1983-01-01T00:00:00.000Z",
               "key": 410227200000,
               "doc_count": 2
            },
            {
               "key_as_string": "1984-01-01T00:00:00.000Z",
               "key": 441763200000,
               "doc_count": 3
            },
            {
               "key_as_string": "1985-01-01T00:00:00.000Z",
               "key": 473385600000,
               "doc_count": 4
            },
            {
               "key_as_string": "1986-01-01T00:00:00.000Z",
               "key": 504921600000,
               "doc_count": 6
            },
            {
               "key_as_string": "1987-01-01T00:00:00.000Z",
               "key": 536457600000,
               "doc_count": 5
            },
            {
               "key_as_string": "1988-01-01T00:00:00.000Z",
               "key": 567993600000,
               "doc_count": 2
            },
            {
               "key_as_string": "1989-01-01T00:00:00.000Z",
               "key": 599616000000,
               "doc_count": 7
            },
            {
               "key_as_string": "1990-01-01T00:00:00.000Z",
               "key": 631152000000,
               "doc_count": 8
            },
            {
               "key_as_string": "1991-01-01T00:00:00.000Z",
               "key": 662688000000,
               "doc_count": 9
            },
            {
               "key_as_string": "1992-01-01T00:00:00.000Z",
               "key": 694224000000,
               "doc_count": 16
            },
            {
               "key_as_string": "1993-01-01T00:00:00.000Z",
               "key": 725846400000,
               "doc_count": 18
            },
            {
               "key_as_string": "1994-01-01T00:00:00.000Z",
               "key": 757382400000,
               "doc_count": 21
            },
            {
               "key_as_string": "1995-01-01T00:00:00.000Z",
               "key": 788918400000,
               "doc_count": 25
            },
            {
               "key_as_string": "1996-01-01T00:00:00.000Z",
               "key": 820454400000,
               "doc_count": 21
            },
            {
               "key_as_string": "1997-01-01T00:00:00.000Z",
               "key": 852076800000,
               "doc_count": 10
            },
            {
               "key_as_string": "1998-01-01T00:00:00.000Z",
               "key": 883612800000,
               "doc_count": 21
            },
            {
               "key_as_string": "1999-01-01T00:00:00.000Z",
               "key": 915148800000,
               "doc_count": 36
            },
            {
               "key_as_string": "2000-01-01T00:00:00.000Z",
               "key": 946684800000,
               "doc_count": 27
            },
            {
               "key_as_string": "2001-01-01T00:00:00.000Z",
               "key": 978307200000,
               "doc_count": 17
            },
            {
               "key_as_string": "2002-01-01T00:00:00.000Z",
               "key": 1009843200000,
               "doc_count": 20
            },
            {
               "key_as_string": "2003-01-01T00:00:00.000Z",
               "key": 1041379200000,
               "doc_count": 20
            },
            {
               "key_as_string": "2004-01-01T00:00:00.000Z",
               "key": 1072915200000,
               "doc_count": 14
            },
            {
               "key_as_string": "2005-01-01T00:00:00.000Z",
               "key": 1104537600000,
               "doc_count": 15
            },
            {
               "key_as_string": "2006-01-01T00:00:00.000Z",
               "key": 1136073600000,
               "doc_count": 12
            },
            {
               "key_as_string": "2007-01-01T00:00:00.000Z",
               "key": 1167609600000,
               "doc_count": 7
            },
            {
               "key_as_string": "2008-01-01T00:00:00.000Z",
               "key": 1199145600000,
               "doc_count": 9
            },
            {
               "key_as_string": "2009-01-01T00:00:00.000Z",
               "key": 1230768000000,
               "doc_count": 9
            },
            {
               "key_as_string": "2010-01-01T00:00:00.000Z",
               "key": 1262304000000,
               "doc_count": 5
            },
            {
               "key_as_string": "2011-01-01T00:00:00.000Z",
               "key": 1293840000000,
               "doc_count": 8
            },
            {
               "key_as_string": "2012-01-01T00:00:00.000Z",
               "key": 1325376000000,
               "doc_count": 6
            },
            {
               "key_as_string": "2013-01-01T00:00:00.000Z",
               "key": 1356998400000,
               "doc_count": 7
            },
            {
               "key_as_string": "2014-01-01T00:00:00.000Z",
               "key": 1388534400000,
               "doc_count": 4
            }
           ]

import pandas as pd

df = pd.DataFrame(data)
df = pd.DataFrame.from_dict({'count': df['doc_count'], 'year':[a.split('-')[0] for a in df['key_as_string']]})

# df.hist()
