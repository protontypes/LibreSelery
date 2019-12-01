#!/usr/bin/env ruby

require 'bibliothecary'
require 'json'

deps = Bibliothecary.analyse('./')

# convert dict array to json
json_deps = deps.to_json

#puts json_deps

# Save dependencies into json file
File.open("dependencies.json","w") do |f|
    f.write(json_deps)
end