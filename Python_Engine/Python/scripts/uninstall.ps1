param (
    [switch]$Run
)

. "$PSScriptRoot\shared.ps1"

function Uninstall-Package {
    $functionName = $MyInvocation.MyCommand.Name
    
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    $locationPushed = $false
    $toolkitName = "Python Toolkit"
    $uninstallationComplete = $false

    try {
        Push-Location $workspaceRoot
        $locationPushed = $true
        $toolkitName = Get-ToolkitName

        $userInput = Read-UserInput -Message "Do you really want to uninstall the $toolkitName Python package? (y/n): "
        if ($userInput -ne "y") {
            Write-InfoMessage -Message "Uninstallation aborted by the user." -FunctionName $functionName
            return
        }

        Write-InfoMessage -Message "Removing the Jupyter kernel." -FunctionName $functionName
        Unregister-Kernel -KernelName $toolkitName

        Write-InfoMessage -Message "Removing the project virtual environment." -FunctionName $functionName
        Remove-PathIfExists -Path (Join-Path $workspaceRoot ".venv") -Description "the $toolkitName virtual environment" -FunctionName $functionName
        $uninstallationComplete = $true
    }
    catch {
        Write-ErrorMessage -Message "Uninstallation failed for $toolkitName. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
    }
    finally {
        if ($locationPushed) {
            Pop-Location
        }
        if ($uninstallationComplete) {
            Write-InfoMessage -Message "Uninstallation process for $toolkitName completed successfully." -FunctionName $functionName
        }
        elseif ($userInput -eq "y") {
            Write-WarningMessage -Message "Uninstallation process for $toolkitName did not complete." -FunctionName $functionName
        }
    }
}

if ($Run -or $MyInvocation.InvocationName -ne '.') {
    Uninstall-Package
}
