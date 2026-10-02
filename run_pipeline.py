"""Run all reproducible steps with: python run_pipeline.py"""
from src.generate_data import generate
from src.build_database import build
from src.make_dashboard import make_dashboard

if __name__ == "__main__":
    print("GENERATE:",generate())
    print("SUMMARY:",build())
    print("DASHBOARD:",make_dashboard())