import 'package:flutter/foundation.dart';

import '../media/video_size.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Resource class requested from the budget (07 §2).
enum ResourceKind {
  videoDecoder,
  imageMemory,
  trackingWorker,
  exportWorker,
  encoder;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [videoDecoder].
  static ResourceKind fromName(String? name) =>
      enumFromName(values, name, videoDecoder);
}

/// Priority of a resource request (07 §2); higher first.
///
/// Named `ResourcePriority` (Kotlin: `Priority`) to avoid clashing with
/// Flutter's scheduler `Priority`.
enum ResourcePriority {
  visibleAudible,
  visible,
  offscreen,
  optional;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [optional].
  static ResourcePriority fromName(String? name) =>
      enumFromName(values, name, optional);
}

/// Suggested degradation when a reservation is denied (07 §3).
enum DegradeSuggestion {
  reduceActiveVideos,
  pauseOffscreen,
  showStaticPlaceholder,
  lowerResolution,
  none;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [none].
  static DegradeSuggestion fromName(String? name) =>
      enumFromName(values, name, none);
}

/// Estimated cost of a request (07 §2).
@immutable
final class ResourceEstimate {
  /// Creates an estimate.
  const ResourceEstimate({
    this.resolution,
    this.frameRate,
    this.codec,
    this.hardware,
    this.bytes,
  });

  /// Resolution.
  final VideoSize? resolution;

  /// Frame rate.
  final int? frameRate;

  /// Codec MIME type.
  final String? codec;

  /// Hardware decoding.
  final bool? hardware;

  /// Memory bytes.
  final int? bytes;

  /// Returns a copy with the given fields replaced.
  ResourceEstimate copyWith({
    Object? resolution = undefined,
    Object? frameRate = undefined,
    Object? codec = undefined,
    Object? hardware = undefined,
    Object? bytes = undefined,
  }) => ResourceEstimate(
    resolution: pick<VideoSize?>(resolution, this.resolution),
    frameRate: pick<int?>(frameRate, this.frameRate),
    codec: pick<String?>(codec, this.codec),
    hardware: pick<bool?>(hardware, this.hardware),
    bytes: pick<int?>(bytes, this.bytes),
  );

  @override
  bool operator ==(Object other) =>
      other is ResourceEstimate &&
      other.resolution == resolution &&
      other.frameRate == frameRate &&
      other.codec == codec &&
      other.hardware == hardware &&
      other.bytes == bytes;

  @override
  int get hashCode =>
      Object.hash(resolution, frameRate, codec, hardware, bytes);

  @override
  String toString() =>
      'ResourceEstimate($resolution, fps: $frameRate, codec: $codec, '
      'hw: $hardware, bytes: $bytes)';
}

/// Request to reserve a resource (07 §2).
@immutable
final class ResourceRequest {
  /// Creates a request.
  const ResourceRequest({
    required this.sessionId,
    required this.kind,
    required this.priority,
    this.estimate = const ResourceEstimate(),
  });

  /// Consumer session.
  final String sessionId;

  /// Kind.
  final ResourceKind kind;

  /// Estimate.
  final ResourceEstimate estimate;

  /// Priority.
  final ResourcePriority priority;

  /// Returns a copy with the given fields replaced.
  ResourceRequest copyWith({
    String? sessionId,
    ResourceKind? kind,
    ResourceEstimate? estimate,
    ResourcePriority? priority,
  }) => ResourceRequest(
    sessionId: sessionId ?? this.sessionId,
    kind: kind ?? this.kind,
    estimate: estimate ?? this.estimate,
    priority: priority ?? this.priority,
  );

  @override
  bool operator ==(Object other) =>
      other is ResourceRequest &&
      other.sessionId == sessionId &&
      other.kind == kind &&
      other.estimate == estimate &&
      other.priority == priority;

  @override
  int get hashCode => Object.hash(sessionId, kind, estimate, priority);

  @override
  String toString() =>
      'ResourceRequest($sessionId, ${kind.name}, ${priority.name}, $estimate)';
}

/// A granted reservation; release it when done.
abstract interface class ResourceLease {
  /// Lease ID.
  String get leaseId;

  /// Kind.
  ResourceKind get kind;

  /// Returns the lease. Idempotent.
  Future<void> release();
}

/// Reservation outcome (07 §2).
@immutable
sealed class ReservationResult {
  const ReservationResult();
}

/// Granted.
final class ReservationGranted extends ReservationResult {
  /// Creates the result.
  const ReservationGranted(this.lease);

  /// Lease.
  final ResourceLease lease;

  @override
  bool operator ==(Object other) =>
      other is ReservationGranted && identical(other.lease, lease);

  @override
  int get hashCode => Object.hash(ReservationGranted, identityHashCode(lease));

  @override
  String toString() => 'ReservationGranted(${lease.leaseId})';
}

/// Denied with an explanation and a suggestion.
final class ReservationDenied extends ReservationResult {
  /// Creates the result.
  const ReservationDenied(this.reason, this.suggestion);

  /// Redacted reason code.
  final String reason;

  /// Suggested degradation.
  final DegradeSuggestion suggestion;

  @override
  bool operator ==(Object other) =>
      other is ReservationDenied &&
      other.reason == reason &&
      other.suggestion == suggestion;

  @override
  int get hashCode => Object.hash(ReservationDenied, reason, suggestion);

  @override
  String toString() => 'ReservationDenied($reason, ${suggestion.name})';
}

/// Per-kind usage in a [ResourceReport].
@immutable
final class ResourceUsage {
  /// Creates a usage entry.
  ResourceUsage({
    required this.kind,
    this.reserved = 0,
    this.held = 0,
    List<String> consumers = const [],
    List<String> unconfirmedReleases = const [],
  }) : consumers = frozenList(consumers),
       unconfirmedReleases = frozenList(unconfirmedReleases);

  /// Kind.
  final ResourceKind kind;

  /// Reserved count/bytes.
  final int reserved;

  /// Actually held count/bytes.
  final int held;

  /// Consumer session IDs.
  final List<String> consumers;

  /// Session IDs whose release is not yet confirmed.
  final List<String> unconfirmedReleases;

  /// Returns a copy with the given fields replaced.
  ResourceUsage copyWith({
    ResourceKind? kind,
    int? reserved,
    int? held,
    List<String>? consumers,
    List<String>? unconfirmedReleases,
  }) => ResourceUsage(
    kind: kind ?? this.kind,
    reserved: reserved ?? this.reserved,
    held: held ?? this.held,
    consumers: consumers ?? this.consumers,
    unconfirmedReleases: unconfirmedReleases ?? this.unconfirmedReleases,
  );

  @override
  bool operator ==(Object other) =>
      other is ResourceUsage &&
      other.kind == kind &&
      other.reserved == reserved &&
      other.held == held &&
      listEquals(other.consumers, consumers) &&
      listEquals(other.unconfirmedReleases, unconfirmedReleases);

  @override
  int get hashCode => Object.hash(
    kind,
    reserved,
    held,
    hashList(consumers),
    hashList(unconfirmedReleases),
  );

  @override
  String toString() =>
      'ResourceUsage(${kind.name}, reserved: $reserved, held: $held, '
      'consumers: $consumers, unconfirmed: $unconfirmedReleases)';
}

/// Snapshot of the budget (07 §2).
@immutable
final class ResourceReport {
  /// Creates a report.
  ResourceReport({List<ResourceUsage> usages = const []})
    : usages = frozenList(usages);

  /// Usage per kind.
  final List<ResourceUsage> usages;

  /// Returns a copy with the given fields replaced.
  ResourceReport copyWith({List<ResourceUsage>? usages}) =>
      ResourceReport(usages: usages ?? this.usages);

  @override
  bool operator ==(Object other) =>
      other is ResourceReport && listEquals(other.usages, usages);

  @override
  int get hashCode => hashList(usages);

  @override
  String toString() => 'ResourceReport($usages)';
}

/// Host-scope resource budget (07 §2). Native implementations do the real
/// accounting; a Dart implementation is optional.
abstract interface class ResourceBudget {
  /// Reserves a resource.
  Future<ReservationResult> reserve(ResourceRequest request);

  /// Current report.
  ResourceReport snapshot();
}
