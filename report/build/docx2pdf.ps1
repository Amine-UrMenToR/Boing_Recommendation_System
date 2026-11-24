<#
.SYNOPSIS
  Exports a .docx to PDF with Microsoft Word (COM) and prints the page count.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File docx2pdf.ps1 "report.docx" "report.pdf"

.NOTES
  - Opens the document read-only; the .docx is never changed.
  - Starts its own hidden Word. It always closes the document, quits that Word and releases COM, even on
    error. A watchdog stops that Word (and only that one) if the export hangs longer than -TimeoutSec.
  - If Word was already open and COM hands back that running instance, the script closes only its own
    document and leaves the person's Word open.
  - Exit code 0 on success, 1 on failure, 2 on bad arguments.
#>
param(
    [Parameter(Mandatory = $true, Position = 0)][string]$InDocx,
    [Parameter(Mandatory = $true, Position = 1)][string]$OutPdf,
    [int]$TimeoutSec = 300
)

$ErrorActionPreference = 'Stop'

function Get-FullPath([string]$p) {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($p)
}

function Get-WordPids {
    return @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
}

$inPath = Get-FullPath $InDocx
$outPath = Get-FullPath $OutPdf
if (-not (Test-Path -LiteralPath $inPath -PathType Leaf)) {
    [Console]::Error.WriteLine("docx2pdf: input not found: $inPath")
    exit 2
}
if ($outPath -notmatch '\.pdf$') {
    [Console]::Error.WriteLine("docx2pdf: the output must end in .pdf: $outPath")
    exit 2
}
$outDir = Split-Path -Parent $outPath
if (-not (Test-Path -LiteralPath $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
if (Test-Path -LiteralPath $outPath) { Remove-Item -LiteralPath $outPath -Force }

$before = Get-WordPids
$word = $null
$doc = $null
$ourPids = @()
$watchdog = $null
$exitCode = 0

try {
    $word = New-Object -ComObject Word.Application
    $ourPids = @(Get-WordPids | Where-Object { $before -notcontains $_ })

    if ($ourPids.Count -gt 0) {
        # Watchdog in a separate hidden process: if Word hangs (a hidden dialog, a damaged file), stop it.
        $ids = ($ourPids -join ',')
        $cmd = "Start-Sleep -Seconds $TimeoutSec; Stop-Process -Id $ids -Force -ErrorAction SilentlyContinue"
        $watchdog = Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -PassThru `
            -ArgumentList @('-NoProfile', '-NonInteractive', '-Command', $cmd)
    }

    $word.Visible = $false
    $word.DisplayAlerts = 0              # wdAlertsNone
    try { $word.Options.SaveNormalPrompt = $false } catch { }

    # Open(FileName, ConfirmConversions, ReadOnly, AddToRecentFiles)
    $doc = $word.Documents.Open($inPath, $false, $true, $false)
    $doc.Repaginate()

    # ExportAsFixedFormat(OutputFileName, ExportFormat=PDF(17), OpenAfterExport, OptimizeFor=Print(0),
    #   Range=AllDocument(0), From, To, Item=DocumentContent(0), IncludeDocProps, KeepIRM,
    #   CreateBookmarks=HeadingBookmarks(1), DocStructureTags, BitmapMissingFonts, UseISO19005_1)
    $doc.ExportAsFixedFormat($outPath, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)

    $pages = $doc.ComputeStatistics(2)    # wdStatisticPages
    Write-Output "pages: $pages"
    Write-Output "saved: $outPath"
}
catch {
    [Console]::Error.WriteLine("docx2pdf: export failed: $($_.Exception.Message)")
    $exitCode = 1
}
finally {
    if ($null -ne $doc) {
        try { $doc.Close(0) } catch { }                       # wdDoNotSaveChanges
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) } catch { }
        $doc = $null
    }
    if ($null -ne $word) {
        $attached = ($ourPids.Count -eq 0 -and $before.Count -gt 0)
        if (-not $attached) {
            try { $word.Quit(0) } catch { }
        }
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) } catch { }
        $word = $null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    [GC]::Collect()

    # Make sure the Word this script started is gone.
    foreach ($id in $ourPids) {
        $p = Get-Process -Id $id -ErrorAction SilentlyContinue
        if ($null -ne $p) {
            if (-not $p.WaitForExit(15000)) {
                Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
            }
        }
    }
    if ($null -ne $watchdog -and -not $watchdog.HasExited) {
        Stop-Process -Id $watchdog.Id -Force -ErrorAction SilentlyContinue
    }
}

if ($exitCode -eq 0 -and -not (Test-Path -LiteralPath $outPath)) {
    [Console]::Error.WriteLine("docx2pdf: Word reported success but no PDF was written: $outPath")
    $exitCode = 1
}
exit $exitCode
