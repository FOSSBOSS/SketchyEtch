w=8;
h=9.6;

module lego_brick(studs=4){
    $fn = 80;
    width = 8 * studs;
    cube([width,16,9.6]);
    for (xpos=[ 4 : 8 : width-4 ]){
        translate([xpos,4,1.7]) cylinder(h=9.6,d=4.8);
        translate([xpos,12,1.7]) cylinder(h=9.6,d=4.8);
        }
    
    }
    
    rotate(0) translate([0,-h,0])lego_brick(4);
    rotate(90) translate([0,-h,0])lego_brick(4);
    rotate(180) translate([0,-h,0])lego_brick(4);
    rotate(270) translate([0,-h,h])lego_brick(4);

    /*The goal is to have 4 trackable units
    degrees, x,y,z
    x,y,z increment by lego_brick() size in their respective dimensions.
    degrees are fixed to 0,90,180,270
    
    */
