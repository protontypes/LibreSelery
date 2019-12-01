#!/usr/bin/env ruby

require 'bibliothecary'

deps = Bibliothecary.analyse('./')
puts deps.class
puts deps[0].class
