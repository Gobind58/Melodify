import 'dart:async';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:audio_service/audio_service.dart';
import 'package:rxdart/rxdart.dart';

// ─── Combined position model so we only need ONE StreamBuilder for the slider ───
class PositionData {
  final Duration position;
  final Duration duration;
  const PositionData(this.position, this.duration);
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // AudioService.init already awaits the builder; _init() is now called
  // inside the factory so the heavy async work is fully awaited before
  // the app renders a single frame.
  final handler = await AudioService.init(
    builder: () => MelodifyAudioHandler(),
    config: const AudioServiceConfig(
      androidNotificationChannelId: 'melodify.audio',
      androidNotificationChannelName: 'Melodify Music',
      androidNotificationOngoing: true,
    ),
  );

  // Kick off playlist setup *after* the service is registered.
  await handler.init();

  runApp(Melodify(handler));
}

// ─────────────────────────────────────────────────────────────────────────────
class Melodify extends StatelessWidget {
  final MelodifyAudioHandler handler;
  const Melodify(this.handler, {super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: HomeScreen(handler),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
class MelodifyAudioHandler extends BaseAudioHandler {
  final AudioPlayer _player = AudioPlayer();
  late final ConcatenatingAudioSource _playlist;

  // Expose a combined stream so the UI subscribes to ONE stream, not two.
  late final Stream<PositionData> positionDataStream;

  // FIX: no longer calls _init() in the constructor — that caused the
  // "doing too much work on main thread" jank because the Future was
  // untracked and could race with the first frame build.
  MelodifyAudioHandler();

  Future<void> init() async {
    _playlist = ConcatenatingAudioSource(children: [
      AudioSource.uri(
        Uri.parse(
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'),
        tag: MediaItem(
          id: '1',
          title: 'Dreams',
          artist: 'Melodify',
          artUri: Uri.parse('https://picsum.photos/seed/dreams/400'),
        ),
      ),
      AudioSource.uri(
        Uri.parse(
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3'),
        tag: MediaItem(
          id: '2',
          title: 'Night Drive',
          artist: 'Melodify',
          artUri: Uri.parse('https://picsum.photos/seed/nightdrive/400'),
        ),
      ),
      AudioSource.uri(
        Uri.parse(
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3'),
        tag: MediaItem(
          id: '3',
          title: 'Chill Vibes',
          artist: 'Melodify',
          artUri: Uri.parse('https://picsum.photos/seed/chillvibes/400'),
        ),
      ),
    ]);

    await _player.setAudioSource(_playlist);

    // FIX: combine position + duration into a single stream so the UI only
    // needs ONE StreamBuilder instead of two nested ones.
    positionDataStream = Rx.combineLatest2<Duration, Duration?, PositionData>(
      _player.positionStream,
      _player.durationStream,
      (position, duration) => PositionData(position, duration ?? Duration.zero),
    );

    // Update mediaItem when the track changes.
    _player.currentIndexStream.listen((index) {
      if (index != null) {
        final source = _playlist.children[index] as UriAudioSource;
        mediaItem.add(source.tag as MediaItem);
      }
    });

    // FIX: Use playingStream + processingStateStream instead of the
    // high-frequency playbackEventStream. These only emit when the
    // value actually changes, dramatically reducing UI rebuilds.
    Rx.combineLatest2<bool, ProcessingState, PlaybackState>(
      _player.playingStream,
      _player.processingStateStream,
      (playing, processingState) => playbackState.value.copyWith(
        controls: [
          MediaControl.skipToPrevious,
          if (playing) MediaControl.pause else MediaControl.play,
          MediaControl.skipToNext,
        ],
        playing: playing,
        processingState: _mapProcessingState(processingState),
      ),
    ).listen(playbackState.add);
  }

  AudioPlayer get player => _player;

  AudioProcessingState _mapProcessingState(ProcessingState state) {
    switch (state) {
      case ProcessingState.idle:
        return AudioProcessingState.idle;
      case ProcessingState.loading:
        return AudioProcessingState.loading;
      case ProcessingState.buffering:
        return AudioProcessingState.buffering;
      case ProcessingState.ready:
        return AudioProcessingState.ready;
      case ProcessingState.completed:
        return AudioProcessingState.completed;
    }
  }

  @override
  Future<void> play() => _player.play();

  @override
  Future<void> pause() => _player.pause();

  @override
  Future<void> skipToNext() => _player.seekToNext();

  @override
  Future<void> skipToPrevious() => _player.seekToPrevious();

  @override
  Future<void> seek(Duration position) => _player.seek(position);
}

// ─────────────────────────────────────────────────────────────────────────────
class HomeScreen extends StatelessWidget {
  final MelodifyAudioHandler handler;
  const HomeScreen(this.handler, {super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Column(
        children: [
          Expanded(child: PlayerUI(handler)),
          MiniPlayer(handler),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
class PlayerUI extends StatelessWidget {
  final MelodifyAudioHandler handler;
  const PlayerUI(this.handler, {super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<MediaItem?>(
      stream: handler.mediaItem,
      builder: (context, snapshot) {
        final song = snapshot.data;
        if (song == null) return const SizedBox();

        return Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.network(
              song.artUri.toString(),
              height: 300,
              cacheWidth: 300,
            ),

            const SizedBox(height: 20),

            Text(
              song.title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),

            Text(
              song.artist ?? '',
              style: const TextStyle(color: Colors.grey),
            ),

            // FIX: Single StreamBuilder using the pre-combined positionDataStream.
            // Before: two NESTED StreamBuilders — positionStream fires ~10× per
            // second, each event rebuilt the inner durationStream builder too.
            StreamBuilder<PositionData>(
              stream: handler.positionDataStream,
              builder: (context, snapshot) {
                final pos = snapshot.data ??
                    const PositionData(Duration.zero, Duration.zero);
                final maxSeconds = pos.duration.inSeconds.toDouble();

                return Slider(
                  min: 0,
                  max: maxSeconds > 0 ? maxSeconds : 1,
                  value: pos.position.inSeconds
                      .clamp(0, pos.duration.inSeconds)
                      .toDouble(),
                  onChanged: (value) {
                    handler.seek(Duration(seconds: value.toInt()));
                  },
                );
              },
            ),

            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  iconSize: 40,
                  icon: const Icon(Icons.skip_previous),
                  onPressed: handler.skipToPrevious,
                ),
                StreamBuilder<bool>(
                  stream: handler.player.playingStream,
                  builder: (context, snapshot) {
                    final playing = snapshot.data ?? false;
                    return IconButton(
                      iconSize: 70,
                      icon: Icon(
                        playing ? Icons.pause_circle : Icons.play_circle,
                      ),
                      onPressed: () =>
                          playing ? handler.pause() : handler.play(),
                    );
                  },
                ),
                IconButton(
                  iconSize: 40,
                  icon: const Icon(Icons.skip_next),
                  onPressed: handler.skipToNext,
                ),
              ],
            ),
          ],
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
class MiniPlayer extends StatelessWidget {
  final MelodifyAudioHandler handler;
  const MiniPlayer(this.handler, {super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<MediaItem?>(
      stream: handler.mediaItem,
      builder: (context, snapshot) {
        final song = snapshot.data;
        if (song == null) return const SizedBox();

        return Container(
          height: 70,
          color: Colors.grey[900],
          child: ListTile(
            leading: Image.network(
              song.artUri.toString(),
              cacheWidth: 100,
            ),
            title: Text(song.title),
            subtitle: Text(song.artist ?? ''),
            // FIX: was always showing play_arrow regardless of state.
            trailing: StreamBuilder<bool>(
              stream: handler.player.playingStream,
              builder: (context, snapshot) {
                final playing = snapshot.data ?? false;
                return IconButton(
                  icon: Icon(playing ? Icons.pause : Icons.play_arrow),
                  onPressed: () => playing ? handler.pause() : handler.play(),
                );
              },
            ),
          ),
        );
      },
    );
  }
}
