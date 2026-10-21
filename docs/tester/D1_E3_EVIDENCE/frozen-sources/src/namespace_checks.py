"""Explicitly invoked checks over newly created non-media files only."""
from __future__ import annotations
import os
from pathlib import Path
import stat
from types import SimpleNamespace
from gcore import BASE, Refused, need
from namespaces import Namespaces, check_ancestors, lexical_absolute


def run_checks(root):
    root=lexical_absolute(root);need(root.is_relative_to((BASE/'selfcheck').absolute()),'SELF_CREATED_NAMESPACE_CHECK_ROOT_ONLY')
    root.mkdir(parents=True,exist_ok=False);source=root/'inputs';output=root/'outputs';source.mkdir();output.mkdir()
    checks=[];limitations=[]
    def check(ok,label):need(ok,'NAMESPACE_CHECK:'+label);checks.append(label)
    def rejects(action,reason,label):
        try:action()
        except Refused as error:check(str(error)==reason,label);return
        raise Refused('NAMESPACE_EXPECTED_REJECTION:'+label)
    paths={name:source/(name+'.bin') for name in ('L','C','Z')}
    for name,data in (('L',b'namespace-L-not-media'*3),('C',b'namespace-C-not-media'),('Z',b'')):
        with open(paths[name],'xb',buffering=0) as file:check(file.write(data)==len(data),'single-fixture-write-'+name)
    before={name:(path.stat().st_size,path.stat().st_mtime_ns) for name,path in paths.items()}
    ns=Namespaces(output,paths,mode='SYNTHETIC')
    for name in ('L','C','Z'):check(ns.input_path(name)==paths[name] and ns.input_path(name+'.bin')==paths[name],'exact-input-alias-'+name)
    rejects(lambda:ns.input_path('other.bin'),'INPUT_ALIAS_UNKNOWN','unknown-input-alias-no-open')
    rejects(lambda:ns.output_path('C.bin'),'INPUT_ALIAS','input-name-cannot-be-output')
    for name in ('../escape.out','a/b.out','a\\b.out','a:stream.out','..',''):
        rejects(lambda name=name:ns.output_path(name),'OUTPUT_NAME_DENIED','unsafe-output-name-'+repr(name))
    check(ns.output_path('T01.out')==output/'T01.out' and not (output/'T01.out').exists(),'output-preflight-does-not-touch-file')
    destination=ns.output_path('T01.out');fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    os.close(fd)
    rejects(lambda:ns.output_path('T01.out'),'OUTPUT_ALREADY_EXISTS_CREATE_NEW_REQUIRED','existing-output-not-replaced')
    check(ns.output_path('T01.out',create=False)==destination,'existing-validator-path-read-only-resolution')
    missing=output/'missing.out'
    rejects(lambda:ns.output_path(missing.name,create=False),'NAMESPACE_PATH_MISSING','validator-does-not-create-missing-output')
    # A real hardlink has another path but the same opened file object. fstat is
    # called on each retained self-created test FD; no input bytes are read.
    hardlink=output/'linked.out';hardlink_available=False
    try:os.link(paths['C'],hardlink);hardlink_available=True
    except OSError as error:
        limitations.append('ACTUAL_HARDLINK_NOT_CREATED:'+type(error).__name__+':'+str(getattr(error,'winerror',None)))
    def opened_proof(fd):
        value=os.fstat(fd)
        return dict(identity=f'{value.st_dev}:{value.st_ino>>32}:{value.st_ino&0xffffffff}',identityStatus='OPENED_HANDLE_PROVEN',
                    length=value.st_size,identityBackend='PYTHON_FSTAT_SELF_CREATED_CHECK_ONLY')
    left=os.open(paths['C'],os.O_RDONLY);right=os.open(hardlink if hardlink_available else paths['C'],os.O_RDONLY)
    try:
        a=opened_proof(left);b=opened_proof(right);check(a['identity']==b['identity'],'two-original-open-handles-same-physical-identity')
        ns.bind_input('C',a)
        rejects(lambda:ns.reject_input_identity(b),'INPUT_ALIAS','same-physical-input-refused-by-opened-proof')
        rejects(lambda:ns.bind_input('C',dict(a,identity='999:999:999')),'SOURCE_VERSION_IDENTITY_CHANGED','input-identity-never-silently-rebound')
    finally:os.close(right);os.close(left)
    if hardlink_available:rejects(lambda:ns.output_path(hardlink.name),'OUTPUT_ALREADY_EXISTS_CREATE_NEW_REQUIRED','hardlink-never-opened-for-write-or-truncate')
    rejects(lambda:ns.bind_input('L',{'identity':'same-hash','identityStatus':'OPENED_HANDLE_PROVEN'}),'OPENED_IDENTITY_INVALID','hash-or-path-not-physical-identity')
    rejects(lambda:ns.bind_input('L',{'identity':'1:2:3','identityStatus':'PATH_ATTRIBUTES_ONLY'}),'OPENED_IDENTITY_UNPROVEN','path-attributes-not-opened-proof')
    rejects(lambda:ns.reject_input_identity({'identity':'1:2:3'}),'OPENED_IDENTITY_UNPROVEN','missing-opened-proof-stops-output')
    fake_parent=source
    def reparse_inspector(path):
        if path==fake_parent:return SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=0x400)
        return os.lstat(path)
    rejects(lambda:check_ancestors(paths['C'],require_exists=True,inspector=reparse_inspector),'REPARSE_NAMESPACE_DENIED','ancestor-reparse-bit-rejected-before-final-entry')
    link=root/'source-link'
    try:os.symlink(source,link,target_is_directory=True)
    except OSError as error:limitations.append('OS_SYMLINK_CREATION_NOT_AVAILABLE:'+type(error).__name__)
    else:rejects(lambda:check_ancestors(link/'C.bin',require_exists=True),'REPARSE_NAMESPACE_DENIED','actual-self-created-ancestor-link-rejected')
    rejects(lambda:Namespaces(root/'outside'/'out',paths,allowed_output_parent=output),'OUTPUT_NAMESPACE_ROOT_DENIED','output-root-outside-explicit-parent-refused')
    rejects(lambda:Namespaces(output,{'L':paths['L'],'C':paths['C']}),'INPUT_ALIAS_SET_REQUIRED','missing-alias-map-refused')
    # Candidate mode is confined to the package's separate runs tree. It grants
    # no authority to create that tree or start a real experiment.
    rejects(lambda:Namespaces(output,paths,mode='CANDIDATE_IO'),'OUTPUT_NAMESPACE_ROOT_DENIED','candidate-output-cannot-use-selfcheck-tree')
    rejects(lambda:Namespaces(output,dict(paths,C=BASE/'outside-synthetic.bin')),'SYNTHETIC_INPUT_NAMESPACE_DENIED','synthetic-bindings-cannot-point-outside-selfcheck')
    after={name:(path.stat().st_size,path.stat().st_mtime_ns) for name,path in paths.items()}
    check(before==after,'inputs-not-written-truncated-or-replaced')
    check(not ns.facts()['executionAuthorized'] and not ns.facts()['atomicNamespaceReplacementProtection'],'namespace-resolver-does-not-authorize-execution-or-claim-atomic-race-safety')
    fixture_bytes=sum(path.stat().st_size for path in root.rglob('*') if path.is_file() and not path.is_symlink())
    check(fixture_bytes<=4096,'small-non-media-fixtures-bounded')
    return dict(scope='SELF_CREATED_NON_MEDIA_NAMESPACE_CHECKS',status='PASS',assertions=len(checks),checks=checks,
                fixtureBytes=fixture_bytes,mediaBytesRead=0,newHelpers=0,physicalIdentityProof='Opened Python test FD fstat only; not Java/Win32 bridge validation.',
                limitations=limitations+['Ancestor precheck is not atomic against directory replacement; CREATE_NEW and post-open identity remain required.'])
