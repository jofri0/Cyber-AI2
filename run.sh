#!/bin/bash
set -e  # stop on error

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📂 Making sure data folder exists..."
mkdir -p data

echo "🚀 Running data fetch pipeline..."
python src/data_fetch.py

echo "✅ All done! Data saved to data/train.txt"
