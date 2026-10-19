#!/usr/bin/env python3
"""Verify the language learning system setup."""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    print(f"❌ Python {version.major}.{version.minor} - Need 3.11+")
    return False


def check_ollama_installation():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama installed - {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("❌ Ollama not found - Install from https://ollama.ai")
    return False


def check_ollama_server():
    """Check if Ollama server is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=2)
        print("✅ Ollama server running on http://localhost:11434")
        return True
    except Exception:
        print("⚠️  Ollama server not running - Start with: ollama serve")
        return False


def check_installed_models():
    """Check for installed Ollama models."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "mistral" in result.stdout or "llama" in result.stdout:
            print("✅ Models installed:")
            for line in result.stdout.split("\n")[1:]:
                if line.strip():
                    print(f"   - {line.split()[0]}")
            return True
    except Exception:
        pass
    print("❌ No models found - Run: ollama pull mistral")
    return False


def check_project_structure():
    """Check project files."""
    required_files = [
        "pyproject.toml",
        "src/main.py",
        "src/agents/base_agent.py",
        "src/agents/coordinator_agent.py",
        "src/communication/a2a_broker.py",
        "src/schemas/messages.py",
        ".env.example",
        "README.md",
        "QUICKSTART.md",
    ]

    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            all_present = False

    return all_present


def check_dependencies():
    """Check Python dependencies."""
    try:
        import langgraph
        import langchain
        import pydantic
        from langchain_ollama import ChatOllama
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: uv sync")
        return False


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("🔍 LANGUAGE LEARNING SYSTEM - Setup Verification")
    print("="*60 + "\n")

    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Ollama Installation", check_ollama_installation),
        ("Ollama Server", check_ollama_server),
        ("Ollama Models", check_installed_models),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 Everything looks good! Run: uv run src/main.py")
    else:
        print("\n⚠️  Fix the issues above before running the app")

    print("="*60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

'''
# 2. Verify setup
uv run verify_setup.py

# 3. Run the app
uv run src/main.py'''