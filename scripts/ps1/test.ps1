<#
.SYNOPSIS
    test.ps1
.DESCRIPTION
    A script that runs pytest and generates a coverage repot
#>

coverage run --source=generator -m pytest -ssvv
coverage report --show-missing
coverage html --title "${@-coverage}"
