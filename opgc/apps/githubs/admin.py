from django.contrib import admin

from apps.githubs.models import GithubUser, Repository, UserOrganization, Organization, UserLanguage, Language


class GithubUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'updated', 'username', 'name', 'total_score')
    list_display_links = ('id', )
    readonly_fields = ('id', 'created', 'updated')
    fields = ('id', 'created', 'updated', 'username', 'name', 'email', 'location', 'avatar_url',
              'total_contribution', 'total_stargazers_count', 'tier', 'user_rank', 'company',
              'bio', 'blog', 'public_repos', 'followers', 'following', 'status', 'continuous_commit_day', 'total_score')
    list_per_page = 15


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')
    list_display_links = ('id', )
    readonly_fields = ('id',)
    fields = ('id', 'type',)
    list_per_page = 15


class UserLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'github_user', 'language', 'number')
    list_display_links = ('id', )
    readonly_fields = ('id',)
    fields = ('id', 'github_user', 'language', 'number')
    raw_id_fields = ('github_user', 'language')
    list_per_page = 15


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('id', )
    readonly_fields = ('id',)
    fields = ('id', 'name', 'description')
    list_per_page = 15


class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'github_user', 'organization',)
    list_display_links = ('id', )
    readonly_fields = ('id',)
    fields = ('id', 'github_user', 'organization',)
    raw_id_fields = ('github_user', 'organization')
    list_per_page = 15


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'github_user', 'contribution', 'stargazers_count', 'name')
    list_display_links = ('id', )
    readonly_fields = ('id',)
    fields = ('id', 'github_user', 'contribution', 'stargazers_count', 'name', 'full_name',
              'owner', 'organization', 'rep_language', 'languages')
    raw_id_fields = ('github_user',)
    list_per_page = 15


admin.site.register(GithubUser, GithubUserAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(UserLanguage, UserLanguageAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(Repository, RepositoryAdmin)

