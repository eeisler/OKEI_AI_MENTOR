from django.contrib import admin

from .models import Department, Specialty, Group, Dialog, SkillMatrix, StudentProgress, User

admin.site.register(Department)
admin.site.register(Specialty)
admin.site.register(Group)
admin.site.register(Dialog)
admin.site.register(SkillMatrix)
admin.site.register(StudentProgress)
admin.site.register(User)
