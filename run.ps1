Param(
  [string]$Host="127.0.0.1",
  [int]$Port=8025
)

Set-Location $PSScriptRoot

if (!(Test-Path .\.venv)) {
  python -m venv .venv
}

$venvPy = Resolve-Path .\.venv\Scripts\python.exe
& $venvPy -m pip install --upgrade pip
pip install -r requirements.txt

uvicorn src.app:app --host $Host --port $Port --reload