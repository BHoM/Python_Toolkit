
param (
    [switch]$Run,
    [switch]$IncludeSkipped
)
. "$PSScriptRoot\shared.ps1"

function Test-Code {
    param (
        [switch]$IncludeSkipped
    )

    $functionName = $MyInvocation.MyCommand.Name
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $previousSkipLongPytest = $env:SKIP_LONG_PYTEST
    $pushedLocation = $false

    try {
        Push-Location $workspaceRoot
        $pushedLocation = $true

        $pythonExecutable = Get-LocalPythonExecutable
        Write-InfoMessage -Message "Using Python executable: $pythonExecutable" -FunctionName $functionName

        if ($IncludeSkipped) {
            $env:SKIP_LONG_PYTEST = "1"
        }
        else {
            Remove-Item Env:SKIP_LONG_PYTEST -ErrorAction SilentlyContinue
        }

        & $pythonExecutable -m pytest
    }
    finally {
        if ($null -eq $previousSkipLongPytest) {
            Remove-Item Env:SKIP_LONG_PYTEST -ErrorAction SilentlyContinue
        }
        else {
            $env:SKIP_LONG_PYTEST = $previousSkipLongPytest
        }
        if ($pushedLocation) {
            Pop-Location
        }
    }
}

if ($Run -or $MyInvocation.InvocationName -ne '.') {
    Test-Code -IncludeSkipped:$IncludeSkipped
}
