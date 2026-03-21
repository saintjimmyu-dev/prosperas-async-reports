param(
    [Parameter(Mandatory = $false)]
    [string]$Owner = "saintjimmyu-dev",

    [Parameter(Mandatory = $false)]
    [string]$Repo = "prosperas-async-reports",

    [Parameter(Mandatory = $false)]
    [string]$Branch = "master",

    [Parameter(Mandatory = $false)]
    [ValidateSet("solo", "team")]
    [string]$Mode = "solo",

    [Parameter(Mandatory = $false)]
    [string]$RequiredCheck = "ci/lint-build",

    [Parameter(Mandatory = $false)]
    [string]$Token
)

$ErrorActionPreference = "Stop"

function Convert-SecureStringToPlainText {
    param([Security.SecureString]$SecureString)

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Invoke-GitHubApi {
    param(
        [string]$Method,
        [string]$Uri,
        [object]$Body = $null,
        [hashtable]$Headers
    )

    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
    }

    $jsonBody = $Body | ConvertTo-Json -Depth 12
    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -Body $jsonBody -ContentType "application/json"
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    $Token = $env:GH_PAT
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    Write-Host "No se encontro GH_PAT en el entorno."
    $secure = Read-Host "Ingresa tu GitHub PAT" -AsSecureString
    $Token = Convert-SecureStringToPlainText -SecureString $secure
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "No se proporciono un token valido."
}

$headers = @{
    Authorization         = "Bearer $Token"
    Accept                = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
    "User-Agent"         = "prosperas-security-script"
}

$repoApi = "https://api.github.com/repos/$Owner/$Repo"

Write-Host "[1/5] Activando Secret Scanning y Push Protection..."
$securityBody = @{
    security_and_analysis = @{
        secret_scanning                 = @{ status = "enabled" }
        secret_scanning_push_protection = @{ status = "enabled" }
    }
}
Invoke-GitHubApi -Method "PATCH" -Uri $repoApi -Body $securityBody -Headers $headers | Out-Null

Write-Host "[2/5] Activando Dependabot alerts (vulnerability alerts)..."
try {
    Invoke-RestMethod -Method "PUT" -Uri "$repoApi/vulnerability-alerts" -Headers $headers | Out-Null
}
catch {
    Write-Warning "No se pudo activar vulnerability alerts. Revisa si tu plan o permisos lo permiten."
}

Write-Host "[3/5] Activando automated security fixes..."
try {
    Invoke-RestMethod -Method "PUT" -Uri "$repoApi/automated-security-fixes" -Headers $headers | Out-Null
}
catch {
    Write-Warning "No se pudo activar automated security fixes. Revisa si tu plan o permisos lo permiten."
}

$reviewCount = 0
if ($Mode -eq "team") {
    $reviewCount = 1
}

Write-Host "[4/5] Configurando proteccion de rama $Branch en modo $Mode..."
$branchProtection = @{
    required_status_checks = @{
        strict   = $true
        contexts = @($RequiredCheck)
    }
    enforce_admins = $true
    required_pull_request_reviews = @{
        dismiss_stale_reviews           = $true
        require_code_owner_reviews      = $false
        required_approving_review_count = $reviewCount
        require_last_push_approval      = $false
    }
    restrictions = $null
    required_linear_history = $true
    allow_force_pushes = $false
    allow_deletions = $false
    block_creations = $false
    required_conversation_resolution = $true
    lock_branch = $false
    allow_fork_syncing = $false
}

Invoke-GitHubApi -Method "PUT" -Uri "$repoApi/branches/$Branch/protection" -Body $branchProtection -Headers $headers | Out-Null

Write-Host "[5/5] Verificando estado aplicado..."
$repoState = Invoke-GitHubApi -Method "GET" -Uri $repoApi -Headers $headers
$branchState = Invoke-GitHubApi -Method "GET" -Uri "$repoApi/branches/$Branch/protection" -Headers $headers

Write-Host ""
Write-Host "===== RESULTADO ====="
Write-Host ("Secret scanning: " + $repoState.security_and_analysis.secret_scanning.status)
Write-Host ("Push protection: " + $repoState.security_and_analysis.secret_scanning_push_protection.status)
Write-Host ("PR reviews required: " + [string]($branchState.required_pull_request_reviews -ne $null))
Write-Host ("Approvals required: " + $branchState.required_pull_request_reviews.required_approving_review_count)
Write-Host ("Status checks strict: " + $branchState.required_status_checks.strict)
Write-Host ("Required check: " + (($branchState.required_status_checks.contexts) -join ","))
Write-Host ("Enforce admins: " + $branchState.enforce_admins.enabled)
Write-Host ("Linear history: " + $branchState.required_linear_history.enabled)
Write-Host ("Conversation resolution: " + $branchState.required_conversation_resolution.enabled)
Write-Host ("Force push allowed: " + $branchState.allow_force_pushes.enabled)
Write-Host ("Delete branch allowed: " + $branchState.allow_deletions.enabled)
Write-Host "====================="
Write-Host ""
Write-Host "Sugerencia: revoca el PAT temporal al terminar."
