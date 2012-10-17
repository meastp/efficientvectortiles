import json

file_name = 'data.json'

ind = open(file_name)

data = json.load(ind)

ind.close()

output = { "results" : dict() }

for result in data :
  for key,value in result["results"].items() :
    if key in output["results"] :
      output["results"][key].extend(value)
    else :
      output["results"][key] = value


print output["results"].keys()

out = open(file_name+'.js', 'w')
json.dump(output, out, sort_keys=True, indent=2)
out.close()
