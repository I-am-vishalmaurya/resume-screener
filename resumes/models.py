from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class CandidateResumes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    content = models.TextField(blank=True)
    resume_date = models.DateTimeField(auto_now_add=True)


class HRJobPostings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()
    skills_required = models.TextField()
    job_location = models.CharField(max_length=100)
    job_date = models.DateTimeField(auto_now_add=True)


class AppliedJobs(models.Model):
    candidate = models.ForeignKey(CandidateResumes, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(HRJobPostings, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
