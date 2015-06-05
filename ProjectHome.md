## Overview ##
A Python spin-off of Chris Gutteridge's Graphite library - http://graphite.ecs.soton.ac.uk/

The intent is to facilitate gathering exactly the data you want from wherever it happens to be and make it as easy to interrogate as possible. To this end there is a single class that contacts SPARQL endpoints and holds any other data you have, and lets you query it using rich wrapper classes - `graph.all_of_type('foaf:Person').sort('foaf:family_name').get('foaf:name')`

Most features are in place and working, but the project is still new so it may not always as efficient as it could be. More updates to follow soon.

In the long run it will be able to tap in to Jena's powerful inference and query capabilities to provide a tailored flexible tool for exploring what's possible with the semantic web.

### Contact ###
If you find a bug or it just fails please do let me know and I'll fix it.

Comments gratefully recieved at **python-graphite@rklyne.net**

I'm also on twitter as [@ronanklyne](https://twitter.com/ronanklyne)

## Getting started ##
### Installation ###
There is an easy [installation guide on the wiki](http://code.google.com/p/python-graphite/wiki/Installation).

### And off you go... ###

Once you're running you can do things like this:
```
>>> g = Graph()
>>> g.load("http://webscience.org/people")
<__main__.Graph object at 0x017F3A70>
>>> g.all_of_type('foaf:Person').sort('foaf:family_name').get('foaf:name').join(", ")
"Harold (Hal) Abelson, Hans Akkermans, Harith Alani, Tim Berners-Lee, Michael L. Brodie, Leslie Carr, Manuel Castells, Samantha Collins, Noshir Contractor, Richard Cyganiak, Susan Davies, David De Roure, Stefan Decker, Craig Gallen, Hugh Glaser, Jennifer  Golbeck, Christopher Gutteridge, Wendy Hall, James Hendler, Lalana Kagal, Joyce Lewis, Helen Margetts, Deborah L. McGuinness, Peter Monge, Sudarshan Murthy, Nichola Need, Kieron  O'Hara, Nigel Shadbolt, Steffen Staab, John Taylor, Brian Uzzi, Mark Weal, Daniel Weitzner, Bebo White, Jianping Wu, mc schraefel, Amy van der Hiel"
>>>
```

**You can do this with SPARQL too!**
```
>>> graph = Graph()
>>> graph.add_endpoint("http://linked4.org/lsd/sparql")
>>> rbwm = 'http://www.rbwm.gov.uk/id/authority/rbwm#id'
>>> print graph[rbwm]['rdfs:label']
Royal Borough of Windsor and Maidenhead
```

Easy, huh?

There is a wiki page with [full documentation](http://code.google.com/p/python-graphite/wiki/Documentation) but I'd recommend just playing around for a bit.

(Hopefully it will just start up and work, but if not there's a section of JPype/Java path related config in `config.ini` that might need tinkering with)

## Multiple data sources ##

All of this works just the same when you add multiple data sources!

Linked data is all about the linking. Interrogating multiple disparate sources at once is one of the main reasons I put this tool together. Try connecting up data from everyone who will provide it and see what you get :-)

This feature is still under development (the project is six days old) and won't be very clever or fast about using 10 or more SPARQL endpoints together, but it should work.

## Features ##

Done and working:
  * Jena backed data model in Python
  * Handy pythonic query syntax (see [run.py](http://code.google.com/p/python-graphite/source/browse/examples/run.py) for 'examples')
  * Add new triples: "graph.get('person:1').set('foaf:nick', 'Binky') # Add a nickname"
  * Run SPARQL queries over data in memory
  * Run SPARQL selects against remote endpoints.
  * Import into local graphs with SPARQL CONSTRUCT statements.
  * Config niceties done.
  * HTML output
  * ResourceList set functions
  * RDF output in something other than Turtle (maybe)
  * Automatically import data from SPARQL endpoints as you query. (It's primitive but it works!)
  * Read in from:
    * HTTP
    * String
      * TTL
      * N3
      * RDF/XML
    * File URI

## Futures ##
Some things that need doing:
  * More and better documentation.
  * Read in from RDFa
  * Delay SPARQL queries in some kind of continuation object.
    * This would make using SPARQL endpoints much more efficient.
  * Optimise

Some ideas of where to go next:
  * 'Live graphs' - Try to remove the dependency on big local datastores and increase our facility for bringing data in and forgetting it when we're done, as we do with the web today.
  * 'Magic SPARQLs' - given a list of endpoints, work out what they can each do and query the appropriate endpoints without being explicitly asked.

## Dependencies ##
**Requires [Python 2.6+](http://python.org/) and [JPype](http://sourceforge.net/projects/jpype/)**. You should go get these.

[Jena](http://jena.sourceforge.net/index.html) 2.6.4 has been included, but you can use your own copy quite easily - see `config.ini`.

JPype and Jena are both wonderful libraries without which I could not have built this tool.

I've tested this successfully on Linux and Windows 7 with Sun JVMs, but other systems ought to work.
