from django.contrib import admin
from .models import CommunityPost, Comment
from django.utils.html import format_html

# Inline for Comments
class CommentInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Comment
    extra = 1  # Number of empty comment forms to show
    readonly_fields = ('created_at', 'updated_at')
    fields = ('author', 'content', 'created_at', 'updated_at')
    
    def has_add_permission(self, request, obj=None):
        # Only allow adding comments if the post exists
        return obj is not None

class CommunityPostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]  # Add comments inline
    list_display = ('title', 'author', 'created_at', 'image_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'content_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

admin.site.register(CommunityPost, CommunityPostAdmin)
admin.site.register(Comment, CommentAdmin)