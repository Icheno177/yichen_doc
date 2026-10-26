param(
  [Parameter(Mandatory=$true)][string]$InputPptx,
  [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$resolvedInput = (Resolve-Path -LiteralPath $InputPptx).Path
$resolvedOut = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $resolvedOut -Force | Out-Null
$app = New-Object -ComObject PowerPoint.Application
try {
  $deck = $app.Presentations.Open($resolvedInput, $true, $false, $false)
  foreach ($slide in $deck.Slides) {
    $slide.Export((Join-Path $resolvedOut ('slide-{0:D3}.png' -f $slide.SlideIndex)), 'PNG', 1600, 900)
  }
  $count = $deck.Slides.Count
  $deck.Close()
  Write-Output "Rendered $count slides to $resolvedOut"
} finally {
  $app.Quit()
}
