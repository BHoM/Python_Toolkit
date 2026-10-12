
param (
    [switch]$Run,
    [switch]$IncludeSkipped
)
. "$PSScriptRoot\shared.ps1"

function Format-PythonFiles {
    param (
        [switch]$IncludeSkipped
    )

    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $pushedLocation = $false

    try {
        Push-Location $workspaceRoot
        $pushedLocation = $true
        
        Write-InfoMessage -Message "Formatting Python files in ./src" -FunctionName $MyInvocation.MyCommand.Name
        & uv run ruff format ./src
        Write-InfoMessage -Message "Formatting Python files in ./tests" -FunctionName $MyInvocation.MyCommand.Name
        & uv run ruff format ./tests

    }
    finally {
        if ($pushedLocation) {
            Pop-Location
        }
    }
}

if ($Run -or $MyInvocation.InvocationName -ne '.') {
    Format-PythonFiles
}
