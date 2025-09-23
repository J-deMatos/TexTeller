# TexTeller LaTeX Predictor Daemon

This folder contains all the daemon-related files for the TexTeller LaTeX Predictor.

## Quick Start

1. **Setup**: `bash safe_setup_daemon.sh`
2. **Run Standard Daemon**: `python run_daemon.py`
3. **Run Optimized Daemon**: `python run_optimized_daemon.py`
4. **Run Tests**: `python run_test.py`
5. **Benchmark**: `python benchmark_daemon.py`

## Files

- **`latex_predictor_daemon.py`** - Standard daemon implementation
- **`optimized_daemon.py`** - Optimized daemon with performance improvements
- **`run_daemon.py`** - Launcher for standard daemon
- **`run_optimized_daemon.py`** - Launcher for optimized daemon
- **`run_test.py`** - Test runner
- **`benchmark_daemon.py`** - Performance benchmarking
- **`test_daemon.py`** - Test script
- **`venv_setup.py`** - Virtual environment setup
- **`cleanup_daemon.py`** - Cleanup script
- **`safe_setup_daemon.sh`** - Safe setup script
- **`daemon_requirements.txt`** - Requirements file
- **`DAEMON_README.md`** - Detailed documentation

## Documentation

See `DAEMON_README.md` for complete documentation.
