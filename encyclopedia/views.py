from django.shortcuts import render, redirect
from django import forms
import markdown2
import random
from . import util

# FORMS
#
# Create and define all the forms
#
# Form to CREATE an entry (will be the EDIT form also)
class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs=
        {'placeholder': 'Title of your entry', 'class': 'form-control', 'style' : 'width : 90%'}), required=True)
    entry = forms.CharField(widget=forms.Textarea(attrs=
        {'placeholder': 'Content (Markdown) : Start with a # Title', 'rows':20, 'class': 'form-control', 'style' : 'width : 90%'}), required=True)
#
# Form to SEARCH within entries
class SearchForm(forms.Form):
    keyword = forms.CharField(label='', required=True, widget=forms.TextInput(attrs={'placeholder': '🔎 Search Encyclopedia', 'class': 'search'}))

# INDEX PAGE
#
# Render the index page with the list of entries
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form" : SearchForm()
    })


# ENTRY PAGE
#
# Display an entry page with dynamic title, content.
# Display the error entry if the entry doesn't exist
def entry_page(request, entry_title): 
    #    
    # Fetch the entries list
    entries = util.list_entries()
    #    
    # Fetch the entry the entry if the entry title exists in the lists of entries  
    if entry_title in entries:
        entry_content = util.get_entry(entry_title)
    #    
    # If doesn't exist, Get the entries/system/ERROR page
    else :
        entry_content = util.get_error("error")
    #    
    # 1/ Stock in a var the result of converting your .md file
    # 2/ Create the content of entry page with title and converted file 
    entry_converted = markdown2.markdown(entry_content)
    content = {
        'entry_title': entry_title,
        'entry_content': entry_converted,
        'search_form' : SearchForm()
        }
    return render(request, "encyclopedia/entry.html", content)


# RANDOM PAGE
#
# Display a random 'entry_page'
def random_page(request):
    #
    # Use random to get a random entry_title in entries list
    random_entry_title = random.choice(util.list_entries())
    #
    # Redirect to 'entry_page' and attribute value for the title argument
    return redirect('entry_page', entry_title = random_entry_title)


# CREATE NEW PAGE
#
# Display the 'create' page and defining the creational function
def create_page(request):
    #
    # Verifies if the create form has been submitted/posted
    if request.method == 'POST':
        form = NewEntryForm(request.POST)
        #
        # Verifies if the posted form is valid
        if form.is_valid():
            #
            # I capture the data submitted in 2 variables. I make sur all the titles are capitalized to match my search engine insensitive to case
            title = form.cleaned_data.get('title').capitalize()
            entry = form.cleaned_data.get('entry')
            #
            # I use the save_entry function to save/create a new entry with the 2 captured variables
            # Applied additionnal styling to the content of the entry
            util.save_entry(title, entry)
            # Redirect me to the entry_page function to display the new created entry
            return redirect('entry_page', entry_title = title)
    # 
    # If the form is not submitted/posted, display the create page with its form
    else:
        content = {
            'form': NewEntryForm(),
            'search_form' : SearchForm()
            }
    return render(request, 'encyclopedia/create.html', content)



# SEARCH ENGINE
#
# Display the 'create' page and defining the creational function
def search(request): 
    #
    # If the searchbar is submitted
    if request.method == 'GET':
        #
        # Stock the data we got from the form in the variable 'k'
        k = request.GET['keyword']
        #
        # Calling the entries list
        # Fetching the entry if the keyword strictly == an entry title in the list
        entries = util.list_entries()
        #
        # s_r stands for search_results
        # The array converts 'Keyword' in lowercase and go through all the filenames (f) in entries to check if 'Keyword' is contained in any 'f'. If it does, it appends.
        s_r = [f for f in entries if k.lower() in f.lower()]
        #
        # If the length of our array is 0 (Condition not fullfilled > Nothing was appended), return an error msg on the search_page.html
        if len(s_r) == 0:
            content = {
                'search_form': SearchForm,
                'error' : 'Sorry, no result found 😿'
                }
            return render(request, 'encyclopedia/search_results.html', content)
        #
        # If I only have 1 result in array and my keyword matches this result (in all the letter cases), render the corresponding entry_page
        elif len(s_r) == 1 and k == s_r[0].lower() or k == s_r[0].upper() or k == s_r[0].capitalize():
            return redirect('entry_page', entry_title = s_r[0])
        #
        # If search result contains more than 1 result, render the search_results html page with the list of matching entries (containing a partial string)
        else:
            content = {
                    'search_form': SearchForm,
                    'entries' : s_r
                            }
            return render(request, 'encyclopedia/search_results.html', content)

# EDIT ENGINE
#
# Display the 'edit' page
def edit(request, entry_title):
    #
    # Fetch the current title
    current_title = entry_title
    #
    # When the edit form is not submitted yet, we want to render the form
    if request.method == "GET":
        #
        # Get the current content thanks to the fetched title
        content = util.get_entry(current_title)
        #
        # Fetch the edit form (it's actually the 'create' form but with the current data and render in the edit page
        edit_form = NewEntryForm({"title": current_title, "entry": content})
        return render(request, "encyclopedia/edit.html",
            {"edit_form": edit_form, 
            "entry_title": entry_title})
    #
    # The edit form has been submitted
    edited_form = NewEntryForm(request.POST)
    if edited_form.is_valid():
        #
        # If valid, the previously current title becomes old
        old_title = current_title
        #
        # We keep the new posted informations in new title and content
        new_title = edited_form.cleaned_data.get("title")
        new_content = edited_form.cleaned_data.get("entry")
        #
        # If the title of the entry has NOT been changed, save_entry can manage the change
        if old_title == new_title:
            util.save_entry(new_title, new_content)
        # If the title of the entry has changed, save_entry just creates another entry.
        # So first I save the new entry, then I delete the old one.
        else :
            util.save_entry(new_title, new_content)
            util.delete_entry(old_title)
        #
        # Render with brand new changes
        return redirect("entry_page", entry_title=new_title)

