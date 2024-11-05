import re


def notes_to_dict(notes):
    def get_categories_and_scope(user_selected_text):
        items, scope = user_selected_text.split("Outcome: ")
        scope = re.sub(r"\s+|\n", "", scope)
        categories = []
        for category in items.split("\n\n"):
            if ": " in category:
                category = category.split(": ")[1]
            categories.append(category)
        return filter(None, categories), scope

    ret = {"user problem": "", "categories": [], "scope": ""}
    if not notes:
        return ret

    contains_user_selected = "User selected:\n" in notes
    contains_user_problem = "User problem:\n" in notes
    contains_public_diagnosis_note = "Public Diagnosis note:\n" in notes

    new_notes = notes
    if contains_public_diagnosis_note:
        new_notes = re.sub("Public Diagnosis note:\n.*\n\n", "", notes)

    if contains_user_selected:
        parts = filter(None, new_notes.split("User selected:\nWhat do you need help with?: "))
        if contains_user_problem:
            ret["categories"], ret["scope"] = get_categories_and_scope(parts[1])
            ret["user problem"] = parts[0].split("User problem:\n")[1]
        else:
            ret["categories"], ret["scope"] = get_categories_and_scope(parts[0])
    elif contains_user_problem:
        ret["user problem"] = filter(None, new_notes.split("User problem:\n"))[0]

    return ret


def test_user_problem():
    user_problem = """User problem:
Data 5678

User selected:
What do you need help with?: Discrimination

Where did the discrimination happen?: Work - including colleagues, employer or employment agency

Why were you treated differently?: Disability, health condition, mental health condition

Outcome: abc"""

    notes_to_dict(user_problem)
