from .store import note_append,Note

def create_note(id,body):
    note = Note(id,body)
    note_append(note)
    return note


    