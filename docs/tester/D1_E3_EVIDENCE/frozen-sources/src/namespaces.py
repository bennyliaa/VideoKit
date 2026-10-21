"""Explicit source aliases and a separate create-new output namespace.

No import/construction opens an input or creates an output. Path checks inspect
metadata without resolving through a reparse point. They are preconditions, not
a claim of atomic protection against a hostile parent-directory replacement.
Opened-object identity remains separate from paths, length, mtime and hashes.
"""
from __future__ import annotations
import copy
import os
from pathlib import Path
import re
import stat
from gcore import BASE, Refused, need

_NAMES={'L':'L','L.bin':'L','C':'C','C.bin':'C','Z':'Z','Z.bin':'Z'}
_IDENTITY=re.compile(r'^[0-9]+:[0-9]+:[0-9]+$')


def lexical_absolute(path):
    """Normalize . and .. without following a link/junction to a new object."""
    value=Path(path)
    need(value.is_absolute(),'ABSOLUTE_NAMESPACE_PATH_REQUIRED')
    return Path(os.path.abspath(value))


def _key(path):return os.path.normcase(str(lexical_absolute(path)))


def check_ancestors(path,*,require_exists=False,inspector=None):
    """Check the final entry and every existing ancestor with no link following."""
    path=lexical_absolute(path);inspector=inspector or os.lstat;final=None
    for part in reversed((path,*path.parents)):
        try:entry=inspector(part)
        except FileNotFoundError:
            if require_exists:raise Refused('NAMESPACE_PATH_MISSING')
            continue
        except OSError as error:raise Refused('NAMESPACE_METADATA_UNPROVEN') from error
        need(not stat.S_ISLNK(entry.st_mode) and not(getattr(entry,'st_file_attributes',0)&0x400),'REPARSE_NAMESPACE_DENIED')
        if part!=path:need(stat.S_ISDIR(entry.st_mode),'NAMESPACE_ANCESTOR_NOT_DIRECTORY')
        else:final=entry
    if require_exists:need(final is not None,'NAMESPACE_PATH_MISSING')
    return final


class Namespaces:
    """A resolver/identity gate, never an execution authorization capability.

    The actual output open must still use CREATE_NEW (or O_CREAT|O_EXCL), and the
    actual source open must use read-only OPEN_EXISTING/share READ. Post-open
    identity failure retains that allocated object for the caller's close path.
    """
    def __init__(self,output_root,input_aliases=None,mode='SYNTHETIC',allowed_output_parent=None):
        need(mode in ('SYNTHETIC','CANDIDATE_IO'),'NAMESPACE_MODE_UNSUPPORTED')
        self.root=lexical_absolute(output_root);self.mode=mode;self.input_identities={};self.input_proofs={}
        package_parent=lexical_absolute(BASE/('selfcheck' if mode=='SYNTHETIC' else 'runs'))
        parent=lexical_absolute(allowed_output_parent or package_parent)
        need(parent==package_parent or parent.is_relative_to(package_parent),'OUTPUT_NAMESPACE_ROOT_DENIED')
        need(self.root!=parent and self.root.is_relative_to(parent),'OUTPUT_NAMESPACE_ROOT_DENIED')
        entry=check_ancestors(self.root,require_exists=True);need(stat.S_ISDIR(entry.st_mode),'OUTPUT_ROOT_NOT_DIRECTORY')
        aliases=input_aliases if input_aliases is not None else {name:self.root/(name+'.bin') for name in ('L','C','Z')}
        need(isinstance(aliases,dict) and set(aliases) in ({'L','C','Z'},{'L.bin','C.bin','Z.bin'}),'INPUT_ALIAS_SET_REQUIRED')
        self.inputs={}
        for name,value in aliases.items():
            alias=self.alias(name)
            path=value.get('path',value.get('absolutePath')) if isinstance(value,dict) else value
            path=lexical_absolute(path);self.inputs[alias]=path
            need(not str(path).startswith('\\\\'),'LOCAL_INPUT_NAMESPACE_REQUIRED')
            # This is only namespace separation. It does not inspect an original
            # media path until an explicitly requested input_path(alias) call.
            if mode=='CANDIDATE_IO':need(not path.is_relative_to(self.root),'INPUT_INSIDE_OUTPUT_NAMESPACE')
            else:need(path.is_relative_to(lexical_absolute(BASE/'selfcheck')),'SYNTHETIC_INPUT_NAMESPACE_DENIED')
        if mode=='CANDIDATE_IO':
            from profile_bindings import REAL_INPUTS
            need(set(self.inputs)==set(REAL_INPUTS) and all(_key(self.inputs[key])==_key(REAL_INPUTS[key]) for key in self.inputs),'EXACT_R2_INPUT_PATHS_REQUIRED')
    @staticmethod
    def alias(name):need(name in _NAMES,'INPUT_ALIAS_UNKNOWN');return _NAMES[name]
    def input_path(self,name):
        alias=self.alias(name);path=self.inputs[alias];entry=check_ancestors(path,require_exists=True)
        need(stat.S_ISREG(entry.st_mode),'INPUT_NOT_REGULAR_FILE');return path
    def output_path(self,name,*,create=True):
        need(isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,64}',name) and '..' not in name,'OUTPUT_NAME_DENIED')
        need(name.casefold() not in {value.casefold() for value in _NAMES},'INPUT_ALIAS')
        path=self.root/name
        need(all(_key(path)!=_key(source) for source in self.inputs.values()),'INPUT_ALIAS')
        entry=check_ancestors(path,require_exists=not create)
        if create:need(entry is None,'OUTPUT_ALREADY_EXISTS_CREATE_NEW_REQUIRED')
        else:need(stat.S_ISREG(entry.st_mode),'OUTPUT_NOT_REGULAR_FILE')
        return path
    @staticmethod
    def _proof(proof):
        need(isinstance(proof,dict) and proof.get('identityStatus')=='OPENED_HANDLE_PROVEN','OPENED_IDENTITY_UNPROVEN')
        identity=proof.get('identity');need(isinstance(identity,str) and _IDENTITY.fullmatch(identity),'OPENED_IDENTITY_INVALID')
        return identity
    def bind_input(self,name,proof):
        alias=self.alias(name);identity=self._proof(proof)
        previous=self.input_identities.get(alias)
        need(previous is None or previous==identity,'SOURCE_VERSION_IDENTITY_CHANGED')
        self.input_identities[alias]=identity;self.input_proofs[alias]=copy.deepcopy(proof);return identity
    def reject_input_identity(self,proof):
        identity=self._proof(proof)
        need(identity not in self.input_identities.values(),'INPUT_ALIAS');return identity
    def facts(self):
        return dict(scope='NAMESPACE_AND_OPENED_IDENTITY_GATE',mode=self.mode,executionAuthorized=False,
                    inputAliases=sorted(self.inputs),boundInputAliases=sorted(self.input_identities),outputCreatePolicy='CREATE_NEW_ONLY',
                    sourceOpenPolicy='READ_ONLY_OPEN_EXISTING_SHARE_READ',pathHashIsVersion=False,
                    atomicNamespaceReplacementProtection=False,rawHandlesExported=False)
