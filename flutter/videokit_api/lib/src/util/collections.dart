/// Collection helpers shared by the immutable data classes.
library;

/// Returns an unmodifiable copy of [source].
List<T> frozenList<T>(Iterable<T> source) => List<T>.unmodifiable(source);

/// Returns an unmodifiable copy of [source].
Map<K, V> frozenMap<K, V>(Map<K, V> source) => Map<K, V>.unmodifiable(source);

/// Returns an unmodifiable copy of [source].
Set<T> frozenSet<T>(Iterable<T> source) => Set<T>.unmodifiable(source);

/// Order-sensitive hash of a list.
int hashList(List<Object?> list) => Object.hashAll(list);

/// Order-insensitive hash of a map.
int hashMap(Map<Object?, Object?> map) => Object.hashAllUnordered(
  map.entries.map((e) => Object.hash(e.key, e.value)),
);

/// Order-insensitive hash of a set.
int hashSet(Set<Object?> set) => Object.hashAllUnordered(set);
