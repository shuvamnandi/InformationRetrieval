from django.core.urlresolvers import reverse
from solrq import Q
import pysolr, json
from django.shortcuts import redirect,render
from django.http import HttpResponse, HttpResponseRedirect
from SearchEngine.Crawl.crawl import Crawl
from .forms import CrawlForm, SearchForm, SpellForm
from SearchEngine import search_index

query_keyword=''
searchType='smartSearch'



def index(request):
    return render(request, 'SearchEngine/home.html')


def search(request):
    return render(request, 'SearchEngine/search.html')


# TODO -- This view must process the form and send data to crawl function,
# TODO -- get crawled information and return a template to display the crawled info
def get_crawl_keyword(request):
    if request.method == 'POST':
        form = CrawlForm(request.POST)
        print "form:", form
        print "valid:", form.is_valid()
        if form.is_valid():
            if form.cleaned_data['query']:
                form_data = form.cleaned_data
                query_keyword = form_data['query']
                print "Keyword: ", query_keyword
                query_keyword = query_keyword.replace(" ", "%20")
                query_keyword = query_keyword.replace("&", "%26")
                query_keyword = query_keyword.replace("|", "%7C")
                crawl = Crawl()
                print "Crawling by query:", query_keyword
                crawl.crawl_dynamic([], query_keyword)
                return HttpResponseRedirect('/thanks')
    else:
        form = CrawlForm()
    return render(request, 'SearchEngine/crawl.html', {'form':form})


def thanks(request):
    return HttpResponse(content="Thanks for submitting your query. Crawling in progress")

def get_search_keyword(request):
    print "Entered get_search_keyword"
    if request.method == 'POST':
        form = SearchForm(request.POST)
       # print "form:", form
        print "valid:", form.is_valid()
        if form.is_valid():
            if form.cleaned_data['searchquery']:
                form_data = form.cleaned_data
                global query_keyword
                global searchType
                query_keyword= form_data['searchquery']
                print "Keyword: ", query_keyword
                print "Searching by query:", query_keyword
                if 'quickSearch' in request.POST:
                    searchType = 'quickSearch'
                    #return send_search(request,query_keyword,'quickSearch')
                elif 'smartSearch' in request.POST:
                    searchType = 'smartSearch'
                return send_search(request)
                    #return send_search(request,query_keyword, 'smartSearch')
    else:
        form = SearchForm()
    return render(request, 'SearchEngine/home.html', {'form':form})

def send_search(request): #def send_search(request, query, searchType):
    print "Entered send search"
    global query_keyword
    if request.method == 'GET':
        query_keyword = request.GET.get('query')
    query = query_keyword
    print "Query_keyword", query
    print "Search Type", searchType
    spellq = ''
    results = ''
    num_results = 0
    # Setup a Solr instance. The timeout is optional.
    if searchType=='quickSearch':
        (num_results, results, suggestions) = search_index.quick_search(query)
    elif searchType=='smartSearch':
        (num_results, results, suggestions) = search_index.smart_search(query)

    print "Came back from searching"
    resultlist=[]
    # Just loop over it to access the results.
    for result in results:
        resultlist.append(result)
        print("The result is '{}'.".format(result))
        print "Came back from printing"
        #print("The address is '{}'.".format(result["address"][0].encode("ascii")))
    return render(request, 'SearchEngine/search.html',{'query':query,'resultlist':resultlist, 'numResults': num_results, 'suggestions':suggestions})


  #   print "Entered request_page"
  #   spellq=''
  #   if request.method == 'POST':
  #       form = SpellForm(request.POST)
  #      # print "form:", form
  #       print "valid:", form.is_valid()
  #       if form.is_valid():
  #           if form.cleaned_data['spellquery']:
  #               form_data = form.cleaned_data
  #               spellq = form_data['spellquery']
  #               print "SpellKeyword: ", spellq
  #               return send_search(request, spellq, 'smartSearch')
  #   else:
  #       form = SpellForm()
  #   return render(request, 'SearchEngine/search.html', {'form': form})
  # # print "Entered request_page"
  # # if(request.GET.get('link')):
  # #   print (str(request.GET.get('link')))
  # #   print (request.GET.get('link'))
  # #   send_search(request, str(request.GET.get('link')),'smartSearch')
