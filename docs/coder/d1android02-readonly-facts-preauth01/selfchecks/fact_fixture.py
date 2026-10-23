"""Frozen synthetic bytes only; never SDK/device evidence."""
import sys
if sys.argv[1:]!=['COMPLETE']:raise SystemExit('EXACT_FIXTURE_ONLY')
sys.stdout.buffer.write(b'GI_FACTS_V1\nGI_ITEM|model|0|1000|1000|8\nTB138FC\n\nGI_ITEM|api|0|1000|1000|3\n31\n\nGI_ITEM|firmware|0|1000|1000|33\nSYNTHETIC_FIXTURE_FIRMWARE_API31\n\nGI_ITEM|user|0|1000|1000|2\n0\n\nGI_ITEM|system|0|1000|1000|35\npackage:com.zui.launcher uid:10012\n\nGI_ITEM|role|0|1000|1000|192\nROLE STATE (dumpsys role):\n{\n  user_states={\n    user_id=0\n    version=1\n    packages_hash=FIXTURE_HASH\n    roles={\n      name=android.app.role.HOME\n      holders=com.zui.launcher\n    }\n  }\n}\n\nGI_ITEM|home|0|1000|1000|27\ncom.zui.launcher/.Launcher\n\nGI_FACTS_END\n')
