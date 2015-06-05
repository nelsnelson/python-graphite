# Classes #

These are the major concepts dealt with.

## Graph ##

An independent object that represents a local RDF graph maintained in Jena.

(Some of these method renames have not been implemented yet.)

Methods:
  * Input
    * `read_text` - guess content type
      * `read_turtle`
      * `read_n3`
      * `read_ntriples`
      * `read_rdfxml`
    * `read_uri` - load data from URI
    * `read_file` - save to a file
  * Output
    * `save_text` - content type param
      * `save_turtle`
      * `save_n3`
      * `save_ntriples`
      * `save_rdfxml`
    * `save_file` - save to a file
  * Query
    * ... all the signature bits but no sparql
    * `resource`/`get`/`graph[uri]` - get a URI Resource
    * `literal` - get a Literal Resource
    * `sparql(query)` - Run a sparql select over this graph.
    * `triples(x, y, z)` - Select statements from the graph.
  * Update
    * `add_triple(x, y, z)`
    * `remove_triple(x, y, z)`

## Endpoint ##
Represents a standalone endpoint and handles caching, querying, etc.

**More work is required here. The class is still largely bare.**

  * select
  * construct
  * describe
  * ask

  * Pending structure changes:
    * This class should:
      * handle automatically fetching triples when requested.
      * be responsible for maintaining a disk based graph that caches those triples.
      * be responsible for maintaining efficiency of access to this endpoint.
      * (all of these responsibilities currently rest with a Dataset)


## Dataset ##
Represents a number of data sources, both sparql endpoints and local graphs.

Method groups:
  * Endpoints:
    * add/remove/list
  * Graphs:
    * Add/remove/list
  * Query - provide a combined query system returning iterator based data in suitable wrapper classes
    * Sparql
    * Triple query
    * Native python query


## Resource ##
Represents a Node (literal, uri or blank) and provides handy query methods. _This is the main workhorse_.

Methods:
  * Data
    * Get literal as native datatype
    * get URI
    * `__nonzero__` method for blank nodes (`if node: node['some:thing']`)
  * Traversal
    * `get(property)` - get the Resource linked to by this property.
    * `all(property)` - get all Resources linked to by this property.
    * `has(property)` - check if the Resource has this property.
  * Update:
    * `node['foaf:nick'] = 'Binky'` or `node.set('foaf:nick', 'Binky')` to replace an existing relation.
    * `node.add('foaf:nick', 'Binky')` to replace an existing relation.
  * Interrogate - list properties, etc.
    * `properties()` - Iterate over all properties of this resource.
    * `property_values()` - Iterate over all properties of this resource and their related values.
  * Utility
    * `shrink_uri()`/`expand_uri()`
    * `is_uri()`/`is_literal()`/`is_blank()`
    * `uri()` - return the URI of this resource.
    * `value()` - return the literal value of this resource.
    * `type()` - return the 'rdf:type' of this resource.
    * `load_same_as()` - load all resources that are 'owl:sameAs' this one.
    * `load()` - Load RDF data form this Resource's URI.
    * `get_ns()` - return the namespace URI form this Resource
    * `in_ns(ns)` - check if the resource is in this namespace.

## ResourceList ##
Represents an iterator based list of resources.

Method groups:
  * Set functions - combine/intersect `ResourceList`s
  * Query - Handy Resource functions mapped across all list items

## Internal ##
  * Node - raw engine (Jena) output in Python datatypes.
    * Resource - A URI node.
    * Blank - just hold the Jena ID object
    * Literal - parsed and tagged
  * Heavy testing on the unicode I/O to Jena through JPype.