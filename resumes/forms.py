from django import forms
from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.models import User


class UploadCandidateResume(forms.Form):
    """
    Form for uploading candidate resume
    """
    resume = forms.FileField(label='Resume')

    def clean_resume(self):
        """
        Validate that the resume is a valid file
        :return:
        """
        resume = self.cleaned_data['resume']
        if resume.name.split('.')[-1] not in settings.ALLOWED_EXTENSIONS:
            raise ValidationError('File type not allowed')
        return resume


class AddJobPosting(forms.Form):
    """
    Only Admins can post job
    """
    title = forms.CharField(label='Job Title', max_length=100)
    description = forms.CharField(label='Job Description', max_length=1000)
    location = forms.CharField(label='Location', max_length=100)
    skills = forms.CharField(label='Skills', max_length=100)

    def clean_inputs(self):
        """
        clean data
        :return:
        """
        title = self.cleaned_data['title']
        description = self.cleaned_data['description']
        location = self.cleaned_data['location']
        skills = self.cleaned_data['skills']
        return title, description, location, skills

