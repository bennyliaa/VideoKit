"""Build passive PS code from frozen diagnostic, replacing its non-production end."""
from pathlib import Path
B=Path(__file__).resolve().parents[1]
s=(B.parent/'d1android02-global-idle-semantics01/tools/global_idle_semantics.ps1').read_text(encoding='utf-8')
s=s.replace('# Pure text review candidate. No IO, package query, SDK, or OEM-name inference.', '# Bounded API31 parser. No IO/query. Qualification is an immutable permit input.')
s=s.replace('([string]$Text,[string[]]$AllowedPackages)', '([string]$Text,$Qualification,$Context)')
s=s.replace("schema='GLOBAL_IDLE_DIAGNOSTIC_V2';qualified=$false;productionPassCapable=$false", "schema='GLOBAL_IDLE_CONTRACT02_V1';qualified=$false;productionPassCapable=$true")
s=s.replace("api31NumericEnum='FIXED_TAG_NUMERIC_TABLE_NOT_RETRIEVED'", "api31NumericEnum='343c60effa4ce83ce42296527bae8bd4341a9da942a670a83b1c86a7ef307881'")
s=s.replace("$stateValue -gt 2147483647", "$stateValue -gt 19")
s=s.replace("  $stateValue=[long]0", "  if($states.Count -ne [regex]::Matches($body,'(?m)^    curProcState=').Count -or $users.Count -ne [regex]::Matches($body,'(?m)^    user #').Count -or $packages.Count -ne [regex]::Matches($body,'(?m)^    packageList=').Count){$d.reason='GLOBAL_OWN_FIELD_FORMAT_UNPROVEN';return $d}\n  $stateValue=[long]0")
s=s.replace("$stop=if($i+1 -lt $headers.Count){$headers[$i+1].Index}else{$proc.Length}", "$stop=if($i+1 -lt $headers.Count){$headers[$i+1].Index}else{$tail=[regex]::Match($proc.Substring($h.Index+$h.Length),'(?m)^  (?:Process OOM control|UID states|UID validation|Process LRU list|Total persistent processes):?');if($tail.Success){$h.Index+$h.Length+$tail.Index}else{$proc.Length}}")
s=s.replace("if($packages.Count -ne 1 -or $pkg.Count -eq 0", "if($packages.Count -ne 1 -or $pkg.Count -ne @($pkg|Sort-Object -Unique -CaseSensitive).Count -or $pkg.Count -eq 0")
start=s.index(' foreach($r in $records){\n  if($r.isolatedOwnerUnproven)')
end=s.index(" $d.stage='resume'",start)
s=s[:start]+s[end:]
s=s.replace(" foreach($r in $resumes){if($r.user -ne 0 -or $r.package -cnotin @($AllowedPackages)){$d.reason='ENV_WAIT_NONALLOWLIST_OR_OTHER_USER_RESUMED';return $d}}",'')
start=s.index(' # This batch has no admitted')
end=s.index('\n }catch',start)
s=s[:start]+r'''
 # One admitted display section, bound to the unique resumed/focused record.
 $displays=[regex]::Matches($activities,'(?m)^Display #(\d+) \(activities from top to bottom\):\r*$')
 if($displays.Count -ne 1 -or $displays.Count -ne [regex]::Matches($activities,'(?m)^Display #').Count -or $displays[0].Groups[1].Value -cne '0' -or $activities -cmatch '(?m)\b(?:mDisplayId|displayId)=[1-9][0-9]*\b'){$d.reason='GLOBAL_DISPLAY_UNPROVEN';return $d}
 if($focus.Count -ne 1){$d.reason='GLOBAL_FOCUS_UNPROVEN';return $d}
 try{$q=GIQualification $Qualification $Context}catch{$d.reason=$_.Exception.Message;return $d}
 $rawBytes=[Text.UTF8Encoding]::new($false,$true).GetBytes($Text)
 if($Context.rawSha256 -cne [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($rawBytes)).ToLowerInvariant() -or $Context.rawBytes -ne $rawBytes.Length){$d.reason='GLOBAL_RAW_BINDING';return $d}
 $homeIdentity=$q.home;$r=$resumes[0];$component=if($r.activity.StartsWith('.')){$r.package+$r.activity}else{$r.activity}
 if($r.user -ne $homeIdentity.user -or $r.package -cne $homeIdentity.package){$d.reason='ENV_WAIT_FOREIGN_RESUMED';$d.status='BLOCKED_OCCUPIED';return $d}
 if($component -cne $homeIdentity.component){$d.reason='GLOBAL_HOME_COMPONENT_UNPROVEN';return $d}
 $homeProcesses=@($records|Where-Object {$_.processName -ceq $homeIdentity.process -and $_.uid -eq $homeIdentity.uid -and $_.user -eq $homeIdentity.user -and $_.packages.Count -eq 1 -and $_.packages[0] -ceq $homeIdentity.package})
 if($homeProcesses.Count -ne 1 -or $homeProcesses[0].state -ne 2){$d.reason='GLOBAL_HOME_PROCESS_STATE_UNPROVEN';return $d}
 $hist=[regex]::Matches($activities,'(?m)^      \* Hist #[0-9]+: ActivityRecord\{(?<token>[A-Za-z0-9]+) u(?<user>[0-9]+) (?<package>[A-Za-z0-9_.]+)/(?<activity>[^\s}]+) (?<task>t[0-9]+)[^}\r\n]*\}')
 if($hist.Count -ne 1 -or [regex]::Matches($activities,'(?m)^      \* Hist #').Count -ne 1){$d.reason='GLOBAL_HOME_ACTIVITY_DETAIL_UNPROVEN';return $d}
 foreach($k in @('token','user','package','activity','task')){if($hist[0].Groups[$k].Value -cne [string]$resumes[0].$k){$d.reason='GLOBAL_HOME_ACTIVITY_IDENTITY_UNPROVEN';return $d}}
 $detail=$activities.Substring($hist[0].Index+$hist[0].Length)
 $detailStop=[regex]::Match($detail,'(?m)^(?:      \* Hist #|    \* Task\{|  RootTask #|  Display:|Display #)');if($detailStop.Success){$detail=$detail.Substring(0,$detailStop.Index)}
 $apps=[regex]::Matches($detail,'(?m)^          app=ProcessRecord\{(?<token>[A-Za-z0-9]+) (?<pid>[0-9]+):(?<process>[^\s/}]+)/(?<user>[^\s}]+)\}\r*$')
 $owners=[regex]::Matches($detail,'(?m)^          packageName=(?<package>\S+) processName=(?<process>\S+)\r*$')
 $components=[regex]::Matches($detail,'(?m)^          mActivityComponent=(?<component>\S+)\r*$')
 if($apps.Count -ne 1 -or $owners.Count -ne 1 -or $components.Count -ne 1 -or [regex]::Matches($detail,'(?m)^          app=').Count -ne 1 -or [regex]::Matches($detail,'(?m)^          state=').Count -ne 1 -or $detail -cnotmatch '(?m)^          state=RESUMED stopped=false delayedResume=false finishing=false(?:\s|$)' -or $detail -cnotmatch '(?m)^          mVisibleRequested=true mVisible=true(?:\s|$)'){$d.reason='GLOBAL_HOME_ACTIVITY_OWNER_UNPROVEN';return $d}
 $hp=$homeProcesses[0];$a=$apps[0]
 $hc=$components[0].Groups['component'].Value.Split('/');if($hc.Count -ne 2){$d.reason='GLOBAL_HOME_ACTIVITY_COMPONENT_UNPROVEN';return $d}
 $fullComponent=if($hc[1].StartsWith('.')){$hc[0]+$hc[1]}else{$hc[1]}
 if($a.Groups['token'].Value -cne $hp.token -or $a.Groups['pid'].Value -cne [string]$hp.pidFromText -or $a.Groups['process'].Value -cne $hp.processName -or $a.Groups['user'].Value -cne $hp.userSpec -or $owners[0].Groups['package'].Value -cne $homeIdentity.package -or $owners[0].Groups['process'].Value -cne $homeIdentity.process -or $hc[0] -cne $homeIdentity.package -or $fullComponent -cne $homeIdentity.component){$d.reason='GLOBAL_HOME_ACTIVITY_PROCESS_BINDING';return $d}
 foreach($r in $records){
  $d.firstRejectedRecord=$r
  if($r.isolatedOwnerUnproven){$d.reason='GLOBAL_ISOLATED_OWNER_UNPROVEN';return $d}
  if($r.packages.Count -ne 1){$d.reason='GLOBAL_SHARED_OWNER_UNPROVEN';return $d}
  if($r.user -ne 0){$d.reason='GLOBAL_OTHER_USER_UNPROVEN';return $d}
  # Package/process mapping is complete, never a suffix-derived identity.
  # Nonstandard system process names require the exact reviewed service entry.
  $services=@($q.services|Where-Object {$_.process -ceq $r.processName -and $_.uid -eq $r.uid -and $_.user -eq $r.user -and $_.kind -ceq $r.kind -and $_.state -eq $r.state -and $_.packages[0] -ceq $r.packages[0]})
  $base=$r.processName.Split(':')[0]
  if($base -cne $r.packages[0] -and $services.Count -ne 1){$d.reason='GLOBAL_PROCESS_PACKAGE_MAPPING_UNPROVEN';return $d}
  if($r.token -ceq $homeProcesses[0].token){continue}
  if($r.state -le 6){
   if($r.state -cin @(2,3)){$d.reason='ENV_WAIT_FOREIGN_FOREGROUND';$d.status='BLOCKED_OCCUPIED';return $d}
   if($services.Count -ne 1){$d.reason=if($r.appId -ge 10000){'ENV_WAIT_ACTIVE_SERVICE_UNQUALIFIED'}else{'GLOBAL_CORE_SERVICE_UNPROVEN'};$d.status=if($r.appId -ge 10000){'BLOCKED_OCCUPIED'}else{'BLOCKED_UNPROVEN'};return $d}
  }elseif($r.state -cin @(9,11,12)){$d.reason='ENV_WAIT_CONTENDING_OPERATION';$d.status='BLOCKED_OCCUPIED';return $d}
 }
 $d.firstRejectedRecord=$null;$d.qualified=$true;$d.status='PASS';$d.reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY';$d.stage='qualified';$d.systemPackageFacts='BOUND_NARROW_POLICY';$d.defaultHomeFacts='BOUND_ROLE_COMPONENT_UID';$d.captureQualification='BODY_RETURNED_OUTER_CONTROLLER_RETURN_STILL_REQUIRED';return $d''' +s[end:]
# Never hide malformed mInstr=nullSuffix, whitespace, or unsupported labels.
needle=" $proc=$Text.Substring"
s=s.replace(needle," if($Text -cmatch '(?m)^\\s*mInstr=(?!null[ \\t]*\\r*$)' -or $Text -cmatch '(?m)^\\s*Instrumentation #(?![0-9]+:)'){$d.reason='GLOBAL_INSTRUMENTATION_FORMAT_UNPROVEN';return $d}\n"+needle)
# CONTRACT03: inventory suspicious records independently of admitted headers.
s=s.replace(r"(?m)^[ \t]*\*(?<kind>APP|PERS)", r"(?m)^  \*(?<kind>APP|PERS)")
old=" $anyHeaders=[regex]::Matches($proc,'(?m)^[ \\t]*\\*[^*\\r\\n]+\\*[ \\t]+UID ')"
new=r""" $suspects=[Collections.Generic.HashSet[int]]::new()
 $summary=[regex]::Match($proc,'(?m)^  (?:Process OOM control|UID states|UID validation|Process LRU list|Total persistent processes):?')
 $recordArea=if($summary.Success){$proc.Substring(0,$summary.Index)}else{$proc}
 foreach($m in [regex]::Matches($proc,'(?m)^[ \t]*\*[^\r\n]*(?:\*|ProcessRecord\{)[^\r\n]*\r*$')){[void]$suspects.Add($m.Index)}
 foreach($m in [regex]::Matches($recordArea,'(?m)^[ \t]{0,2}(?=[^ \t\r\n])(?=[^\r\n]*ProcessRecord\{)[^\r\n]+\r*$')){[void]$suspects.Add($m.Index)}
 foreach($m in [regex]::Matches($proc,'(?m)^[ \t]{0,2}(?:(?i:UID)[^\r\n]*ProcessRecord\{|ProcessRecord\{)[^\r\n]*\r*$')){[void]$suspects.Add($m.Index)}
 foreach($h in $headers){if(-not $suspects.Contains($h.Index) -or ($summary.Success -and $h.Index -ge $summary.Index)){$d.reason='GLOBAL_PROCESS_HEADERS_UNPROVEN';return $d}}
 $prefixStop=if($headers.Count -gt 0){$headers[0].Index}else{$proc.Length}
 if($proc.Substring(0,$prefixStop) -cmatch '(?m)^    (?:user #|packageList=|curProcState=)'){$d.reason='GLOBAL_PROCESS_HEADERS_UNPROVEN';return $d}
 $anyHeaders=$suspects"""
assert old in s
s=s.replace(old,new).replace("$headers.Count -ne $anyHeaders.Count","$headers.Count -ne $anyHeaders.Count")
s=s.replace("curProcState=(\\d+)\\b", "curProcState=([0-9][^ \\t\\r\\n]*)(?=[ \\t\\r\\n]|$)")
s=s.replace("if($states.Count -ne 1 -or -not [long]::TryParse", "if($states.Count -ne 1 -or $states[0].Groups[1].Value -cnotmatch '^(?:0|[1-9][0-9]?)$' -or [regex]::IsMatch($body,'(?m)^    curProcState=[^\\r\\n]*\\bcurProcState=') -or -not [long]::TryParse")
(B/'tools/semantics.ps1.txt').write_text(s,encoding='utf-8',newline='\n')
