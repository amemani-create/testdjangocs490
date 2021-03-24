from django import forms
from posts.models import Post, TF_Post, Topics
from ckeditor.widgets import CKEditorWidget


class NewPostForm(forms.ModelForm):
    picture = forms.ImageField(required=False)
    caption = forms.CharField(widget=CKEditorWidget, required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=True)
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=False)

    class Meta:
        model = Post
        fields = ('subject', 'picture', 'caption', 'tags')


VIDEO_OR_PERSON = [('Video', 'Video'), ('In Person', 'In Person'), ('Both', 'Both')]

SCHOOL_LEVEL = [('elementary school', 'Elementary School'), ('middle school', 'Middle School'), ('high school', 'High School')]

topic_choices = Topics.objects.all().values_list('topic_name', 'topic_name')
topic_list = []
for topic in topic_choices:
    topic_list.append(topic)


class TFPostForm(forms.ModelForm):
    picture = forms.ImageField(required=False)
    caption = forms.CharField(widget=CKEditorWidget, required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=True)
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=False)
    state = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=False)
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=False)
    virtual = forms.CharField(widget=forms.Select(choices=VIDEO_OR_PERSON), required=False)
    school_level = forms.CharField(widget=forms.SelectMultiple(choices=SCHOOL_LEVEL, attrs={'class': 'input is-medium'}), required=False)
    topics = forms.CharField(widget=forms.SelectMultiple(choices=topic_list, attrs={'class': 'input is-medium'}), required=False)

    class Meta:
        model = TF_Post
        fields = ('subject', 'picture', 'caption', 'tags', 'state', 'city', 'virtual', 'school_level', 'topics')
