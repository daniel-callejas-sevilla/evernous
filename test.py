#!/usr/bin/env python

from evernote.api.client import EvernoteClient, NoteStore
from evernote.edam.error.ttypes import EDAMUserException

dev_tokens = {
  'cuenta1': '',
  'cuenta2': '',
}
for d in dev_tokens:
  with open("{}.devtoken.txt".format(d)) as f:
    dev_tokens[d] = f.read()
    
print(dev_tokens)

nbs = { # Notebooks
  'source': '51eb610e-d0c3-4e40-9bf4-140867404730',
  'target': 'e56fa2dc-9439-4e15-9089-44a44b87afa4',
}
client_a = EvernoteClient(token=dev_tokens['cuenta1'])
client_b = EvernoteClient(token=dev_tokens['cuenta2'])


print("Fetching notes from source notebook, with tags")
store_a = client_a.get_note_store()
source_tags = {}
for n in store_a.listNotebooks():
  if n.guid == nbs['source']:
    print(n.name, n.guid)
    filter = NoteStore.NoteFilter()
    filter.notebookGuid = n.guid
    rspec = NoteStore.NotesMetadataResultSpec()
    rspec.includeTitle = True
    rspec.includeAttributes = True
    rspec.includeTagGuids = True
    print("Getting notes")
    results = store_a.findNotesMetadata(filter, 0, 250, rspec)
    
    print("Found {} notes".format(results.totalNotes))
    found_tag_guids = {} # TODO: Use a set
    for note in results.notes:
      print("Note: {}".format(note.title))
      print("Guid: {}".format(note.guid))
      print("Tags: {}".format(note.tagGuids))
      print("---")
      for t in note.tagGuids:
        found_tag_guids[t] = True

    for g in found_tag_guids.keys():
      tag = store_a.getTag(g)
      source_tags[g] = tag
      print(tag)


print("Creando notas iguales en cuenta2, con sus etiquetas")
store_b = client_b.get_note_store()
for guid in source_tags:
  tag = source_tags[guid]
  tag.updateSequenceNum = None
  tag.guid = None  # Will be different in target account
  tag.parentGuid = None # By design, we want to avoid replicating hierarchy
  print("Creating tag {} in target notebook".format(tag.name))
  try:
    store_b.createTag(tag)
    print("...created ok!")
  except EDAMUserException, e:
    if e.errorCode == 10 and e.parameter == 'Tag.name':
      print("...failed, it already exists".format(tag.name))
      pass
      

  
  