class Album {

  final String title;
  final String image;

  Album(this.title,this.image);
}

class Song {

  final String title;
  final String artist;
  final String image;
  final String url;

  Song({
    required this.title,
    required this.artist,
    required this.image,
    required this.url,
  });
}

final albums = [

  Album("Daily Mix","https://picsum.photos/200"),
  Album("Top Hits","https://picsum.photos/201"),
  Album("Hip Hop","https://picsum.photos/202"),
  Album("Chill","https://picsum.photos/203"),
  Album("Focus","https://picsum.photos/204"),
];

final songs = [

  Song(
    title: "Dreams",
    artist: "Melofify",
    image: "https://picsum.photos/200",
    url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
  ),

  Song(
    title: "Night Drive",
    artist: "Melofify",
    image: "https://picsum.photos/201",
    url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
  ),

];