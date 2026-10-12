param (
    [switch]$Run
)

. "$PSScriptRoot\shared.ps1"

function Install-Package {
    $functionName = $MyInvocation.MyCommand.Name

    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $locationPushed = $false
    $toolkitName = "Python Toolkit"
    $installationComplete = $false

    try {
        Push-Location $workspaceRoot
        $locationPushed = $true
        $tomlFile = Get-TomlFile
        $toolkitName = Get-ToolkitName
        Write-InfoMessage -Message "Starting installation process for $toolkitName." -FunctionName $functionName

        Write-InfoMessage -Message "Preparing UV and its command-line tools." -FunctionName $functionName
        Install-UV

        Write-InfoMessage -Message "Syncing the Python environment from $tomlFile." -FunctionName $functionName
        Sync-PythonEnvironment

        Write-InfoMessage -Message "Registering the Jupyter kernel." -FunctionName $functionName
        Register-Kernel -KernelName $toolkitName
        $installationComplete = $true
    }
    catch {
        Write-ErrorMessage -Message "Installation failed for $toolkitName. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
    }
    finally {
        if ($locationPushed) {
            Pop-Location
        }
        if ($installationComplete) {
            Write-InfoMessage -Message "Installation process for $toolkitName completed successfully." -FunctionName $functionName
        }
        else {
            Write-WarningMessage -Message "Installation process for $toolkitName did not complete." -FunctionName $functionName
        }
    }
}

if ($Run -or $MyInvocation.InvocationName -ne '.') {
    Install-Package
}
