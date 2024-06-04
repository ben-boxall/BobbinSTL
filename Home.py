import trimesh
import streamlit as st
import tempfile
import os
import pyvista as pv
from stpyvista import stpyvista
pv.start_xvfb()

def create_cylinder_mesh(internal_diameter, wall_thickness, height, flange_diameter, flange_thickness):
    external_diameter = internal_diameter + 2 * wall_thickness
    radius_inner = internal_diameter / 2
    radius_outer = external_diameter / 2
    radius_flange = flange_diameter / 2

    # Create outer and inner cylinders
    outer_cylinder = trimesh.creation.cylinder(radius=radius_outer, height=height, sections=32)
    inner_cylinder = trimesh.creation.cylinder(radius=radius_inner, height=height, sections=32)
    
    # Create hollow cylinder by subtracting inner from outer
    hollow_cylinder = outer_cylinder.difference(inner_cylinder)

    # Create top and bottom discs
    top_disc = trimesh.creation.annulus(r_min=radius_inner, r_max=radius_outer, height=0.1, sections=32)
    top_disc.apply_translation([0, 0, height / 2])
    
    bottom_disc = trimesh.creation.annulus(r_min=radius_inner, r_max=radius_outer, height=0.1, sections=32)
    bottom_disc.apply_translation([0, 0, -height / 2])
    
    # Combine parts
    combined_cylinder = hollow_cylinder.union([top_disc, bottom_disc])
    
    # Create flanges
    flange_outer_top = trimesh.creation.cylinder(radius=radius_flange, height=flange_thickness, sections=32)
    flange_inner_top = trimesh.creation.cylinder(radius=radius_inner, height=flange_thickness, sections=32)
    flange_top = flange_outer_top.difference(flange_inner_top)
    flange_top.apply_translation([0, 0, height / 2 + flange_thickness / 2])
    
    flange_outer_bottom = trimesh.creation.cylinder(radius=radius_flange, height=flange_thickness, sections=32)
    flange_inner_bottom = trimesh.creation.cylinder(radius=radius_inner, height=flange_thickness, sections=32)
    flange_bottom = flange_outer_bottom.difference(flange_inner_bottom)
    flange_bottom.apply_translation([0, 0, -height / 2 - flange_thickness / 2])
    
    # Add flanges to the cylinder
    combined_cylinder = combined_cylinder.union([flange_top, flange_bottom])
    
    return combined_cylinder

st.title("Bobbin STL Generator")

internal_diameter = st.number_input("Internal Diameter (ID)", min_value=0.0, step=0.1, value=5.0)
wall_thickness = st.number_input("Wall Thickness", min_value=0.0, step=0.1, value=5.0)
height = st.number_input("Height", min_value=0.0, step=0.1, value=10.0)
flange_diameter = st.number_input("Flange Diameter", min_value=0.0, step=0.1, value=15.0)
flange_thickness = st.number_input("Flange Thickness", min_value=0.0, step=0.1, value=1.0)

if st.button("Generate STL"):
    if internal_diameter > 0 and wall_thickness > 0 and height > 0 and flange_diameter > 0 and flange_thickness > 0:
        cylinder_mesh = create_cylinder_mesh(internal_diameter, wall_thickness, height, flange_diameter, flange_thickness)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp_file:
            tmp_file_name = tmp_file.name
            cylinder_mesh.export(tmp_file_name, file_type='stl')

        st.write("Cylinder STL:")

        # Convert the mesh to a PyVista object and display it using stpyvista
        mesh_pv = pv.wrap(cylinder_mesh)
        plotter = pv.Plotter(window_size=[800, 600])
        plotter.add_mesh(mesh_pv, color="tan")
        plotter.background_color = "white"
        plotter.view_isometric()
        stpyvista(plotter)

        st.download_button(
            label="Download STL",
            data=open(tmp_file_name, "rb").read(),
            file_name="cylinder.stl",
            mime="application/octet-stream"
        )

        os.remove(tmp_file_name)
    else:
        st.error("Please provide valid dimensions for the cylinder and flanges.")
