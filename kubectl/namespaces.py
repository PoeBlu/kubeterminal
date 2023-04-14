
from .cmd import getNamespaces

def list():
    '''Return list of tuples of namespaces: [(value,label),(value,label),...]'''
    namespaces = [("all-namespaces","All namespaces")]
    allNamespaces =  getNamespaces()

    namespaces.extend((ns, ns) for ns in allNamespaces)
    return namespaces