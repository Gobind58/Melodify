import 'package:flutter/material.dart';

class AlbumCard extends StatelessWidget {

  final dynamic album;

  const AlbumCard({required this.album});

  @override
  Widget build(BuildContext context) {

    return Container(
      width:140,
      margin: EdgeInsets.only(right:15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: Image.network(
              album.image,
              height:140,
              width:140,
              fit: BoxFit.cover,
            ),
          ),

          SizedBox(height:8),

          Text(
            album.title,
            style: TextStyle(fontWeight: FontWeight.bold),
          ),

          Text(
            "Playlist • Melofify",
            style: TextStyle(color: Colors.grey,fontSize:12),
          )

        ],
      ),
    );
  }
}