# coding:utf-8

from django.shortcuts import render


def index_unlog(request):
    return render(request, 'index_unlog.html')
