import 'package:flutter/material.dart';

class LibraryScreen extends StatelessWidget {

  final playlists = [
    "Liked Songs",
    "Workout Mix",
    "Chill Vibes",
    "Top Hits",
    "Focus Music"
  ];

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: Colors.black,

      appBar: AppBar(
        backgroundColor: Colors.black,
        title: Text("Your Library"),
      ),

      body: ListView.builder(
        itemCount: playlists.length,
        itemBuilder:(context,index){

          return ListTile(
            leading: Icon(Icons.music_note,color: Colors.white),
            title: Text(playlists[index]),
            subtitle: Text("Playlist • Melofify"),
          );
        },
      ),
    );
  }
}