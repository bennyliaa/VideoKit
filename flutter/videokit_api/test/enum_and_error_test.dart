import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

void main() {
  group('ErrorCode', () {
    test('has the 22 codes of 04 §9.1 with stable wire names', () {
      expect(ErrorCode.values, hasLength(22));
      expect(ErrorCode.sourceNotFound.wireName, 'SOURCE_NOT_FOUND');
      expect(
        ErrorCode.internalErrorRedacted.wireName,
        'INTERNAL_ERROR_REDACTED',
      );
      expect(
        ErrorCode.outputCapabilityUnsupported.wireName,
        'OUTPUT_CAPABILITY_UNSUPPORTED',
      );
    });

    test('round-trips every value via Dart and wire names', () {
      for (final code in ErrorCode.values) {
        expect(ErrorCode.fromName(code.name), code);
        expect(ErrorCode.fromName(code.wireName), code);
      }
    });

    test('unknown or null codes map to internalErrorRedacted', () {
      expect(
        ErrorCode.fromName('SOME_FUTURE_CODE'),
        ErrorCode.internalErrorRedacted,
      );
      expect(ErrorCode.fromName(null), ErrorCode.internalErrorRedacted);
    });
  });

  group('enum fallbacks', () {
    test('non-state-machine enums fall back to a documented value', () {
      expect(ErrorStage.fromName('X'), ErrorStage.unknown);
      expect(SuggestedAction.fromName('X'), SuggestedAction.none);
      expect(UnsupportedReason.fromName('X'), UnsupportedReason.unknown);
      expect(MediaKind.fromName('X'), MediaKind.imageUnknown);
      expect(Seekability.fromName('X'), Seekability.sequentialOnly);
      expect(FitMode.fromName('X'), FitMode.fit);
      expect(SeekMode.fromName('X'), SeekMode.closestSync);
      expect(SessionVisibility.fromName('X'), SessionVisibility.offscreen);
      expect(OrientationRequest.fromName('X'), OrientationRequest.auto);
      expect(ActionPlacement.fromName('X'), ActionPlacement.overflow);
      expect(NavigationResult.fromName('X'), NavigationResult.failed);
      expect(RecoveryDecision.fromName('X'), RecoveryDecision.keepErrorState);
      expect(TrackingState.fromName('X'), TrackingState.notAnalyzed);
      expect(ExportStage.fromName('X'), ExportStage.preparing);
      expect(FeatureKey.fromName('X'), FeatureKey.unknown);
      expect(PrecheckIssueKind.fromName('X'), PrecheckIssueKind.unknown);
      expect(MediaKind.fromName('IMAGE_ANIMATED'), MediaKind.imageAnimated);
      expect(
        ResourcePriority.fromName('VISIBLE_AUDIBLE'),
        ResourcePriority.visibleAudible,
      );
    });

    test('state machine enums reject unknown names', () {
      expect(
        SessionPhase.fromName('ERROR_RECOVERABLE'),
        SessionPhase.errorRecoverable,
      );
      expect(() => SessionPhase.fromName('NOPE'), throwsArgumentError);
      expect(EditPhase.fromName('CANCELLING'), EditPhase.cancelling);
      expect(() => EditPhase.fromName('NOPE'), throwsArgumentError);
    });

    test('phase helpers', () {
      expect(SessionPhase.paused.isBound, isTrue);
      expect(SessionPhase.binding.isBound, isFalse);
      expect(SessionPhase.errorFatal.isError, isTrue);
      expect(SessionPhase.releasing.isReleasingOrReleased, isTrue);
      expect(EditPhase.ready.acceptsEdits, isTrue);
      expect(EditPhase.exporting.acceptsEdits, isFalse);
      expect(TrackingState.lost.blocksExport, isTrue);
      expect(TrackingState.lowConfidence.blocksExport, isFalse);
      expect(MaskType.face.isAutomatic, isTrue);
    });
  });

  group('VideoKitStableError', () {
    const e = VideoKitStableError(
      code: ErrorCode.sourceTimeout,
      stage: ErrorStage.playback,
      retryable: true,
      suggestedAction: SuggestedAction.retry,
      diagnostic: 'read_timeout',
    );

    test('equality, hashCode, copyWith', () {
      expect(e, e.copyWith());
      expect(e.hashCode, e.copyWith().hashCode);
      expect(e.copyWith(retryable: false), isNot(e));
      expect(e.copyWith(diagnostic: null).diagnostic, isNull);
      expect(e.toString(), contains('SOURCE_TIMEOUT'));
    });

    test('internal shortcut', () {
      const i = VideoKitStableError.internal();
      expect(i.code, ErrorCode.internalErrorRedacted);
      expect(i.retryable, isFalse);
      expect(const VideoKitException(i).toString(), contains('INTERNAL'));
    });
  });

  group('VideoKitApiVersion', () {
    test('parse, compare, compatibility', () {
      final v = VideoKitApiVersion.parse('1.2.3');
      expect(v, const VideoKitApiVersion(1, 2, 3));
      expect(v.toString(), '1.2.3');
      expect(v.compareTo(const VideoKitApiVersion(1, 10, 0)), lessThan(0));
      expect(v.isCompatibleWith(const VideoKitApiVersion(1, 0, 0)), isTrue);
      expect(v.isCompatibleWith(const VideoKitApiVersion(1, 3, 0)), isFalse);
      expect(v.isCompatibleWith(const VideoKitApiVersion(2, 0, 0)), isFalse);
      expect(() => VideoKitApiVersion.parse('1.2'), throwsFormatException);
      expect(() => VideoKitApiVersion.parse('1.x.0'), throwsFormatException);
      expect(VideoKitApiVersion.current.major, 1);
      expect(v.copyWith(patch: 9).patch, 9);
    });
  });
}
