import re

tekst = "S1E2/4455"

series = re.match(r'([Ss](\d+))([Ee](\d+))?(\/(\d+))?', tekst)

print(series.group(2))
print(series.group(4))
print(series.group(6))

# for i in range(1,(len(series.groups())+1)):
#      print(series.group(i))
