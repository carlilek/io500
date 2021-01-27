#!/usr/bin/env python
import sys
import json
import re

# This tool allows to view and edit the options in an existing schema file.
# In order to get started download the two files:
# wget https://www.vi4io.org/lib/plugins/newcdcl/scripts/schema-io500.json
# wget https://www.vi4io.org/lib/plugins/newcdcl/scripts/site-io500.json
#
# You can then copy the site-io500.json template file and modify it using this tool

if len(sys.argv) < 3:
  print("synopsis: %s <FILE> {<TOKEN[=VALUE [UNIT]]>}" % sys.argv[0])
  print("examples:")
  print("printing current: %s site.json Site.institution" % sys.argv[0])
  print("Token examples:")
  print("changing: Site.StorageSystem.Lustre.OSS.count=5")
  print("changing options: Site.StorageSystem.Lustre.features=DNE1;DNE2")
  print("changing a numeric value \"Site.IO500.IOR.easy write = 351.2 GiB/s\"")
  print("setting a value for a second Lustre (for multiple schemes): Site.StorageSystem.Lustre[1].OSS.count=5")
  sys.exit(1)

file = sys.argv[1]
schemafile = "schema-io500.json"
value = None # currently parsed value

def parse_full_val(val, schema_data):
  global units
  tmp = val
  if "unit" in schema_data and schema_data["unit"] != "":
    tmp = val.split(" ")
    if schema_data["dtype"] == "number":
      number = float(tmp[0])
    elif schema_data["dtype"] == "integer":
      number = int(tmp[0])
    else:
      return None
    if len(tmp) != 2:
      print("The value %s requires a unit of type: %s" % (val, schema_data["unit"]))
      return None
    val_unit = tmp[1].strip()
    exp_unit = units[schema_data["unit"]]
    for (unit, multiplier) in exp_unit:
      if val_unit == unit:
        return [ number, val_unit ]
    return None

  if schema_data["dtype"] == "number":
    return float(tmp[0])
  elif schema_data["dtype"] == "integer":
    return int(tmp[0])
  else:
    return val

def processDict(data, token, path, val):
  global value
  cur = token[0].strip()

  if len(token) == 1:
    was = ""
    if cur in data["att"]:
      cval = data["att"][cur]
      if isinstance(cval, list):
        cval = "%s %s" % (cval[0], cval[1])
      if val != None:
        was = "   # was: %s" % cval

    if val != None:
      data["att"][cur] = val

    if cur in data["att"]:
      cval = val
      if isinstance(val, list):
        cval = "%s %s" % (val[0], val[1])
      print("%s = %s%s" % (path, cval, was))
    else:
      print("%s = undefined" % path)
  else:
    processSingle(data["childs"], token, path, val)

def processSingle(data, token, path, val):
  cur = token.pop(0)
  index = 0
  m = re.search("(.*)\[([0-9]+)\]", cur)
  if m:
    cur = m.group(1)
    index = int(m.group(2))

  if isinstance(data, list):
    # need to find token
    for k in range(0, len(data)):
      if data[k]["type"] == cur:
        if index == 0:
          processDict(data[k], token, path, val)
          return
        else:
          index = index - 1
    for k in range(0, index + 1):
      data.append({"type" : cur, "att" : {}, "childs" : [] })
    processDict(data[len(data)-1], token, path, val)
    return
  if data["type"] == cur:
    processDict(data, token, path, val)

def validate_in_template(templateNames, cur, token, val, multi = False):
  global templates
  index = 0
  m = re.search("(.*)(\[[0-9]+\])", cur)
  if m:
    cur = m.group(1)
    index = m.group(2)

  for t in templateNames:
    name = t
    if t.find(":") > -1: # a renamed type
      name = t.split(":")[0]
      t = t.split(":")[1]
    if name == cur: # found it
      if index > 0 and not multi:
        print("The template %s does not support [X] notation" % cur)
        return None
      return validate_path_value(templates[t], token, val)
  return None

# Check if the schema supports the provided path token Site.XXX.YYY.ZZZ
def validate_path_value(schema, token, val):
  global value
  cur = token.pop(0).strip()
  if cur in schema:
    if len(token) == 0:
      # Validate the correctness of the value
      if val:
        schema = schema[cur]
        value = parse_full_val(val, schema)
        return value != None
      return True;
    else:
      return validate_path_value(schema[cur], token, val)
  if "SCHEMES" in schema:
    ret = validate_in_template(schema["SCHEMES"], cur, token, val)
    if ret != None:
      return ret
  if "SCHEMES_multi" in schema:
    ret = validate_in_template(schema["SCHEMES_multi"], cur, token, val, multi = True)
    if ret != None:
      return ret
  return False

def process(data, schema, tokens):
  global value
  for t in tokens:
    kv = t.split("=")
    token = kv[0].split(".")
    val = kv[1].strip() if len(kv) == 2 else None
    value = None
    if validate_path_value(schema, list(token), val):
      processSingle(data, token, kv[0].strip(), value)
    else:
      print("Error: cannot validate path (or value): %s" % token)

with open(schemafile, 'r') as f:
  schema = json.load(f)
  templates = schema["SCHEMES"]
  units = schema["UNITS"]

with open(file, 'r+') as f:
    data = json.load(f)
    process(data["DATA"], schema["SYSTEM"], sys.argv[2:])

    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()


print("OK")
