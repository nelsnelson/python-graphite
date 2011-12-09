""" A hackers RDF query and manipulation tool.
Ripped off from Chris Gutteridge's Graphite: http://graphite.ecs.soton.ac.uk/
"""

# CONFIG! (finally)

class Config(object):
    def __init__(self):
        import os
        base_dir = os.path.dirname(__file__)
        import ConfigParser
        cp = ConfigParser.SafeConfigParser(defaults={
            'jena_libs': 'jena\\libs',
            'jvm_lib': None,
        })
        cp.read([
            'config.ini',
        ])

        libs_cfg = cp.get('config', 'jena_libs')
        if libs_cfg:
            self.jena_libs = os.path.join(base_dir, libs_cfg)
        self.jena_libs = os.path.abspath(self.jena_libs)
        self.jena_libs += '\\'

        jvm_cfg = cp.get('config', 'jvm_lib')
        if jvm_cfg:
            # Have a good guess with relative paths - probably JAVA_HOME relative
            java_base_dir = os.environ['JAVA_HOME'] or base_dir
            self.jvm_file = os.path.join(java_base_dir, jvm_cfg)
            self.jvm_file = os.path.abspath(self.jvm_file)
        else:
            self.jvm_file = None # Guess later

Config = Config()

# Some constants
DEFAULT_NAMESPACES = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
}

def takes_list(f):
    def parse_list(self, tpl):
        for item in tpl:
            if getattr(item, 'isResourceList', False) or isinstance(item, list):
                 for resource in item:
                    yield resource
            elif getattr(item, 'isResource', False):
                yield item
            elif isinstance(item, (str, unicode)):
                # Assume it's a URI. Maybe add some literal support later.
                yield URIResource(self, item)
            else:
                yield item

    def g(self, *t, **k):
        l = parse_list(self, t)
        return f(self, l, **k)
    return g
class SimpleGraph(object):
    "Represents an RDF graph."
    def __init__(self, uri=None, namespaces=None, engine=None):
        if not engine:
            engine = self.create_default_engine()
        self.engine = engine
        self.graph = None
        # A log of which URIs have been loaded already, for efficiency
        self.loaded = {}
        if uri:
            self.load(uri)
        self.add_ns(DEFAULT_NAMESPACES)
        if namespaces:
            self.add_ns(namespaces)

    def create_default_engine(self):
        return JenaEngine()

    @takes_list
    def load(self, lst, **k):
        reload = k.get('reload', False)
        assert lst, "Load what?"
        for datum in lst:
            assert getattr(datum, 'isURIResource', False), "Can't load " +`datum`
            if not reload and datum.uri in self.loaded: continue
            self.loaded[datum.uri] = True
            self.engine.load_uri(datum.uri)
        return self

    def read_sparql(self, endpoint, query):
        "Make a SPARQL SELECT and traverse the results"
        return SparqlList(self._parse_sparql_result(
            self.engine.load_sparql(endpoint, query)
        ))

    def load_sparql(self, endpoint, query):
        "Load data into memory from a SPARQL CONSTRUCT"
        self.engine.import_sparql(endpoint, query)
        return self

    def _parse_uri(self, data):
        if isinstance(data, Resource):
            return data.uri
        if not isinstance(data, (str, unicode)):
            return None
        return self._expand_uri(data)

    def _expand_uri(self, uri):
        import urlparse
        tpl = urlparse.urlparse(uri)
        if tpl[0] and tpl[2] and len(filter(None, tpl)) == 2:
            # "dc:title"-ish
            return self.engine.expand_uri(uri)
        return uri
    expand_uri = _expand_uri

    def shrink_uri(self, uri):
        return self.engine.shrink_uri(uri)

    def _parse_subject(self, sub):
        attempt = self._parse_uri(sub)
        if attempt is not None:
            return URIResource(self, attempt)
        return sub

    def _parse_object(self, obj):
        attempt = self._parse_uri(obj)
        if attempt is not None:
            return URIResource(self, attempt)
        if callable(getattr(obj, 'value', None)):
            return obj.value()
        return obj

    def _parse_property(self, prop):
        attempt = self._parse_uri(prop)
        if attempt is not None:
            return attempt
        return prop

    def _format_as_html(self, data):
        # XXX: Not Implemented !!!
        return data

    def dump(self):
        return self._format_as_html(
            self.engine.dump()
        )

    def dump_resources(self, res, extended=False):
        return self._format_as_html(
            self.engine.dump_resources(res, extended=extended)
        )

    def has_triple(self, *t):
        "Returns True if triples(*t) would return any triples."
        for x in self.triples(*t):
            return True
        return False

    def triples(self, *t):
        return ResourceList(self._triples(*t))
    def _triples(self, x, y, z):
        triple_iter = self.engine.triples(
            self._parse_subject(x),
            self._parse_property(y),
            self._parse_object(z),
        )
        for sub, pred, ob in triple_iter:
            if getattr(ob, 'is_uri', False):
                ob = URIResource(self, ob)
            else:
                ob = Resource(self, ob)
            sub = URIResource(self, sub)
            yield sub, pred, ob

    def sparql(self, query_text):
        return SparqlList(self._parse_sparql_result(self.engine.sparql(query_text)))

    def _parse_sparql_result(self, result_obj):
        for result in result_obj:
            output = {}
            for k, v in result.items():
                if getattr(v, 'is_uri', False):
                    v = URIResource(self, v)
                else:
                    v = Resource(self, v)
                output[k] = v
            yield output

    def resource(self, uri):
        return URIResource(self, uri)
    get = resource
    __getitem__ = resource

    @takes_list
    def all_of_type(self, types):
        return ResourceList(self._all_of_type(types))
    def _all_of_type(self, types):
        for type in types:
            for x, y, z in self.triples(None, 'rdf:type', URIResource(self, type)):
                yield x

    def add_ns(self, *t, **k):
        return self.add_namespaces(*t, **k)

    def add_namespaces(self, namespaces):
        for prefix, uri in namespaces.items():
            self.engine.add_namespace(prefix, uri)

class SparqlStats(object):
    "Stores stats on endpoint for deciding whether to send it a particular query."
    def __init__(self, uri, graph):
        self.uri = uri
        self.graph = graph

class SparqlGraph(SimpleGraph):
    "And I shall call this module... Magic Spaqrls!"
    def __init__(self, uri=None, namespaces=None, engine=None):
        super(SparqlGraph, self).__init__(uri=None, namespaces=None, engine=None)

    @takes_list
    def add_endpoint(self, endpoints):
        for resource in endpoints:
            uri = resource.uri
            self.endpoints[uri] = SparqlStats(uri, self)

class Graph(SimpleGraph): pass

# When SparqlGraph is good, make it the default.
# class Graph(SparqlGraph): pass


class Reiterable(object):
    def __init__(self, iterable):
        self.iterable = iterable
        self.iter_history = []

    def __iter__(self):
        i = 0
        while i < len(self.iter_history):
            yield self.iter_history[i]
            i += 1
        if self.iterable:
            for x in self.iterable:
                self.iter_history.append(x)
                yield x
            self.iterable = None

class SparqlList(Reiterable):
    def _get(self, var):
        for dct in self:
            yield dct[var]
    def get(self, var):
        return ResourceList(self._get(var))
    __getitem__ = get

class ResourceList(Reiterable):
    isResourceList = True

    def map(self, name, *t, **k):
        result = []
        for r in self:
            result.append(getattr(r, name)(*t, **k))
        return result
    def map_concat(self, name, *t, **k):
        result = []
        for l in self.map(name, *t, **k):
            result.extend(l)
        return result

    def all(self, prop):
        return ResourceList(self.map_concat('all', prop))

    def has(self, prop):
        for b in self.map('has', prop):
            if b:
                return True
        return False

    def get(self, prop):
        return ResourceList(self.map('get', prop))
    __getitem__ = get

    def load_same_as(self):
        self.map('load_same_as')
        return self

    def sort(self, prop):
        lst = []
        for x in self:
            key = x.get(prop)
            lst.append((key, x))
        lst.sort()
        return ResourceList([y for x, y in lst])

    def join(self, sep=''):
        return sep.join(map(str, self))


class Resource(object):
    isResource = True

    def __init__(self, graph, datum):
        self.graph = graph
        self.datum = datum

    def _all_resources(self):
        return [self]

    def __eq__(self, other):
        if not isinstance(other, Resource):
            return False
        return self.datum == other.datum

    def __str__(self):
        return unicode(self.datum)
    def __repr__(self):
        return "Resource(" + repr(self.datum) + ")"
    def __cmp__(self, other):
        return cmp(self.datum, other.datum)

    def value(self):
        return self.datum

    def as_uri(self):
        return URIResource(self.graph, self.datum)

class URI(str):
    """Used to label some strings as known URIs, so that they may be
    distinguished from literals"""
    is_uri = True

class URIResource(Resource):
    isURIResource = True
    def __init__(self, graph, uri):
        self.graph = graph
        if isinstance(uri, URIResource):
            uri = uri.uri
        assert isinstance(uri, (str, unicode)), uri
        uri = graph._expand_uri(uri)
        self.uri = uri
        self.same_as_resources = []

    def __eq__(self, other):
        if not isinstance(other, URIResource):
            return False
        return self.uri == other.uri

    def __str__(self):
        return "<"+str(self.uri)+">"
    def __repr__(self):
        return "URIResource(" + self.uri + ")"

    def _all_resources(self):
        return [self] + self.same_as_resources

    def properties(self):
        for y, z in self.property_values():
            yield y

    def property_values(self):
        for res in self._all_resources():
            for x, y, z in self.graph.triples(res, None, None):
                yield y, z

    def get(self, prop):
        "Get a property"
        for x in self.all(prop):
            return x
        return None
    __getitem__ = get

    def type(self):
        return self['rdf:type']

    def _parse_prop(self, prop):
        invert = False
        assert isinstance(prop, (str, unicode))
        if prop[0] == '-':
            invert, prop = True, prop[1:]
        prop = self.graph._parse_property(prop)
        return prop, invert

    def all(self, prop):
        "Get a list of properties"
        prop, invert = self._parse_prop(prop)
        if invert:
            for x, y, z in self.graph.triples(None, prop, self):
                yield z
        else:
            for x, y, z in self.graph.triples(self, prop, None):
                yield z

    def has(self, prop):
        "Returns True iff the resource has a value for this property"
        prop, invert = self._parse_prop(prop)
        if invert:
            return self.graph.has_triple(None, prop, self)
        else:
            return self.graph.has_triple(self, prop, None)

    def load_same_as(self):
        for other in self.all('owl:sameAs'):
            other = URIResource(self.graph, other)
            if other not in self.same_as_resources:
                self.same_as_resources.append(other)
            self.graph.load(other.uri)
        return self

    def to_string(self, extended=True):
        s = ''
        for prop, value in self.property_values():
            s += "<span style='font-size:130%%'>&larr;</span> is <a title='%s' href='%s' style='text-decoration:none;color: green'>%s</a> of <span style='font-size:130%%'>&larr;</span> %s\n" % (
                prop,
                prop,
                self.graph.shrink_uri(prop),
                value,
            )
        return self.graph.dump_resources(self._all_resources(), extended=extended)
    dump = to_string

    def as_uri(self):
        return self

class Engine(object):
    """Defines an interface for an RDF triple store and query engine.
    """
    def sparql(self, query_text):
        raise NotImplemented, "SPARQL querying not supported by this engine"

    def triples(self, subject, predicate, object):
        raise NotImplemented, "Select triples from the store"

    def load_uri(self, uri):
        raise NotImplemented, "Load RDF from a URI into the store"

    def expand_uri(self, uri):
        raise NotImplementedError, "Expand a URI's shorthand prefix"

    def add_namespace(self, prefix, uri):
        raise NotImplementedError, "Register a namespace and it's prefix"


from jpype import startJVM, shutdownJVM, ByteArrayCustomizer, \
  CharArrayCustomizer, ConversionConfig, ConversionConfigClass, JArray, \
  JBoolean, JByte, JChar, JClass, JClassUtil, JDouble, JException, \
  JFloat, JInt, JIterator, JLong, JObject, JPackage, JProxy, JString, \
  JavaException
_jvm_running = False
def runJVM():
    global _jvm_running
    if _jvm_running:
        return
    jvm_args = []
    import os

    if os.name == 'nt':
        cp_sep = ';'
    else:
        cp_sep = ':'

    java_classpath = [
        Config.jena_libs+'jena-2.6.4.jar',
        Config.jena_libs+'log4j-1.2.13.jar',
        Config.jena_libs+'arq-2.8.7.jar',
        Config.jena_libs+'slf4j-api-1.5.8.jar',
        Config.jena_libs+'slf4j-log4j12-1.5.8.jar',
        Config.jena_libs+'xercesImpl-2.7.1.jar',
        Config.jena_libs+'iri-0.8.jar',
        Config.jena_libs+'icu4j-3.4.4.jar',
    ]
    jvm_file = Config.jvm_file
    if not jvm_file:
        if os.name == 'nt':
            jvm_file = os.path.join(os.environ['JAVA_HOME'], 'bin','client','jvm.dll')
        else:
            jvm_file = os.path.join(os.environ['JAVA_HOME'], 'jre', 'lib', 'amd64', 'server', 'libjvm.so')

    if java_classpath:
        jvm_args.append("-Djava.class.path=" + cp_sep.join(
            map(os.path.abspath, java_classpath))
        )


    startJVM(jvm_file, *jvm_args)
    _jvm_running = True

class JenaEngine(Engine):
    _jena_pkg_name = 'com.hp.hpl.jena'

    def __init__(self, debug=False):
        if debug:
            if callable(debug):
                self.debug = debug
            else:
                def debug(x):
                    print x
                self.debug = debug
        runJVM()
        self.jena_model = None
        self.get_model()

    def debug(self, msg): pass

    def get_model(self):
        if not self.jena_model:
            klass = JClass(self._jena_pkg_name+'.rdf.model.ModelFactory')
            self.jena_model = klass.createDefaultModel()
        return self.jena_model

    def _new_submodel(self):
        model = JClass('com.hp.hpl.jena.rdf.model.ModelFactory').createDefaultModel()
        model = model.setNsPrefixes(self.jena_model.getNsPrefixMap())
        return model

    def expand_uri(self, uri):
        return str(self.get_model().expandPrefix(JString(uri)))

    def shrink_uri(self, uri):
        return str(self.get_model().shortForm(JString(uri)))

    def _mk_resource(self, uri):
        "Make this Subject thing suitable to pass to Jena"
        if uri is None:
            return JObject(None,
                JPackage(self._jena_pkg_name).rdf.model.Resource,
            )
        if isinstance(uri, URIResource):
            uri = uri.uri
        assert isinstance(uri, (unicode, str)), (uri, type(uri))
        return JObject(
            self.get_model().createResource(JString(uri)),
            JPackage(self._jena_pkg_name).rdf.model.Resource,
        )

    def _mk_property(self, uri):
        "Make this Property thing suitable to pass to Jena"
        if uri is None:
            return JObject(None,
                JPackage(self._jena_pkg_name).rdf.model.Property,
            )
        if isinstance(uri, URIResource):
            uri = uri.uri
        assert isinstance(uri, (unicode, str)), (uri, type(uri))
        return JObject(
            self.get_model().createProperty(JString(uri)),
            JPackage(self._jena_pkg_name).rdf.model.Property,
        )

    def _mk_object(self, obj):
        "Make this Object thing suitable to pass to Jena"
        if obj is None:
            return JObject(
                None,
                JPackage(self._jena_pkg_name).rdf.model.RDFNode,
            )
        if isinstance(obj, URIResource):
            return JObject(
                self.get_model().createResource(obj.uri),
                JPackage(self._jena_pkg_name).rdf.model.RDFNode,
            )
        else:
            return JObject(
                self.get_model().createLiteral(obj),
                JPackage(self._jena_pkg_name).rdf.model.RDFNode,
            )

    def as_node(self, obj):
        return JObject(
            self.get_model().createResource(obj.uri),
            JPackage(self._jena_pkg_name).rdf.model.RDFNode,
        )

    def load_uri(self, uri):
        self.debug("JENA load "+uri)
        jena = self.get_model()
        jena = jena.read(uri)
        self.jena_model = jena

    def _iter_sparql_results(self, qexec):
        try:
            jresults = qexec.execSelect() # ResultsSet
            while jresults.hasNext():
                result = {}
                soln = jresults.nextSolution() # QuerySolution
                for name in soln.varNames():
                    try:
                        v = soln.getResource(name)   # Resource // Get a result variable - must be a resource
                        if v:
                            v = URI(v.getURI())
                    except:
                        v = soln.getLiteral(name)    # Literal  // Get a result variable - must be a literal
                        v = v.getValue()
                    result[name] = v
                yield result
        finally:
            qexec.close()

    def load_sparql(self, endpoint, query):
        q_pkg = JPackage("com.hp.hpl.jena.query")
        qexec = q_pkg.QueryExecutionFactory.sparqlService(JString(endpoint), JString(query))
        return self._iter_sparql_results(qexec)

    def has_triple(self, x, y, z):
        self.debug(' '.join(["JENA has_triple ", `x`, `y`, `z`]))
        jena = self.get_model()
        sub = self._mk_resource(x)
        pred = self._mk_property(y)
        ob = self._mk_object(z)
        return bool(jena.contains())

    def triples(self, x, y, z):
        self.debug(' '.join(["JENA triples ", `x`, `y`, `z`]))
        jena = self.get_model()
        sub = self._mk_resource(x)
        pred = self._mk_property(y)
        ob = self._mk_object(z)

        for stmt in jena.listStatements(
            sub,
            pred,
            ob,
        ):
            st = stmt.getSubject()
            a = st.getURI()
            b = stmt.getPredicate().getURI()
            c = stmt.getObject()
            if c.isResource():
                c = URI(c.getURI())
            else:
                c = c.getValue()
            yield a, b, c

    def _dump_model(self, model, format="TTL"):
        out = JPackage('java').io.StringWriter()
        model.write(out, format)
        return unicode.encode(out.toString(), 'utf-8')

    def dump_resources(self, resources, format="TTL", extended=False):
        model = self._new_submodel()
        for res in resources:
            model.add(self.get_model().listStatements(
                self._mk_resource(res),
                self._mk_property(None),
                self._mk_object(None),
            ))
            if extended:
                model.add(self.get_model().listStatements(
                    self._mk_resource(None),
                    self._mk_property(None),
                    self._mk_object(res),
                ))
        return self._dump_model(model)

    def to_string(self, format="TTL"):
        return self._dump_model(self.get_model(), format)
        return unicode.encode(out.toString(), 'utf-8')

    def dump(self, *t, **k):
        return self.to_string(*t, **k)

    def add_namespace(self, prefix, uri):
        self.get_model().setNsPrefix(prefix, uri)

    def sparql(self, query_text):
        q_pkg = JPackage("com.hp.hpl.jena.query")
        model = self.get_model()
        query = q_pkg.QueryFactory.create(query_text)
        qexec = q_pkg.QueryExecutionFactory.create(query, model)
        return self._iter_sparql_results(qexec)
