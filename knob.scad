/*
Create Knobs for your rotary Encoders
*/
$fn = 500;

rad=24.0;
//This cylinder covers the hole for the knob
cylinder(3.0,rad,true); //cap thickness, radius
//translate(0.0,0.0,10.0);
difference(){
    cylinder(10,rad,rad);//knob length, top radius ,bot radius
difference(){
    cylinder(d=6.0, h=25);//d inner hole
    translate([0,50.0,40]) //2nd var: how far teh flat is into the hole
    cube(96, center=true);
}
}


