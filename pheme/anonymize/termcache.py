import argparse
import shelve
import sys

from pheme.util.config import Config


class TermCache(object):
    """Persistent cache of terms and their anonymized values

    Interface to lookup a value (presumably anonymized) from
    any existing term, so set a term's anonymized value, and persist
    the entire store to the filesystem.

    """
    def __init__(self):
        cachefile = Config().get('anonymize', 'cachefile')
        self.shelf = shelve.open(cachefile, writeback=True)

    def _convert_key(self, key):
        if isinstance(key, str):
            return key
        return str(key)

    def __contains__(self, key):
        return self.shelf.__contains__(self._convert_key(key))

    def __getitem__(self, key):
        if self._convert_key(key) in self.shelf:
            return self.shelf[self._convert_key(key)]
        return None

    def __setitem__(self, key, value):
        self.shelf[self._convert_key(key)] = value

    def __delitem__(self, key):
        del self.shelf[self._convert_key(key)]


tc = TermCache()  # module level singleton


def lookup_term(term):
    """lookup term - return if found, None otherwise"""
    return tc[term]


def store_term(term, value):
    """set term to value in cache"""
    tc[term] = value


def delete_term(term):
    """delete term from cache"""
    del tc[term]


def lookup_term_ep():
    """entry point to lookup arbitrary term from persistent cache"""
    parser = argparse.ArgumentParser()
    parser.add_argument("term", help="lookup 'term' in termcache")
    args = parser.parse_args()
    result = lookup_term(args.term)
    if result is not None:
        print "%s:%s" % (args.term, result)
        return
    else:
        print sys.stderr, "Not Found: '%s'" % args.term
        sys.exit(1)


def store_term_ep():
    """entry point to store arbitrary term from persistent cache"""
    parser = argparse.ArgumentParser()
    parser.add_argument("term", help="the 'term' to set in termcache")
    parser.add_argument("value", help="set 'value' for 'term'")
    parser.add_argument("-o", "--overwrite", action='store_true',
                        help="overwrite existing values if set")
    args = parser.parse_args()

    if not args.overwrite and lookup_term(args.term) is not None:
        raise ValueError("term '%s' already assigned, "
                         "overwrite flag not set" % args.term)
    store_term(args.term, args.value)
    print "Cached %s:%s" % (args.term, args.value)
    return