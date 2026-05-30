import 'package:flutter/material.dart';
import '../widgets/album_card.dart';
import '../data/dummy_data.dart';

class HomeScreen extends StatelessWidget {

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        backgroundColor: Colors.black,
        body: Padding(
          padding: EdgeInsets.all(16),
          child: ListView(
            children: [

              Text(
                "Good Evening",
                style: TextStyle(fontSize:26,fontWeight:FontWeight.bold),
              ),

              SizedBox(height:20),

              GridView.builder(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                itemCount: albums.length,
                gridDelegate:
                SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisExtent: 70,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                ),
                itemBuilder: (context,index){

                  return Container(
                    decoration: BoxDecoration(
                      color: Colors.grey[900],
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      children: [

                        ClipRRect(
                          borderRadius: BorderRadius.horizontal(left: Radius.circular(6)),
                          child: Image.network(
                            albums[index].image,
                            width:70,
                            height:70,
                            fit: BoxFit.cover,
                          ),
                        ),

                        SizedBox(width:10),

                        Expanded(
                          child: Text(
                            albums[index].title,
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                        )
                      ],
                    ),
                  );
                },
              ),

              SizedBox(height:30),

              Text(
                "Made For You",
                style: TextStyle(fontSize:22,fontWeight:FontWeight.bold),
              ),

              SizedBox(height:15),

              SizedBox(
                height:180,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: albums.length,
                  itemBuilder:(context,index){
                    return AlbumCard(album: albums[index]);
                  },
                ),
              )

            ],
          ),
        ),
      ),
    );
  }
}