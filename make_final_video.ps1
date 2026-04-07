param(
    [Parameter(Mandatory = $false)]
    [string]$RunDir,

    [Parameter(Mandatory = $false)]
    [string]$ClipsDir,

    [Parameter(Mandatory = $false)]
    [string]$AudioPath,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [string]$FfmpegPath = "ffmpeg"
)

$ErrorActionPreference = "Stop"

function Resolve-AbsolutePath([string]$PathValue) {
    if (-not $PathValue) {
        return $null
    }
    return (Resolve-Path -LiteralPath $PathValue).Path
}

if (-not $RunDir -and -not $ClipsDir) {
    throw "Provide -RunDir or -ClipsDir."
}

if ($RunDir) {
    $RunDir = Resolve-AbsolutePath $RunDir
    if (-not (Test-Path -LiteralPath $RunDir -PathType Container)) {
        throw "Run directory not found: $RunDir"
    }
    if (-not $ClipsDir) {
        $ClipsDir = Join-Path $RunDir "clips"
    }
    if (-not $OutputPath) {
        $OutputPath = Join-Path $RunDir "final_video_with_audio.mp4"
    }
}

if (-not $ClipsDir) {
    throw "Clips directory is required when -RunDir is not provided."
}

$ClipsDir = Resolve-AbsolutePath $ClipsDir
if (-not (Test-Path -LiteralPath $ClipsDir -PathType Container)) {
    throw "Clips directory not found: $ClipsDir"
}

if ($AudioPath) {
    $AudioPath = Resolve-AbsolutePath $AudioPath
    if (-not (Test-Path -LiteralPath $AudioPath -PathType Leaf)) {
        throw "Audio file not found: $AudioPath"
    }
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $ClipsDir "final_video_with_audio.mp4"
}

$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$OutputDir = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$manifestPath = if ($RunDir) { Join-Path $RunDir "clip_manifest.json" } else { $null }
$clipPaths = @()

if ($manifestPath -and (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $clipPaths = $manifest | Sort-Object shot_id | ForEach-Object { $_.local_clip_path }
} else {
    $clipPaths = Get-ChildItem -LiteralPath $ClipsDir -Filter "*.mp4" | Sort-Object Name | ForEach-Object { $_.FullName }
}

if (-not $clipPaths -or $clipPaths.Count -lt 1) {
    throw "No clips found to stitch in $ClipsDir"
}

$tempList = [System.IO.Path]::GetTempFileName()
$stitchedPath = Join-Path $OutputDir "stitched_no_audio.mp4"

try {
    $lines = $clipPaths | ForEach-Object {
        $path = [System.IO.Path]::GetFullPath($_)
        $escaped = $path.Replace("'", "'\\''")
        "file '$escaped'"
    }
    Set-Content -LiteralPath $tempList -Value $lines -Encoding UTF8

    & $FfmpegPath -y -f concat -safe 0 -i $tempList -c:v libx264 -pix_fmt yuv420p $stitchedPath

    if ($AudioPath) {
        & $FfmpegPath -y -i $stitchedPath -i $AudioPath -c:v copy -c:a aac -af apad -shortest $OutputPath
    } else {
        Move-Item -LiteralPath $stitchedPath -Destination $OutputPath -Force
    }

    Write-Host "Saved final video to $OutputPath"
}
finally {
    if (Test-Path -LiteralPath $tempList) {
        Remove-Item -LiteralPath $tempList -Force
    }
    if (Test-Path -LiteralPath $stitchedPath) {
        Remove-Item -LiteralPath $stitchedPath -Force
    }
}
