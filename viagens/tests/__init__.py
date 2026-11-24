# Patch de compatibilidade entre Python 3.14 e Django 5.1 (copy do BaseContext nos testes)
import copy
from django.template import context as django_context

def _safe_basecontext_copy(self):
    duplicate = object.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    return duplicate

def _safe_context_copy(self):
    duplicate = _safe_basecontext_copy(self)
    duplicate.render_context = copy.copy(self.render_context)
    return duplicate

django_context.BaseContext.__copy__ = _safe_basecontext_copy
django_context.Context.__copy__ = _safe_context_copy
