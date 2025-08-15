CULTURE_PARSE_ENTRY_RE = r'(?i)Rodzaj materiału:'
CULTURE_PARSE_SAMPLE_RE = r'(?i)Rodzaj materiału:\s+(.+\b)\s\s'
CULTURE_PARSE_DATE_RE = r'(?i)\bData zakończenia badania:\s+(\d{2}[-]\d{2}[-]\d{4})\s\s'
CULTURE_PARSE_DESCR_RE = r'(?i)\bOpis:\s+(.+)\s\s'
CULTURE_PARSE_NOTE_RE = r'(?i)\bUwagi:\s+(.+)\s\s'
CULTURE_PARSE_PATOGEN_RE = r'(?i)\bIzolacja:\s*(.+)\b\s\s+'

# MIND: IN CASE OF EDITING: CULTURE_PARSE_RESISTANCE_RE and CULTURE_PARSE_ABGRAM_RE must match
CULTURE_PARSE_RESISTANCE_RE = r'(?i)((\b.+):([OWSRI])\s*(MIC:\s*([<=>]{0,2}\d\d?([.,]\d\d?)?\b))?.*\s\s)'
CULTURE_PARSE_ABGRAM_RE = r'(?i)(Antybiogram:.*?\s\s((.+):([OWSRI])\s*(MIC:\s*([<=>]{0,2}\d\d?([.,]\d\d?)?\b))?.*\s\s)+)'

# bacterial resistance
INTERMEDIATE = 'i'
RESISTANT = 'r'
SENSITIVE = 's'
UNKNOWN = 'u'
