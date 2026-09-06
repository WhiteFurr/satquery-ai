import streamlit as st
from controller import CentralController

@st.cache_resource
def load_controller():
    return CentralController()

controller = load_controller()

st.title("SatQuery AI")

uploaded_files = st.file_uploader(
    "Upload image(s)",
    accept_multiple_files=True,
    type=["tif", "tiff", "jpg", "png"]
)

query = st.text_input("Ask a question about the image(s)")

if st.button("Submit") and uploaded_files and query:
    paths = []

    for f in uploaded_files:
        path = f"../data/uploads/{f.name}"

        with open(path, "wb") as out:
            out.write(f.read())

        paths.append(path)

    result, log = controller.route(query, paths)

    st.write("**Answer:**", result)
    st.write("**Execution trace:**", log)