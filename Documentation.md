# **work in progress** #

# What it does #

This library lets you query all possible RDF data sources, aggregate them and query them. The query syntax is friendly and easy to aid you in exploring what the semantic web can do.



## Illustrative examples ##
Loading RDF over HTTP:

```
>>> import rdfgraph
>>> g = rdfgraph.Graph()
>>> g.load("http://webscience.org/people")
<__main__.Graph object at 0x017F3A70>
>>> g.all_of_type('foaf:Person').sort('foaf:family_name').get('foaf:name').join(", ")
"Harold (Hal) Abelson, Hans Akkermans, Harith Alani, Tim Berners-Lee, Michael L. Brodie, Leslie Carr, Manuel Castells, Samantha Collins, Noshir Contractor, Richard Cyganiak, Susan Davies, David De Roure, Stefan Decker, Craig Gallen, Hugh Glaser, Jennifer  Golbeck, Christopher Gutteridge, Wendy Hall, James Hendler, Lalana Kagal, Joyce Lewis, Helen Margetts, Deborah L. McGuinness, Peter Monge, Sudarshan Murthy, Nichola Need, Kieron  O'Hara, Nigel Shadbolt, Steffen Staab, John Taylor, Brian Uzzi, Mark Weal, Daniel Weitzner, Bebo White, Jianping Wu, mc schraefel, Amy van der Hiel"
>>>
```
This illustrates how the `ResourceList` object (returned by `all_of_type`) helps you manipulate sets of data easily.

Loading from SPARQL endpoints
```
>>> graph = Graph()
>>> graph.add_endpoint("http://linked4.org/lsd/sparql")
>>> rbwm = 'http://www.rbwm.gov.uk/id/authority/rbwm#id'
>>> print graph[rbwm]['rdfs:label']
Royal Borough of Windsor and Maidenhead
```
Note that you query in exactly the same way and don't have to write SPARQL. Just don't worry about how the querying happens :-)

# Graph class #
This class is your gateway into the semantic web. It's got a Jena backed data model to store data locally for processing and it can also maintain a list of remote data sources to progressively load data into the local graph as you query.

## Returned lists ##
Most returned lists are actually `ResourceList`s with lots of extra handy methods.

## Passing parameters ##
Most methods accept single items, parameter lists, tuples and `ResourceList`s - just try passing in whatever you have and it'll normally work.

## Getting data in ##

### add\_endpoint(uri) ###
Register a SPARQL endpoint for future automatic queries.

### import\_uri(uri) ###
Takes a single URI and loads from it directly into the graph, bypassing the web cache. It's rare that you'll want to do that...

### load(`<URIs>`) ###
Takes some URIs and loads RDF from each of them into the graph.

### String data loading functions ###
You can load RDF data from strings using the following functions:
  * load\_n3
  * load\_ntriple
  * load\_rdfxml
  * load\_turtle

### load\_sparql ###
Execute a SPARQL CONSTRUCT statement and incorporate the results into this graph.


### read\_sparql, sparql(query) ###
Execute a SPARQL SELECT and return a `SparqlList` iterator over the results.

This does NOT import triples into the local graph, as no triples are returned by a Sparql select.


## Query ##

### resource, get(uri) ###
Given a uri returns a Resource (`URIResource`) object that has a world of handy convenience methods for traversing, querying and updating your graph.

### has\_triple(subject, predicate, object) ###
Returns True if the given triple is present in the graph.

### triples(subject, predicate, object) ###
The main workhorse method. Returns iterators of triples that match the given pattern, where 'None' represents a wildcard.

### all\_of\_type(type) ###
A handy method for selecting resources based on their `rdf:type` property.

### all\_types() ###
Returns a list of all distinct `rdf:type`s.

## Other ##
### dump() ###
Render as HTML.

### expand\_uri(uri) ###
Convert a short form URI into a full one.

### add\_namespaces, add\_ns(prefix, uri) ###
Add a prefix and URI to the graph's record of shortform URI prefixes.

### prefixes/namespaces() ###
Returns a dictionary of all URI namespace prefixes.

### set\_triple(subject, predicate, object) ###
Usually this would be done through Resource objects (see `get(uri)`) but if you need it, then it's here.

### shrink\_uri(uri) ###
Convert a full URI into a prefixed one, if possible.

### to\_string(format='turtle') ###
Return an RDF rendering of this graph.



# Resource functions #
## Properties ##
### all(property) ###
Iterate over all the values of the given property.

### get(property) ###
Return the (arbitrarily first) value of this property. Useful when you know there's only one value.

### has(property) ###
Test if the given property exists.

### set(property, value) ###
Update the graph, adding a triple with this resource as the subject and the two given resources as the predicate and the object.

### properties() ###
Iterate over the distinct properties of this resource.

### property\_values() ###
Iterate over the properties of this resource and their values.

### inverse\_properties() ###
Iterate over all distinct inverse properties (where this resource is the object).

### inverse\_property\_values() ###
Iterate over all inverse properties and their values.

## Other ##
### dump() ###
Render as HTML.

### load() ###
Load RDF data from this resource's URI.

### load\_same\_as() ###
Look up the URIs of everything that is 'owl:sameAs' this resource and load RDF from them.

Also available through item assignment:
```
resource[property] = value
```

### short\_html() ###
Return a short HTML description of this resource, not including any arbitrary properties.

### shrink\_uri() ###
Return the short form of this resource's URI.

### to\_string ###
Export this resource as RDF.

### type() ###
Look up the 'rdf:type' of this resource.




# ResourceList functions #

### get(property) ###
For each resource, get this property, returning a further list.

### sort(property) ###
Sort the list by this property. Involves loading the whole list - beware.

### all(property) ###
For each resource, get all the values of this property, concatenation those lists.

### join(separator) ###
Call to\_string() on each resource then join them with this separator.

### union(other) ###
Returns the union of this resource with another.

### intersection(other) ###
Returns the intersection of this resource and another.