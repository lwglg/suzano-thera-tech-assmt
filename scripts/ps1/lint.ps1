<#
.SYNOPSIS
    lint.ps1
.DESCRIPTION
    A script that checks formatting and runs type system analysis with Mypy.
#>

mypy generator
ruff check generator
ruff format generator --check
