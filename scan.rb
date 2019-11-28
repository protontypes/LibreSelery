#!/usr/bin/env ruby

require 'bibliothecary'

deps = Bibliothecary.analyse('./')
puts deps
