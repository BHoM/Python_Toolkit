param (
	[switch]$Serve,
	[ValidateRange(1, 65535)]
	[int]$Port = 8000
)

. "$PSScriptRoot\shared.ps1"

function Build-Documentation {
	param (
		[switch]$Serve,
		[int]$Port
	)

	$functionName = $MyInvocation.MyCommand.Name
	$workspaceRoot = Split-Path -Parent $PSScriptRoot
	$docsDirectory = Join-Path $workspaceRoot "docs"
	$configFile = Join-Path $docsDirectory "conf.py"
	$outputDirectory = Join-Path $docsDirectory "_build\html"
	$pythonExecutable = $null

	try {
		if (-not (Test-Path $configFile -PathType Leaf)) {
			throw "Sphinx configuration was not found at $configFile."
		}

		$pythonExecutable = Get-LocalPythonExecutable
		Write-InfoMessage -Message "Building HTML documentation using $configFile." -FunctionName $functionName
		& $pythonExecutable -m sphinx -b html -c $docsDirectory $docsDirectory $outputDirectory
		if ($LASTEXITCODE -ne 0) {
			throw "Sphinx build failed with exit code $LASTEXITCODE."
		}
		Write-InfoMessage -Message "Documentation was built at $outputDirectory." -FunctionName $functionName

		if ($Serve) {
			Write-InfoMessage -Message "Serving documentation at http://127.0.0.1:$Port/ (press Ctrl+C to stop)." -FunctionName $functionName
			& $pythonExecutable -m http.server $Port --bind 127.0.0.1 --directory $outputDirectory
			if ($LASTEXITCODE -ne 0) {
				throw "The documentation server exited with code $LASTEXITCODE."
			}
		}
	}
	catch {
		Write-ErrorMessage -Message "Documentation build or serve failed. $($_.Exception.Message)" -FunctionName $functionName -ThrowError
	}
}

if ($MyInvocation.InvocationName -ne '.') {
	Build-Documentation -Serve:$Serve -Port $Port
}
