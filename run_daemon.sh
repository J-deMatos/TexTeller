#!/bin/bash

# Quick launcher for TexTeller LaTeX Predictor Daemon
# This script just runs the daemon without setup

echo "TexTeller LaTeX Predictor Daemon Launcher"
echo "========================================="
echo ""
echo "Choose an action:"
echo "1) Run daemon"
echo "2) Run tests"
echo "3) Benchmark performance"
echo ""
read -p "Choose an option (1-3): " -n 1 -r
echo

case $REPLY in
    1)
        echo "Starting daemon..."
        python daemon/run_daemon.py
        ;;
    2)
        echo "Running tests..."
        python tests/run_test.py
        ;;
    3)
        echo "Running benchmark..."
        python tests/benchmark_daemon.py
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac
