from django.db.models import Q
from lars.forms import SearchForm
from datetime import datetime

def searchQuerySet(queryset, tag, user, fulltext, date, sort, order):
    if fulltext:
        queryset = queryset.filter(Q(text__icontains=fulltext)|Q(title__icontains=fulltext))
    if tag:
        try:
            queryset = queryset.filter(tag__id=int(tag))
        except ValueError:
            tags = [t.rstrip().lstrip() for t in tag.split(',') if t.rstrip().lstrip()]
            queryset = queryset.filter(tags__text__in=tags)
        except Exception: #perhaps it's worth noting if it fails for another reason
            pass
    if user:
        try:
            queryset = queryset.filter(creator__id=int(user))
        except ValueError:
            users = user.split()
            queryset = queryset.filter(creator__username__in=users)
        except Exception:
            pass
    if date:
        pass #this shit'll be hard
    queryset = queryset.order_by("%s%s" % ({SearchForm.ASC_CHOICE:'', SearchForm.DESC_CHOICE:'-'}[order], sort))
    return queryset