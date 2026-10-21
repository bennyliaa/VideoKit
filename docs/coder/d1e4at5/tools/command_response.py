"""Complete original response gate; explicit ADB features token separators, no substring admission."""
import hashlib
import re

EMPTY_SHA=hashlib.sha256(b'').hexdigest()

def complete_stdout(result):
    if (result['status']!='PROCESS_IO_COMPLETE_ONLY' or result['ownership']!='RETURNED'
        or result['originalExitCode']!=0 or not result['originalExitObserved']
        or result['firstError'] is not None or result['errors'] or result['creationUnknown']
        or not all(result[k] for k in ('flushReturned','stdinCloseReturned','sourceCloseReturned','writerReturned'))
        or result['stdinCloseError'] is not None):
        raise ValueError('ORIGINAL_RESPONSE_NOT_SUCCESSFULLY_RETURNED')
    for name in ('stdout','stderr'):
        stream=result[name]
        if stream['prefixTruncated'] or not stream['closeReturned'] or stream['error'] is not None:
            raise ValueError('ORIGINAL_RESPONSE_INCOMPLETE_'+name)
        data=bytes.fromhex(stream['prefixHex'])
        if len(data)!=stream['bytes'] or hashlib.sha256(data).hexdigest()!=stream['sha256']:
            raise ValueError('ORIGINAL_RESPONSE_LENGTH_OR_SHA_'+name)
        if name=='stdout':out=data
        elif data or stream['sha256']!=EMPTY_SHA:raise ValueError('ORIGINAL_RESPONSE_STDERR')
    return out

def parse_features(raw):
    text=raw.decode('ascii','strict')
    # No whitespace stripping or substring matching: lone CR/space/control/invalid token refuses.
    token=r'[A-Za-z0-9_]+'
    separator=r'(?:\r\n|\n|,)'
    if not re.fullmatch(token+r'(?:'+separator+r'+'+token+r')*'+separator+r'*',text):
        raise ValueError('FEATURES_TOKEN_FORMAT')
    return frozenset(re.split(separator+r'+',text.rstrip('\r\n,')))
