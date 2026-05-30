import 'package:flutter/material.dart';

class SearchScreen extends StatelessWidget {

  final genres = [
    "Pop",
    "Hip Hop",
    "Rock",
    "Chill",
    "Workout",
    "Electronic",
    "Focus"
  ];

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: Colors.black,

      appBar: AppBar(
        title: Text("Search"),
        backgroundColor: Colors.black,
      ),

      body: Padding(
        padding: EdgeInsets.all(16),
        child: GridView.builder(
          itemCount: genres.length,
          gridDelegate:
          SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount:2,
              mainAxisSpacing:12,
              crossAxisSpacing:12
          ),
          itemBuilder:(context,index){

            return Container(
              decoration: BoxDecoration(
                color: Colors.primaries[index],
                borderRadius: BorderRadius.circular(10),
              ),
              padding: EdgeInsets.all(12),
              child: Align(
                alignment: Alignment.topLeft,
                child: Text(
                  genres[index],
                  style: TextStyle(
                    fontSize:18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}