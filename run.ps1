# PowerShell launcher for Animated Cursor Buddy
param (
    [switch]$Settings,
    [switch]$Test
)

$argsList = @()
if ($Settings) { $argsList += "--settings" }
if ($Test) { $argsList += "--test" }

python "$PSScriptRoot\main.py" @argsList
