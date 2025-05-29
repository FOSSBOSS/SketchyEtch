// brick.scad
w = 8;
h = 9.6;

module lego_brick(studs=4){
    $fn = 80;
    width = 8 * studs;
    cube([width,16,9.6]);
    for (xpos=[4 : 8 : width-4]){
        translate([xpos,4,1.7]) cylinder(h=9.6,d=4.8);
        translate([xpos,12,1.7]) cylinder(h=9.6,d=4.8);
    }
}
