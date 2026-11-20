function Write-InfoMessage {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [string]$FunctionName = $MyInvocation.MyCommand.Name
    )

    Write-Host "- [$FunctionName] Info: $Message" -ForegroundColor Cyan
}

function Write-WarningMessage {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [string]$FunctionName = $MyInvocation.MyCommand.Name
    )

    Write-Host "- [$FunctionName] Warning: $Message" -ForegroundColor Magenta
}

function Write-ErrorMessage {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [Parameter(Mandatory = $false)]
        [string]$FunctionName = $MyInvocation.MyCommand.Name,
        [switch]$ThrowError
    )

    Write-Host "m- [$FunctionName] Error: $Message" -ForegroundColor Red
    if ($ThrowError) {
        throw $Message
    }
}

function Read-UserInput {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host $Message -ForegroundColor Yellow -NoNewline
    return Read-Host
}

function Get-LocalPythonExecutable {
    $functionName = $MyInvocation.MyCommand.Name
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $projectPython = Join-Path $workspaceRoot ".venv\Scripts\python.exe"
    if (Test-Path $projectPython -PathType Leaf) {
        Write-InfoMessage -Message "Using Python executable: $projectPython" -FunctionName $functionName
        return $projectPython
    }
    else {
        Write-ErrorMessage -Message "Local Python executable not found at $projectPython. Run the installation script first." -FunctionName $functionName -ThrowError
    }
}

function Get-TomlFile {
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $tomlFile = Join-Path $workspaceRoot "pyproject.toml"
    if (Test-Path $tomlFile -PathType Leaf) {
        return $tomlFile
    }
    else {
        throw "pyproject.toml file not found at $tomlFile."
    }
}

function Register-Kernel {
    param (
        [Parameter(Mandatory = $true)]
        [string]$KernelName,
        [Parameter(Mandatory = $false)]
        [string]$DisplayName
    )

    $functionName = $MyInvocation.MyCommand.Name

    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $pythonExecutable = Get-LocalPythonExecutable

    if (-not $DisplayName) {
        $DisplayName = "Python ($KernelName)"
    }
    
    $locationPushed = $false
    try {
        Push-Location $workspaceRoot
        $locationPushed = $true
        Write-InfoMessage -Message "Creating $KernelName ($DisplayName) Jupyter kernel." -FunctionName $functionName

        & $pythonExecutable -m ipykernel install --user --name $KernelName --display-name $DisplayName
        if ($LASTEXITCODE -ne 0) {
            throw "Python failed to register the Jupyter kernel (exit code $LASTEXITCODE)."
        }
    }
    catch {
        Write-ErrorMessage -Message "Failed to create the $KernelName Jupyter kernel. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
    }
    finally {
        if ($locationPushed) {
            Pop-Location
        }
    }
}

function Unregister-Kernel {
    param (
        [Parameter(Mandatory = $true)]
        [string]$KernelName
    )
    $functionName = $MyInvocation.MyCommand.Name
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $pythonExecutable = Get-LocalPythonExecutable

    try {
        Push-Location $workspaceRoot
        try {
            Write-InfoMessage -Message "Removing $KernelName Jupyter kernel." -FunctionName $functionName

            & $pythonExecutable -m jupyter kernelspec uninstall $KernelName -f
            $uninstallExitCode = $LASTEXITCODE
            if ($uninstallExitCode -ne 0) {
                Write-WarningMessage -Message "Jupyter could not remove the kernel (exit code $uninstallExitCode); checking its files directly." -FunctionName $functionName
            }

            $kernelPath = Join-Path $env:APPDATA "jupyter\kernels\$KernelName"
            if (Test-Path $kernelPath) {
                Remove-PathIfExists -Path $kernelPath -Description "the $KernelName Jupyter kernel" -FunctionName $functionName
            }
            else {
                Write-InfoMessage -Message "No remaining Jupyter kernel files found for $KernelName." -FunctionName $functionName
            }
        }
        finally {
            Pop-Location
        }
    }
    catch {
        Write-ErrorMessage -Message "Failed to remove the $KernelName Jupyter kernel. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
    }
}

function Get-ToolkitName {
    $tomlFile = Get-TomlFile
    $tomlContent = Get-Content -LiteralPath $tomlFile -ErrorAction Stop
    foreach ($line in $tomlContent) {
        if ($line -match '^\s*name\s*=\s*"([^"]+)"\s*$') {
            return $matches[1]
        }
    }
    throw "Project name was not found in $tomlFile."
}

function Remove-PathIfExists {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [Parameter(Mandatory = $true)]
        [string]$FunctionName
    )

    if (Test-Path $Path) {
        try {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            Write-InfoMessage -Message "Removed ${Description}: $Path" -FunctionName $FunctionName
        }
        catch {
            Write-ErrorMessage -Message "Could not remove ${Description} at $Path. $($_.Exception.Message)" -FunctionName $FunctionName -ThrowError
        }
    }
}

function Get-UVExecutable {
    return Join-Path $env:ProgramData "BHoM\Extensions\Python\tools\uv.exe"
}

function Install-UV {
    $functionName = $MyInvocation.MyCommand.Name
    $uvExecutable = Get-UVExecutable
    $uvBinPath = Split-Path -Parent $uvExecutable

    if (-not (Test-Path -LiteralPath $uvExecutable -PathType Leaf)) {
        try {
            Write-InfoMessage -Message "Installing UV in $uvBinPath." -FunctionName $functionName
            $escapedDirectory = $uvBinPath.Replace("'", "''")
            & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "`$ErrorActionPreference = 'Stop'; `$env:UV_INSTALL_DIR = '$escapedDirectory'; `$env:UV_NO_MODIFY_PATH = '1'; irm https://astral.sh/uv/install.ps1 | iex"
            if ($LASTEXITCODE -ne 0) {
                throw "UV installer exited with code $LASTEXITCODE."
            }
        }
        catch {
            Write-ErrorMessage -Message "Failed to install UV. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
        }
    }

    try {
        if (-not (Test-Path -LiteralPath $uvExecutable -PathType Leaf)) {
            throw "The UV executable was not installed at $uvExecutable."
        }
        $otherPaths = @($env:Path -split ';' | Where-Object { $_.Trim().Trim('"') -ine $uvBinPath })
        $env:Path = (@($uvBinPath) + $otherPaths) -join ';'
        Write-InfoMessage -Message "Using UV from $uvExecutable." -FunctionName $functionName
    }
    catch {
        Write-ErrorMessage -Message "Could not locate UV. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
    }

    # install core tools
    foreach ($tool in @("ruff", "jupyterlab", "sphinx")) {
        try {
            Write-InfoMessage -Message "Installing $tool to UV." -FunctionName $functionName
            & $uvExecutable tool install $tool
            if ($LASTEXITCODE -ne 0) {
                throw "uv tool install exited with code $LASTEXITCODE."
            }
        }
        catch {
            Write-ErrorMessage -Message "Failed to install $tool to UV. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
        }
    }
}

function Sync-PythonEnvironment {
    $functionName = $MyInvocation.MyCommand.Name
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $locationPushed = $false

    try {
        Push-Location $workspaceRoot
        $locationPushed = $true
        Write-InfoMessage -Message "Installing Python packages with UV." -FunctionName $functionName
        & (Get-UVExecutable) sync
        if ($LASTEXITCODE -ne 0) {
            throw "uv sync exited with code $LASTEXITCODE."
        }
    }
    catch {
        Write-ErrorMessage -Message "Failed to sync the Python environment. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
    }
    finally {
        if ($locationPushed) {
            Pop-Location
        }
    }
}
