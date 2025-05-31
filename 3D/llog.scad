module ll(l = 30 , r = 9){
//Lincon Log module
$fn = 100;
difference(){
difference(){
rotate([0,90,0])cylinder(l,r,r);
translate([5,-r,4]) cube([r,2*r,6]);
 
}
translate([5,-r,-r]) cube([r,2*r,6]);  
}
}
ll(25,8);

//translate([60,0,0])rotate(180)ll(4,8);
