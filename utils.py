def memoize(f):
    """Return a function like f but caching its results. Its arguments
    must be hashable."""
    def memoized(*args):
        try: return memoized._memos[args]
        except KeyError:
            result = memoized._memos[args] = f(*args)
            return result
    memoized._memos = {}
    return memoized
