<#
.SYNOPSIS
    format.ps1
.DESCRIPTION
    A script that runs Ruff in order to apply formatting rules.
#>

ruff check generator --fix --unsafe-fixes
ruff format generator
