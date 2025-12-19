#!/usr/bin/env bash
# Render start script

# Set environment variables
export TRANSFORMERS_CACHE=/tmp/transformers_cache
export HF_HOME=/tmp/huggingface

# Create cache directories
mkdir -p $TRANSFORMERS_CACHE
mkdir -p $HF_HOME

# Run streamlit with proper port binding
exec streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
