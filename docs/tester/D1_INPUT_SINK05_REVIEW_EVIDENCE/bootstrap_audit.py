from pathlib import Path
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent
s=(R/'docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/audit_frozen.py').read_text()
s=s.replace('d1input-sink04','d1input-sink05').replace('D1_INPUT_SINK04','D1_INPUT_SINK05').replace('input-sink04','input-sink05').replace("OLD=R/'docs/coder/d1input-sink03'","OLD=R/'docs/coder/d1input-sink04'")
for a,b in [('7a71b68959de3480a8f3d3a1d326fe6994cc843377398845f033956ba1e21650','ec7e5e9a8f38d2d1fe531592117f5db0a6d3481cd3ff89536d985f9dae173d96'),('0d062ee1ebf693b92a4206a5412a18aef491016e6f1cce820a91417f28c77e55','25503fe0f72310db4b22eeb23875fbdc17f782092ebd4e0bf132baf2fb3f82a7'),('8fe78bf542f1bbb2671aa35778fc555157c1c7a8e733bf70512a0660f142c231','b387471995c555628baee54e0f56a3affd1782b36da2f6de1fd3425aa08fa5ab'),('24c6fdbed294771268a103200b19e5a3a8a099002d16dc392fe8d86f8c2d305b','0b5fc8d530c8159c9283d670472255b883d97ad3885e2bae8fd427d25c1148b7'),('f241f2f256f261f696f1713b164d17f6ffe68a692e2cf3702acf9eb881ce2e95','6fbf307a4f0a06f45606ad9a162fcad95330924c2f220b5f68cec1e851916b0b'),('==704','==827'),('2978','3683'),("['versionCode']==4","['versionCode']==5"),(",'src/com/videokit/d1input/Failures.java'",'')]:s=s.replace(a,b)
(E/'audit_frozen.py').write_text(s,encoding='utf8')
g=(R/'docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/check_output_gates.py').read_text().replace('sink04','sink05').replace('SINK04','SINK05').replace('SINK03_REVIEW_EVIDENCE','SINK04_REVIEW_EVIDENCE')
(E/'check_output_gates.py').write_text(g,encoding='utf8')
