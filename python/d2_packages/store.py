from .models import Note

note_list = []

def note_append(note: Note):
    note_list.append(note)
    
def find_note(id):
    for i in note_list:
        if i.id == id:
            return i
    print("No note exist with that id")

    

