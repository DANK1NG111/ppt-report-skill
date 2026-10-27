$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$explicitPython = $null
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--python" -and $i + 1 -lt $args.Count) { $explicitPython = $args[$i + 1]; break }
    if ($args[$i] -like "--python=*") { $explicitPython = $args[$i].Substring(9); break }
}
if ($explicitPython) {
    & $explicitPython "$root/scripts/setup.py" @args
    exit $LASTEXITCODE
}
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & $python.Source -c "import sys; raise SystemExit(sys.version_info < (3, 11))" 2>$null
    if ($LASTEXITCODE -eq 0) {
    & $python.Source "$root/scripts/setup.py" @args
    exit $LASTEXITCODE
    }
}
$uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uv) {
    $env:UV_INSTALL_DIR = Join-Path $root ".runtime/bin"
    $env:UV_NO_MODIFY_PATH = "1"
    $installer = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString() + ".ps1")
    try {
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile $installer
        & $installer
        $uvPath = Join-Path $env:UV_INSTALL_DIR "uv.exe"
    } finally { Remove-Item $installer -ErrorAction SilentlyContinue }
} else { $uvPath = $uv.Source }
& $uvPath run --no-project --python 3.12 "$root/scripts/setup.py" @args
exit $LASTEXITCODE
