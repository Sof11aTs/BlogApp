from django.contrib import admin
from .models import BlogEntry, Categorys, Comments


@admin.register(Categorys)
class CategorysAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    readonly_fields = ["created_at"]
    search_fields = ["title",]
    list_filter = ["created_at",]

@admin.register(BlogEntry)
class BlogEntryAdmin(admin.ModelAdmin):
    list_display = ["view_id", "title", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["title", "id"]
    list_filter = ["created_at", "updated_at"]

    @admin.display(description="Entry id")
    def view_id(self, obj):
        return f"Entry obj {obj.id}"
    
# @admin.register(Comments)
# class CommentsAdmin(admin.ModelAdmin):
#     list_display = ["content", "created_at", "updated_at"]

