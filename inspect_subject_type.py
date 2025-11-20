from moviebox_api import SubjectType
with open('subject_type_result.txt', 'w') as f:
    f.write("SubjectType members:\n")
    for member in SubjectType:
        f.write(f"{member.name}: {member.value}\n")
    f.write(f"Dir: {dir(SubjectType)}\n")
