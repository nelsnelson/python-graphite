# Prerequisites #

This library depends on Python 2.6 or greater and [JPype](http://sourceforge.net/projects/jpype/).

# Installing JPype #

## Windows ##
  * [Download the installer](http://sourceforge.net/projects/jpype/files/JPype/0.5.4/) that matches your Python version.
  * Run it and follow the instructions.

## Linux/Mac ##
  * [Download the ZIP](http://sourceforge.net/projects/jpype/files/JPype/0.5.4/) package of JPype.
  * Extract the contents somewhere and then open a command prompt there.
  * As root, run `python setup.py install`.

# Installing python-graphite #

  * First download the latest ZIP package in the [downloads area](http://code.google.com/p/python-graphite/downloads/list).
  * Extract the contents somewhere and then open a command prompt there.
  * As root/administrator, run `python setup.py install`.


## Testing the installation ##
Run this:
```
~# python
>>> import graphite
>>> graph = graphite.Graph()
>>>
```

If you don't get a traceback, it worked! If it fails, do let me know what the error message is and I'll do my best to help.