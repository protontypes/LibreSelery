
def getOrUpdateDict(dict, key, defaultValue):
  if not key in dict:
    dict[key] = defaultValue

  return dict[key]

def groupBy(list, keyFun):
  dict = {}

  for elem in list:
    key = keyFun(elem)
    list = getOrUpdateDict(dict, key, [])
    list.append(elem)

  return dict
