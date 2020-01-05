require 'bibliothecary'
require 'json'
require 'optparse'
project_root = ''
options = {}
OptionParser.new do |parser|
  parser.on("-p", "--project LIBRARY",
            "Project root folder to scan for manifesto files recursaivly") do |lib|
    project_root = lib
  end
end.parse!
deps = Bibliothecary.analyse(project_root)

# convert dict array to json
json_deps = deps.to_json

puts json_deps
