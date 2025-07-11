import requests
from io import BytesIO
from datetime import datetime
import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord

st.title("Astrophotography FOV Simulator")
st.markdown("Author: [Bill Chen](https://yingtianchen.com/)")    

focal_length = st.number_input(
    "Telescope Focal Length (mm)", 
    value=1500.0, min_value=0.0
)
sensor_width = st.number_input(
    "Camera Sensor Width (mm)", 
    value=11.31, min_value=0.0
)
sensor_height = st.number_input(
    "Camera Sensor Height (mm)", 
    value=11.31, min_value=0.0
)
objname = st.text_input(
    "Object Name", value="M101"
)

def generate_figure(focal_length, sensor_width, sensor_height, objname):
    rad2deg = 180 / np.pi
    fov_width = rad2deg * sensor_width / focal_length
    fov_height = rad2deg * sensor_height / focal_length

    factor = 1.5
    img_size = factor * max(fov_width, fov_height)
    npix = 512
    scale = img_size * 3600 / npix

    try:
        obj = SkyCoord.from_name(objname)
        ra, dec = obj.ra.deg, obj.dec.deg

        url = f"http://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg?"\
            f"ra={ra}&dec={dec}&scale={scale}&width={npix}&height={npix}"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

        fig, ax0 = plt.subplots(1, 1, figsize=(6,6))
        ax0.imshow(img, extent=(-img_size/2,img_size/2,-img_size/2,img_size/2))

        fov_arr = np.array([
            [-fov_width/2,-fov_height/2],
            [fov_width/2,-fov_height/2],
            [fov_width/2,fov_height/2],
            [-fov_width/2,fov_height/2],
            [-fov_width/2,-fov_height/2]
        ])
        ax0.plot(fov_arr[:,0], fov_arr[:,1], c="w", lw=2)

        ax0.text(
            0.95, 0.95, objname, ha="right", va="top", color="w", fontsize=16, 
            transform=ax0.transAxes
        )
        ax0.text(
            0,1.05*fov_arr[0,1], 
            f"f: {focal_length:g} mm + "\
                f"camera: {sensor_width:g}x{sensor_height:g} mm",
            ha="center", va="top", color="w", fontsize=10)

        ax0.set_aspect("equal")
        ax0.set_xticks([])
        ax0.set_yticks([])
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")

if "ran_once" not in st.session_state:
    st.session_state.ran_once = True
    generate_figure(focal_length, sensor_width, sensor_height, objname)

if st.button("Generate FOV"):
    generate_figure(focal_length, sensor_width, sensor_height, objname)