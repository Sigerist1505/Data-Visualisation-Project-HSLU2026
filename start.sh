#!/bin/bash

# Start Jupyter Notebook in the background (no token for easy access)
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
    --NotebookApp.token='' --NotebookApp.password='' &

# Start Streamlit in the foreground
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
