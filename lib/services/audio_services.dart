import 'package:just_audio/just_audio.dart';

class AudioPlayerService {

  final AudioPlayer player = AudioPlayer();

  Future<void> playSong(String url) async {
    await player.setUrl(url);
    player.play();
  }

  void pauseSong() {
    player.pause();
  }

  void stopSong() {
    player.stop();
  }
}