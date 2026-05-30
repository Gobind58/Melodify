import 'package:flutter/material.dart';

class PlayerScreen extends StatelessWidget {

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: Colors.black,

      appBar: AppBar(
        backgroundColor: Colors.black,
        title: Text("Now Playing"),
      ),

      body: Column(
        children: [

          SizedBox(height:40),

          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Image.network(
                "https://picsum.photos/400",
                height:300,
                width:300,
                fit: BoxFit.cover,
              ),
            ),
          ),

          SizedBox(height:40),

          Text(
            "Song Title",
            style: TextStyle(fontSize:24,fontWeight:FontWeight.bold),
          ),

          Text(
            "Artist Name",
            style: TextStyle(color: Colors.grey),
          ),

          SizedBox(height:30),

          Slider(
            value: 0.4,
            onChanged: (value){},
          ),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [

              Icon(Icons.shuffle,size:28),
              Icon(Icons.skip_previous,size:40),
              Icon(Icons.play_circle,size:70),
              Icon(Icons.skip_next,size:40),
              Icon(Icons.repeat,size:28),

            ],
          )

        ],
      ),
    );
  }
}