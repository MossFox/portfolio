from django.shortcuts import render, redirect
from . import util
from django.conf import settings
import os
import random
import markdown2

def checklist(request):
    return render(request, "encyclopedia/checklist.html")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries() #calls the util.py function list_entries
    })

def fix_name(name): # this function checks for lowercase entry of name and if so, returns the upper case version of it
    if name.lower() == "css":
        return "CSS"
    elif name.lower() == "html":
        return "HTML"
    return name

def entry(request, name): # this function takes the value name passed down from urls.py as a str:name
    name = fix_name(name) #checks for lowercase
    entry_content = util.get_entry(name) # gets the entry content using util.py function
    if entry_content is None: # if the variable is empty
        return render(request, "encyclopedia/error.html", {
            "message": "Entry not found." #renders an error page and message
        })
    html_content = markdown2.markdown(entry_content) # converts the entry markdown content into html friendly contetn
    return render(request, "encyclopedia/entry.html", {
        "content": html_content,  # passes html friendly markdown content as "content"
        "title": name # passesthe title of the entry
    })


def search(request): #search function
    query = request.GET.get("search_request") # gets the search input
    match = util.get_entry(query) # matches it to an entry based on the input
    if match: # if there is a match / function finds the entry
        html_content = markdown2.markdown(match) # converts the content to html and renders the page
        return render(request, "encyclopedia/entry.html", {
            "content": html_content,
            "title": query
        })
    else: # if there isn't a match
        entries = util.list_entries() # gets a list of available entries
        filtered_entries = [entry for entry in entries if query.lower() in entry.lower()] # filters them based on the substring parameters
        return render(request, "encyclopedia/search_results.html", { # displays the page with suggestions
            "entries": filtered_entries
        })

def new_entry(request): # function to create a new entry
    if request.method == "POST": # if the page content is posted / aka info submitted
        title = request.POST["title"] # gets the title input
        content = request.POST["content"] # gets the content input
        file_path = os.path.join(settings.BASE_DIR, "entries", f"{title}.md") # constructs a file path by joining the base directory of your project (settings.BASE_DIR), the "entries" directory, and a filename that includes the title variable with a .md extension.
        entry_check = util.get_entry(title) # checks if the entry already exists
        if entry_check == None: # if not
            with open(file_path, "w") as file: # creates the file at file_path in write mode.
                file.write(f"# {title}\n\n{content}") # writes a string to the file, which includes the title as a Markdown header and the content as the body.
            return redirect("entry", name=title) # redirects into that new entry page
        else: # if entry already exists gives the error
            return render(request, "encyclopedia/error.html", {
            "message": "Entry already exists."
        })
    else: # if the pages content is requested, just loads the html page
        return render(request, "encyclopedia/new_entry.html")

def edit(request): # entry editting function
    title = request.GET.get('title') # gets the page title
    content = util.get_entry(title) # gets the content of the entry based on the title
    if request.method == "GET":
        if content.startswith(f"# {title}\n"): # if the contetn starts with # title:
            content = content[len(f"# {title}\n"):] # content[start:end] performs the slicing of the length of #{title}
        return render(request, "encyclopedia/edit.html", { # loads the page with this context
            "title": title,
            "content": content,
            'entry': title
        })
    if request.method == "POST": # if something is posted to the page
        old_title = request.POST.get('entry') # gets the old title of the entry
        new_title = request.POST.get('title') # gets the new input title
        new_content = request.POST.get('content') # gets the new content of the entry
        if request.POST.get("action") == "edit": # if the edit action is executed
            if new_title == old_title: # compares the titles
                if not new_content.startswith(f"# {new_title}\n"): # if new content doesn't start with this
                    full_content = f"# {new_title}\n{new_content}" # adds the #
                else:
                    full_content = new_content # otherwise saves it as is
                util.save_entry(new_title, full_content) # calls the save entry function
                return redirect('entry', name=new_title)
            else:
                os.remove(f"entries/{old_title}.md") # if the titles are different, removes the old entry file
                full_content = f"# {new_title}\n{new_content}" #gets the content
                util.save_entry(new_title, full_content) # saves a new file
                return redirect('entry', name=new_title)
        if request.POST.get("action") == "delete": # if the action called is delete
            os.remove(f"entries/{old_title}.md") # deletes the old_title entry
            return redirect('index')

def rand (request): # calls the random function
    entries = util.list_entries() # gets the list of entries
    n = len(entries) # gets the length of the list
    number = random.randint(0, n-1) #
    entry = entries[number]
    html_content = markdown2.markdown(util.get_entry(entry))


    return render (request, "encyclopedia/entry.html", {
        "title": entry,
        "content": html_content
    })



