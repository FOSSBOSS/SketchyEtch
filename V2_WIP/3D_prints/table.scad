// Parameters
table_width = 150;
table_length = 200;
table_thickness = 2.5;
leg_height = 20;
leg_thickness = 10
;  // Thickness of legs (square cross-section)

// Flip the whole model upside down
rotate([180, 0, 0]) {
    // Tabletop
    cube([table_width, table_length, table_thickness]);

    // Legs
    translate([0, 0, -leg_height])
        cube([leg_thickness, leg_thickness, leg_height]);

    translate([table_width - leg_thickness, 0, -leg_height])
        cube([leg_thickness, leg_thickness, leg_height]);

    translate([0, table_length - leg_thickness, -leg_height])
        cube([leg_thickness, leg_thickness, leg_height]);

    translate([table_width - leg_thickness, table_length - leg_thickness, -leg_height])
        cube([leg_thickness, leg_thickness, leg_height]);
}
